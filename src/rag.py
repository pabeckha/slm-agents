"""RAG pipeline for tool schema retrieval.

Builds a FAISS index over function schemas and retrieves top-k candidates
for a given user query.  Used by Config CD+Q+RAG to simulate realistic
tool selection from a large catalog.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .schema import FunctionDef


def _function_text(func: FunctionDef) -> str:
    """Build a text representation of a function for embedding.

    Combines name, description, and parameter signature into a single
    string that captures the function's semantics.
    """
    params = ", ".join(
        f"{name}: {param.type}" for name, param in func.parameters.items()
    )
    sig = f"{func.name}({params})"
    return f"{sig} — {func.description}"


def build_corpus(test_data: list[dict]) -> list[FunctionDef]:
    """Deduplicate all functions from BFCL test data by name.

    Args:
        test_data: List of dicts with a ``functions`` key (list[FunctionDef]).

    Returns:
        Deduplicated list of FunctionDef, one per unique function name.
    """
    seen: dict[str, FunctionDef] = {}
    for entry in test_data:
        for func in entry["functions"]:
            if func.name not in seen:
                seen[func.name] = func
    return list(seen.values())


class FunctionIndex:
    """FAISS-based vector index over function definitions."""

    def __init__(
        self,
        corpus: list[FunctionDef],
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self._corpus = corpus
        self._model_name = model_name
        self._index = None
        self._embedder = None

    def _get_embedder(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(self._model_name, device="cpu")
        return self._embedder

    def build(self) -> None:
        """Embed all functions and build the FAISS index."""
        import faiss

        embedder = self._get_embedder()
        texts = [_function_text(func) for func in self._corpus]
        embeddings = embedder.encode(texts, normalize_embeddings=True)
        embeddings = np.asarray(embeddings, dtype=np.float32)

        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)  # inner product on L2-normed = cosine
        self._index.add(embeddings)

    def save(self, path: Path) -> None:
        """Save FAISS index and corpus metadata to disk."""
        import faiss

        path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(path / "index.faiss"))

        meta = [
            {"name": f.name, "text": _function_text(f)}
            for f in self._corpus
        ]
        with open(path / "corpus.json", "w") as fh:
            json.dump(meta, fh)

    @classmethod
    def load(cls, path: Path, corpus: list[FunctionDef], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> "FunctionIndex":
        """Load a previously saved index from disk."""
        import faiss

        idx = cls(corpus, model_name)
        idx._index = faiss.read_index(str(path / "index.faiss"))
        return idx

    def retrieve(
        self, query: str, top_k: int = 5,
    ) -> list[tuple[FunctionDef, float]]:
        """Retrieve the top-k most relevant functions for a query.

        Args:
            query: The user's natural-language request.
            top_k: Number of candidates to return.

        Returns:
            List of (FunctionDef, score) tuples, sorted by descending score.
        """
        embedder = self._get_embedder()
        q_emb = embedder.encode([query], normalize_embeddings=True)
        q_emb = np.asarray(q_emb, dtype=np.float32)

        k = min(top_k, len(self._corpus))
        scores, indices = self._index.search(q_emb, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append((self._corpus[idx], float(score)))
        return results


def retrieve_functions(
    index: FunctionIndex,
    query: str,
    top_k: int = 5,
) -> list[FunctionDef]:
    """Retrieve top-k function definitions for a query.

    Convenience wrapper that returns just the FunctionDef list.
    """
    results = index.retrieve(query, top_k=top_k)
    return [func for func, _score in results]


def recall_at_k(
    retrieved: list[FunctionDef],
    ground_truth: list[FunctionDef],
) -> bool:
    """Check if any ground-truth function appears in the retrieved set."""
    retrieved_names = {f.name for f in retrieved}
    return any(f.name in retrieved_names for f in ground_truth)
