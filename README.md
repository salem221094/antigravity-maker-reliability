# Antigravity MAKER Reliability Framework

Implementation of the **MAKER (Massively decomposed AgenT KERnel)** framework for zero-error execution of long-horizon tasks, based on the research paper [Solving a Million-Step LLM Task with Zero Errors](https://arxiv.org/abs/2511.09030) (arXiv:2511.09030v1).

## 🚀 Key Features

- **Maximal Agentic Decomposition (MAD)**: Automatically breaks complex tasks into minimal subtasks to prevent reliability decay.
- **First-to-ahead-by-k Voting**: Uses mathematical consensus to guarantee success even with imperfect models.
- **Red-Flag Filtration**: Real-time monitoring to catch and discard "suspicious" outputs (hallucinations, loops, hedging).

## 📦 Installation

To use this framework in your Antigravity setup:

1.  Place the provided `.skill` file in your `~/.antigravity/skills/` directory.

Alternatively, you can clone this repository and copy the folder:
```bash
git clone https://github.com/salem221094/antigravity-maker-reliability.git
mkdir -p ~/.antigravity/skills/core/
cp -r antigravity-maker-reliability ~/.antigravity/skills/core/maker-reliability
```

## 🛠️ Components

- `voting.py`: Consensus algorithm with scaling law calculators.
- `red_flag.py`: Heuristic filters for response quality.
- `simulation_test.py`: Reproduce the paper's findings on reliability scaling.

## 📚 References

- Sinha, S., et al. (2025). *Solving a Million-Step LLM Task with Zero Errors*. arXiv:2511.09030.
