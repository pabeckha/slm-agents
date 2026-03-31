"""Constrained decoding engine for guided LLM token generation."""

import json
import re

import numpy as np

# ── Regex patterns for number validation ────────────────────────────────────
# Valid partial number (still being constructed): "", "-", "1", "1.", "-1.5"
_PARTIAL_NUM_RE = re.compile(r'^-?(\d+(\.\d*)?)?$')
# Valid complete number: must have at least one digit
_COMPLETE_NUM_RE = re.compile(r'^-?\d+(\.\d+)?$')
# Partial / complete integer
_PARTIAL_INT_RE = re.compile(r'^-?\d*$')
_COMPLETE_INT_RE = re.compile(r'^-?\d+$')


# ── BPE byte-level decoding ─────────────────────────────────────────────────

def _build_unicode_to_byte() -> dict[str, int]:
    """Build the reverse of GPT-2's bytes_to_unicode mapping.

    Qwen2/Qwen3 vocab.json stores token strings using GPT-2's byte-level BPE
    encoding (e.g. Ġ = U+0120 represents a space).  This mapping converts
    those Unicode stand-ins back to raw byte values so tokens can be decoded
    to UTF-8 text.

    Returns:
        A mapping from Unicode character to its corresponding byte value.
    """
    printable: list[int] = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    encoded = list(printable)
    extra = 0
    for byte in range(256):
        if byte not in printable:
            printable.append(byte)
            encoded.append(256 + extra)
            extra += 1
    return {chr(enc): byte for byte, enc in zip(printable, encoded)}


_UNICODE_TO_BYTE: dict[str, int] = _build_unicode_to_byte()


def _decode_bpe_token(bpe_str: str) -> str:
    """Decode a BPE-encoded vocabulary token to a UTF-8 string.

    Args:
        bpe_str: The token string as stored in vocab.json (e.g. ``"Ġfn"``).

    Returns:
        The actual UTF-8 text the token represents (e.g. ``" fn"``).
    """
    try:
        return bytes(
            [_UNICODE_TO_BYTE[ch] for ch in bpe_str]
        ).decode("utf-8", errors="replace")
    except KeyError:
        return bpe_str


# ── Public helper ────────────────────────────────────────────────────────────

def encode_prompt(model: object, text: str) -> list[int]:
    """Encode *text* to a flat list of token IDs.

    The SDK's ``encode()`` returns a 2-D ``torch.Tensor`` of shape
    ``[1, seq_len]``.  This helper squeezes and converts it so the rest of
    the codebase can work with plain ``list[int]`` values.

    Args:
        model: A :class:`llm_sdk.Small_LLM_Model` instance.
        text: The prompt string to encode.

    Returns:
        A flat list of integer token IDs.
    """
    tensor = model.encode(text)  # type: ignore[attr-defined]
    result: list[int] = tensor.squeeze().tolist()
    return result


# ── Constrained decoder ──────────────────────────────────────────────────────

