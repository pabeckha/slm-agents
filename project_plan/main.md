# Project Plan - Agents with Small Language Models

**Paulo Ricardo Beckhauser de Araujo - s242779**

## Motivation

Recent progress in agentic systems has primarily resulted from the
development of increasingly large language models, whose scale facilitates
intricate reasoning, tool usage, and structured interactions.
However, reliance on large models poses major challenges, including elevated
computing costs, elevated latency, greater deployment complexity, and
restricted accessibility in resource-constrained settings.
This situation motivates an investigation into whether current agent
capabilities are inherently tied to model scale, or whether comparable
reliability and functionality can be achieved through enhanced system design
using smaller language models [@Zhang2025The] and [@Belcák2025Small].

This thesis is motivated by the hypothesis that many shortcomings observed in
agentic systems, including unreliable function calls, malformed structured
outputs, and nondeterministic behavior, emerge primarily from insufficient
constraints during generation rather than from model size.
Constrained decoding and structural enforcement techniques deliver an
effective alternative, enabling smaller language models to generate outputs
that strictly adhere to fixed schemas and execution plans [@Beurer-Kellner2024Guiding].
Guiding generation through formal constraints may enable predictable,
production-ready agent behavior without reliance on ever-larger models.

This research aims to determine whether techniques currently employed in
large-model agentic systems can be effectively replicated using small
language models when supported by constrained decoding.
Demonstrating this capability would help decouple agent reliability from
model scale, thereby enabling the development of lightweight, cost-efficient,
and locally deployable agents suitable for enterprise, embedded, and
privacy-sensitive applications.

Ultimately, this research seeks to contribute to a shift in focus from
scaling models to improving system-level reliability, demonstrating that
dependable agentic systems can be built through structural and algorithmic
improvements rather than computational scale alone.

## Background

TALK ABOUT AGENTS with LLMs

## Research Question

Can reliable agentic behavior, particularly in function calling and structured
output generation, be achieved using small language models when constrained
decoding techniques are applied, thereby reducing dependence on large-scale
models for production-grade agent systems?

This research is based on the assumption that many reliability issues in
current agentic systems arise not only from limited model capability but also
from unconstrained generation processes that permit outputs to deviate from
expected structures.
The central hypothesis is that enforcing structural constraints during
decoding enables small language models to achieve levels of correctness,
determinism, and robustness comparable to those of larger models in agent
scenarios requiring precise tool invocation and structured responses.

Addressing this question provides new insight into whether advances in
agentic AI primarily depend on model scale or on improvements in generation
control and system design.
Demonstrating that constrained decoding can enable dependable agent behavior
in small models would support the development of more efficient,
cost-effective, and deployable AI systems, particularly in environments with
limited computational resources or where local deployment is necessary.

## Time Plan

The main phases of this thesis are outlined below. An overview of the
timetable associated with these phases is provided in Figure 1.

![Gantt chart of the project plan.](time_plan.png)

Several risks may impact the project timeline. The literature review phase could
extend beyond initial estimates if relevant prior work is broader or more
fragmented than anticipated, potentially delaying subsequent design decisions.
Model development and system setup may encounter technical challenges related
to framework compatibility, hardware limitations, or unforeseen implementation
complexity.

During the experimental phases, delays may arise from unstable model behavior,
longer-than-expected training or inference times, or the need to repeat
experiments to ensure statistical validity. Exploring alternative efficiency
techniques, such as knowledge distillation or model compression, carries the
risk of limited performance gains or increased engineering overhead, which may
reduce the depth of analysis achievable within the allocated timeframe. To
mitigate these risks, the project prioritizes constrained decoding as the core
contribution and maintains flexibility in the scope of complementary techniques.

Finally, report writing may be affected by delays in earlier phases. To address
this, writing is scheduled to overlap with experimentation to ensure steady
progress toward the final submission.

## References

\nocite{*}
\bibliographystyle{unsrt}
\bibliography{bibliography}
