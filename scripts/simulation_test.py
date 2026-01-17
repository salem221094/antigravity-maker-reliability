#!/usr/bin/env python3
"""
Agent-Zero Reliability Simulation: Comparing Standard Agent vs. Agent-Zero.

This script simulates a multi-step task (like Tower of Hanoi or code refactoring)
and demonstrates how Agent-Zero's voting principle prevents exponential reliability decay.
"""

import random
import time
from typing import List, Tuple
import sys
import os

# Add scripts directory to path to import voting
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from voting import vote_until_consensus

# Simulation Parameters
TOTAL_STEPS = 100
LLM_ACCURACY = 0.8  # 80% accuracy per step
VOTING_K = 7        # Lead by 7 votes to win for 99%+ success over 100 steps

def simulate_step(accuracy: float) -> bool:
    """Simulates a single LLM step. Returns True if correct."""
    return random.random() < accuracy

def run_standard_agent(steps: int, accuracy: float) -> Tuple[bool, int]:
    """Simulates a single agent doing all steps. One mistake = failure."""
    for i in range(1, steps + 1):
        if not simulate_step(accuracy):
            return False, i  # Failed at step i
    return True, steps

def run_maker_agent(steps: int, accuracy: float, k: int) -> Tuple[bool, int, int]:
    """Simulates Agent-Zero agent with voting at every step."""
    total_calls = 0
    for i in range(1, steps + 1):
        # MAKER samples until consensus
        samples = []
        while True:
            total_calls += 1
            # Simulate sampling (True = correct candidate, False = incorrect candidate)
            # In a real race, there might be multiple incorrect ones, but we assume
            # the worst case: one strong incorrect competitor.
            samples.append(simulate_step(accuracy))
            
            # Check for winner
            winner = vote_until_consensus(samples, k=k)
            if winner is not None:
                if not winner: # If the winner is 'False' (the incorrect action)
                    return False, i, total_calls
                break # Consensus reached on correct action, move to next step
    return True, steps, total_calls

def main():
    print("="*60)
    print(f"AGENT-ZERO RELIABILITY SIMULATION")
    print(f"Task Length: {TOTAL_STEPS} steps")
    print(f"Agent Step-wise Accuracy: {LLM_ACCURACY*100}%")
    print(f"Agent-Zero Voting Margin (k): {VOTING_K}")
    print("="*60)
    print("\n[1] Running Standard Agent (No Agent-Zero)...")
    
    standard_successes = 0
    trials = 1000
    for _ in range(trials):
        success, _ = run_standard_agent(TOTAL_STEPS, LLM_ACCURACY)
        if success: standard_successes += 1
        
    print(f"Results over {trials} trials:")
    print(f"  - Success Rate: {standard_successes/trials*100:.2f}%")
    print(f"  - Theoretical:  {(LLM_ACCURACY**TOTAL_STEPS)*100:.8f}%")
    
    print("\n[2] Running Agent-Zero (Voting & Decomposition)...")
    
    maker_successes = 0
    total_calls_to_llm = 0
    for _ in range(trials):
        success, step_failed, calls = run_maker_agent(TOTAL_STEPS, LLM_ACCURACY, VOTING_K)
        total_calls_to_llm += calls
        if success: maker_successes += 1
        
    print(f"Results over {trials} trials:")
    print(f"  - Success Rate: {maker_successes/trials*100:.2f}%")
    print(f"  - Avg LLM Calls/Task: {total_calls_to_llm/trials:.1f}")
    print(f"  - Reliability Gain: {((maker_successes/trials) / (max(standard_successes/trials, 1e-10))):,.0f}x")

    print("\n" + "="*60)
    print("CONCLUSION:")
    print(f"Standard agent failure is almost certain ({100 - standard_successes/trials*100:.2f}% failure).")
    print(f"Agent-Zero achieves near-perfect reliability ({maker_successes/trials*100:.2f}%)")
    print(f"by using ~{total_calls_to_llm/trials/TOTAL_STEPS:.1f}x more calls per step.")
    print("="*60)

if __name__ == "__main__":
    main()