class ConstrainedDecoder:
    """Token-by-token decoder that restricts generation to valid outputs.

    At each step the decoder:
    1. Calls the LLM to obtain logits over the full vocabulary.
    2. Masks all tokens that would violate the current constraint to ``-inf``.
    3. Picks the ``argmax`` among valid tokens.

    Args:
        model: A loaded :class:`llm_sdk.Small_LLM_Model` instance.
    """

    def __init__(self, model: object) -> None:
        self._model = model

        # Load vocabulary and decode BPE token strings to real text
        vocab_path: str = model.get_path_to_vocabulary_json()  # type: ignore[attr-defined]  # noqa: E501
        with open(vocab_path, encoding="utf-8") as fh:
            raw_vocab: dict[str, int] = json.load(fh)

        self._id_to_str: dict[int, str] = {
            token_id: _decode_bpe_token(bpe_str)
            for bpe_str, token_id in raw_vocab.items()
        }

    # ── Low-level helpers ────────────────────────────────────────────────────

    def _logits(self, input_ids: list[int]) -> np.ndarray:
        """Return next-token logits as a NumPy array.

        Args:
            input_ids: Current sequence of token IDs.

        Returns:
            1-D float64 array of length ``vocab_size``.
        """
        get = self._model.get_logits_from_input_ids  # type: ignore[attr-defined]  # noqa: E501
        raw = get(input_ids)
        return np.array(raw, dtype=np.float64)

    def _is_partial_number(self, s: str, is_int: bool) -> bool:
        """Return True if *s* is a valid prefix of a number.

        Args:
            s: Accumulated string so far.
            is_int: When True, only integer prefixes are accepted.

        Returns:
            Whether *s* could still become a valid number.
        """
        if is_int:
            return bool(_PARTIAL_INT_RE.fullmatch(s))
        return bool(_PARTIAL_NUM_RE.fullmatch(s))

    def _is_complete_number(self, s: str, is_int: bool) -> bool:
        """Return True if *s* is already a valid complete number.

        Args:
            s: Accumulated string.
            is_int: When True, require an integer (no decimal point).

        Returns:
            Whether *s* is a syntactically valid number.
        """
        if is_int:
            return bool(_COMPLETE_INT_RE.fullmatch(s))
        return bool(_COMPLETE_NUM_RE.fullmatch(s))

    # ── Generation primitives ────────────────────────────────────────────────

    def generate_from_choices(
        self, prompt_ids: list[int], choices: list[str]
    ) -> str:
        """Generate a token sequence constrained to one of the given choices.

        At each step only tokens whose decoded string keeps the accumulated
        output a valid prefix of at least one choice are allowed.  Generation
        stops as soon as the accumulated text (after stripping any leading
        whitespace added by the tokenizer) exactly matches a choice.

        Args:
            prompt_ids: Token IDs of the full prompt so far.
            choices: The set of exact strings the model may produce.

        Returns:
            The matched choice string, or ``choices[0]`` as a fallback.
        """
        if not choices:
            return ""

        current_ids: list[int] = list(prompt_ids)
        current_str = ""

        for _ in range(200):
            logits = self._logits(current_ids)
            mask = np.full(len(logits), -np.inf)

            for token_id, token_str in self._id_to_str.items():
                # Strip leading whitespace: the tokenizer may attach the
                # space that precedes the first word to that word's token.
                candidate = (current_str + token_str).lstrip()
                if any(choice.startswith(candidate) for choice in choices):
                    if 0 <= token_id < len(mask):
                        mask[token_id] = logits[token_id]

            if np.all(np.isinf(mask)):
                break

            next_id = int(np.argmax(mask))
            current_str += self._id_to_str.get(next_id, "")
            current_ids.append(next_id)

        clean = current_str.lstrip()
        if clean in choices:
            return clean
        for choice in choices:
            if choice.startswith(clean):
                return choice
        return choices[0]

    def generate_number(
        self, prompt_ids: list[int], is_int: bool = False
    ) -> str:
        """Generate a valid number (integer or float).

        Only tokens that keep the accumulated buffer a valid *partial* number
        are allowed.  Generation stops when the model's unconstrained best
        token would not extend the number (i.e. it naturally wants to move
        on), provided the buffer is already a complete number.

        Args:
            prompt_ids: Token IDs of the full prompt so far.
            is_int: When True, restrict to integers (no decimal point).

        Returns:
            The generated number as a string, or ``"0"`` / ``"0.0"`` on
            failure.
        """
        current_ids: list[int] = list(prompt_ids)
        current_str = ""

        for _ in range(30):
            logits = self._logits(current_ids)
            clean = current_str.lstrip()

            # Stop early if we have a complete number and the model naturally
            # wants to produce something that isn't a numeric extension.
            if self._is_complete_number(clean, is_int):
                best_id = int(np.argmax(logits))
                best_str = self._id_to_str.get(best_id, "")
                extended = (clean + best_str).lstrip()
                if not self._is_partial_number(extended, is_int):
                    break

            mask = np.full(len(logits), -np.inf)
            for token_id, token_str in self._id_to_str.items():
                candidate = (current_str + token_str).lstrip()
                if self._is_partial_number(candidate, is_int):
                    if 0 <= token_id < len(mask):
                        mask[token_id] = logits[token_id]

            if np.all(np.isinf(mask)):
                break

            next_id = int(np.argmax(mask))
            current_str += self._id_to_str.get(next_id, "")
            current_ids.append(next_id)

        clean = current_str.lstrip()
        if not self._is_complete_number(clean, is_int):
            return "0" if is_int else "0.0"
        return clean

    def generate_string(self, prompt_ids: list[int]) -> str:
        """Generate a string value, stopping at a closing quote.

        The prompt should end with an opening ``"`` so the model generates
        the string content.  This method produces tokens freely (no masking)
        and stops as soon as a token containing ``"`` is emitted, returning
        everything generated before that quote.

        Args:
            prompt_ids: Token IDs of the full prompt (including opening ``"``).

        Returns:
            The string value without surrounding quotes.
        """
        current_ids: list[int] = list(prompt_ids)
        generated = ""

        for _ in range(200):
            logits = self._logits(current_ids)
            next_id = int(np.argmax(logits))
            token_str = self._id_to_str.get(next_id, "")

            if '"' in token_str:
                generated += token_str[: token_str.index('"')]
                break

            if not token_str or "\n" in token_str:
                break

            generated += token_str
            current_ids.append(next_id)

        return generated

    def generate_bool(self, prompt_ids: list[int]) -> str:
        """Generate ``"true"`` or ``"false"``.

        Delegates to :meth:`generate_from_choices` with the two boolean
        literals as the only valid choices.

        Args:
            prompt_ids: Token IDs of the full prompt so far.

        Returns:
            Either ``"true"`` or ``"false"``.
        """
        return self.generate_from_choices(prompt_ids, ["true", "false"])
