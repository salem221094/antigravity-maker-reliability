# Agent-Zero Reliability Framework

Implementation of the **Agent-Zero** framework for zero-error execution of long-horizon tasks, based on the **MAKER (Massively decomposed AgenT KERnel)** research paper [Solving a Million-Step LLM Task with Zero Errors](https://arxiv.org/abs/2511.09030) (arXiv:2511.09030v1).

## 🚀 Key Features

- **Maximal Agentic Decomposition (MAD)**: Automatically breaks complex tasks into minimal subtasks to prevent reliability decay.
- **First-to-ahead-by-k Voting**: Uses mathematical consensus to guarantee success even with imperfect models.
- **Red-Flag Filtration**: Real-time monitoring to catch and discard "suspicious" outputs (hallucinations, loops, hedging).
- **ASP v2.0 Compliant**: Universal skill standard for any IDE or Agent (Claude Code, Cursor, etc.).

## 📦 Installation

To use this framework:

1.  **Antigravity Agents**: Place the provided `.skill` file in your `~/.antigravity/skills/` directory.

2.  **Generic Agents (Claude Code / Cursor)**: Clone this repository and point your agent to this directory. It will detect the `SKILL.md` and `scripts/` automatically.

## 🛠️ Components

- `voting.py`: Consensus algorithm with scaling law calculators.
- `red_flag.py`: Heuristic filters for response quality.
- `simulation_test.py`: Reproduce the paper's findings on reliability scaling.

## 📚 References

- Sinha, S., et al. (2025). *Solving a Million-Step LLM Task with Zero Errors*. arXiv:2511.09030.
- [ASP v2.0 Protocol](https://github.com/salem221094/universal-skills-protocol)
