# Agent-Zero: Theory & Scaling Laws

Deep-dive reference on the mathematical foundations of the Agent-Zero (MAKER) framework.

## Core Insight

For a task with `s` total steps and per-step accuracy `p`:

**Without Agent-Zero**: Success probability = p^s → exponentially decays  
**With Agent-Zero (voting)**: Success probability → near 1 (configurable via k)

## Maximal Agentic Decomposition (MAD)

### Why Decompose?

| Approach | Context Size | Error Behavior | Correction |
|----------|--------------|----------------|------------|
| Monolithic | Grows with task | Compounds | Impossible |
| MAD (m=1) | Constant | Independent | Per-step voting |

### The Decomposition Paradox

More steps = more failure points, BUT:
- Each step is simpler → higher per-step accuracy
- Errors become independent → correctable via voting
- Net effect: **reliability increases with decomposition**

## First-to-ahead-by-k Voting

### How It Works

Sample responses until one candidate leads by k votes:

```
Round 1: A      → A:1, B:0
Round 2: B      → A:1, B:1
Round 3: A      → A:2, B:1
Round 4: A      → A:3, B:1  ← A wins (leads by 2, if k=2)
```

### Hitting Probability Formula

For per-step accuracy `p > 0.5`, the probability the correct answer wins:

```
P(correct wins) = 1 - ((1-p)/p)^k
```

| p    | k=3   | k=5    | k=7     |
|------|-------|--------|---------|
| 0.6  | 93.6% | 98.7%  | 99.7%   |
| 0.7  | 97.4% | 99.6%  | 99.95%  |
| 0.8  | 99.2% | 99.92% | 99.995% |
| 0.9  | 99.9% | 99.999%| 99.9999%|

### Minimum k for Target Reliability

For `s` total steps and target success rate `t`:

```python
k_min = ceil(log(s * (1-t) / t) / (2 * log(p / (1-p))))
```

| Steps (s) | p=0.7, t=99% | p=0.8, t=99% | p=0.9, t=99% |
|-----------|--------------|--------------|--------------|
| 100       | k=4          | k=3          | k=2          |
| 10,000    | k=6          | k=4          | k=3          |
| 1,000,000 | k=8          | k=5          | k=4          |

**Key insight**: k grows logarithmically with s, not linearly!

## Cost Analysis

### Expected Samples per Step

For first-to-k voting:

```
E[samples] ≈ k / (2p - 1)
```

### Total Cost

```
Total cost = s × (k / (2p - 1)) × cost_per_call
```

For s=1M, p=0.8, k=5:
```
Total = 1,000,000 × (5 / 0.6) × 1 = 8.3M calls
```

This is **feasible** with modern LLMs at ~$0.0001/call = ~$830 total.

## Red-Flagging Effects

Red-flagging increases effective `p` by filtering bad responses:

| Without Red-Flagging | With Red-Flagging |
|---------------------|-------------------|
| p = 0.80            | p = 0.95          |
| k_min = 5 for 1M    | k_min = 3 for 1M  |
| 8.3M calls          | 3.3M calls        |

### What to Flag

1. **Long responses** (>2x expected) → model confused
2. **Malformed output** → parsing will fail anyway
3. **Hedging language** → low confidence = higher error rate
4. **Self-reference** ("As an AI...") → going off-rails

## Practical Guidelines

### Choosing k

| Use Case | Suggested k | Notes |
|----------|-------------|-------|
| Development/testing | 1 | Fast iteration |
| Standard operations | 3 | Good balance |
| Deployment/mutations | 5 | Data integrity matters |
| Security/financial | 7 | Maximum safety |
| Life-critical | 11+ | Overkill for most |

### When NOT to Use Full MAKER

- Single-step tasks (just use regular prompting)
- Exploratory/creative tasks (voting kills creativity)
- p > 0.99 already (diminishing returns)

### Decorrelating Errors

If errors are correlated across samples:
- Vary temperature between samples
- Paraphrase prompts slightly
- Use different model sizes/versions
- The goal: make each sample truly independent

## References

- Paper: "Solving a Million-Step LLM Task with Zero Errors" (arXiv:2511.09030v1)
- Random walk theory / Gambler's ruin
- Sequential Probability Ratio Test (SPRT)
