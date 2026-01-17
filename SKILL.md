---
name: maker-reliability
description: "Automatic error-correction framework for high-stakes multi-step tasks using MAKER principles (Maximal Agentic Decomposition, voting consensus, red-flagging). Auto-triggers for: (1) complex workflows with more than 5 steps, (2) critical operations (deployment, data mutation, security), (3) any task where reliability over speed is required. Provides voting utilities and output validation filters."
---

# MAKER Reliability Framework

Implements the MAKER (Massively decomposed AgenT KERnel) framework for zero-error execution of long-horizon tasks.

## Core Principles

### 1. Maximal Agentic Decomposition (MAD)
Break tasks into the smallest possible subtasks (m=1 step per call). Benefits:
- Reduces context length → fewer errors
- Enables per-step error correction
- Allows smaller, focused models to succeed

### 2. First-to-ahead-by-k Voting
For critical steps, sample multiple times and pick the answer that leads by k votes:
- k=3 for standard critical operations
- k=5 for high-stakes (deployment, security, financial)
- k=7+ for mission-critical (rarely needed)

### 3. Red-Flagging
Discard suspicious outputs before they corrupt the pipeline:
- **Too long**: Response exceeds expected length → likely confused
- **Wrong format**: Malformed output → model went off-rails
- **Low confidence**: Hedging language patterns → uncertain

## When This Skill Auto-Triggers

| Condition | Action |
|-----------|--------|
| Task has >5 sequential steps | Apply MAD decomposition |
| Step involves deployment/mutation | Use k=3 voting |
| Step involves security/financial | Use k=5 voting |
| Output seems malformed | Red-flag and resample |

## Usage

### Voting for Critical Decisions

```python
# Import the voting utility
from maker_reliability.voting import vote_until_consensus

# Get consensus on a critical decision
candidates = [generate_response() for _ in range(10)]
winner = vote_until_consensus(candidates, k=3)
```

### Red-Flag Filtering

```python
from maker_reliability.red_flag import is_red_flagged

response = get_llm_response()
if is_red_flagged(response, max_tokens=500, require_format="json"):
    response = resample()  # Discard and try again
```

## Integration with Task Boundaries

This skill works with the existing `task_boundary` tool:
- Each task boundary represents a decomposition level
- Status updates enable progress tracking
- Mode switching (PLANNING/EXECUTION/VERIFICATION) maps to MAKER phases

## Theory Reference

For mathematical foundations (scaling laws, cost formulas, k optimization):
→ See [maker-theory.md](references/maker-theory.md)

## Scripts

| Script | Purpose |
|--------|---------|
| [voting.py](scripts/voting.py) | First-to-ahead-by-k consensus voting |
| [red_flag.py](scripts/red_flag.py) | Output validation and red-flag detection |
