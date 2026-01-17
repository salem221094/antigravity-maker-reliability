#!/usr/bin/env python3
"""Tests for the MAKER voting utility."""

import pytest
from voting import vote_until_consensus, calculate_required_k, estimate_expected_cost


class TestVoteUntilConsensus:
    """Tests for vote_until_consensus function."""
    
    def test_clear_winner(self):
        """Test with a clear winner."""
        candidates = ["A", "A", "A", "B"]
        winner = vote_until_consensus(candidates, k=2)
        assert winner == "A"
    
    def test_tie_resolution(self):
        """Test that ties are broken by seeing more candidates."""
        candidates = ["A", "B", "A", "B", "A", "A", "A"]
        winner = vote_until_consensus(candidates, k=3)
        assert winner == "A"
    
    def test_single_candidate(self):
        """Test with only one candidate type."""
        candidates = ["X", "X", "X"]
        winner = vote_until_consensus(candidates, k=3)
        assert winner == "X"
    
    def test_empty_list(self):
        """Test with empty candidate list."""
        winner = vote_until_consensus([], k=2)
        assert winner is None
    
    def test_k_equals_one(self):
        """Test with k=1 (first to lead by 1)."""
        candidates = ["A", "B", "A"]
        winner = vote_until_consensus(candidates, k=1)
        # After "A", A leads by 1, so A should win
        assert winner == "A"
    
    def test_numeric_candidates(self):
        """Test with numeric candidates."""
        candidates = [42, 42, 17, 42]
        winner = vote_until_consensus(candidates, k=2)
        assert winner == 42
    
    def test_equivalence_function(self):
        """Test with custom equivalence function."""
        candidates = ["HELLO", "hello", "Hello", "world"]
        winner = vote_until_consensus(
            candidates, 
            k=2,
            equivalence_fn=lambda a, b: a.lower() == b.lower()
        )
        assert winner.lower() == "hello"
    
    def test_max_samples_limit(self):
        """Test that max_samples is respected."""
        candidates = ["A"] * 1000
        winner = vote_until_consensus(candidates, k=500, max_samples=10)
        # Should return most common even if k not reached
        assert winner == "A"


class TestCalculateRequiredK:
    """Tests for calculate_required_k function."""
    
    def test_basic_calculation(self):
        """Test basic k calculation."""
        k = calculate_required_k(1000, per_step_accuracy=0.8, target_success_rate=0.99)
        assert k >= 1
        assert k <= 10  # Should be reasonable for these params
    
    def test_more_steps_needs_higher_k(self):
        """Test that more steps require higher k."""
        k_small = calculate_required_k(100, per_step_accuracy=0.8)
        k_large = calculate_required_k(1000000, per_step_accuracy=0.8)
        assert k_large > k_small
    
    def test_higher_accuracy_needs_lower_k(self):
        """Test that higher accuracy needs lower k."""
        k_low_acc = calculate_required_k(10000, per_step_accuracy=0.7)
        k_high_acc = calculate_required_k(10000, per_step_accuracy=0.9)
        assert k_high_acc < k_low_acc
    
    def test_rejects_low_accuracy(self):
        """Test that accuracy <= 0.5 raises error."""
        with pytest.raises(ValueError):
            calculate_required_k(100, per_step_accuracy=0.5)
    
    def test_minimum_k_is_one(self):
        """Test that k is at least 1."""
        k = calculate_required_k(1, per_step_accuracy=0.99, target_success_rate=0.99)
        assert k >= 1


class TestEstimateExpectedCost:
    """Tests for estimate_expected_cost function."""
    
    def test_basic_cost(self):
        """Test basic cost estimation."""
        cost = estimate_expected_cost(
            total_steps=100,
            k=3,
            per_step_accuracy=0.8,
            cost_per_call=1.0
        )
        assert cost > 0
        assert cost > 100  # Should be more than just s calls due to voting
    
    def test_higher_k_means_higher_cost(self):
        """Test that higher k increases cost."""
        cost_k3 = estimate_expected_cost(100, k=3, per_step_accuracy=0.8)
        cost_k7 = estimate_expected_cost(100, k=7, per_step_accuracy=0.8)
        assert cost_k7 > cost_k3
    
    def test_cost_scales_with_steps(self):
        """Test that cost scales with number of steps."""
        cost_100 = estimate_expected_cost(100, k=3, per_step_accuracy=0.8)
        cost_1000 = estimate_expected_cost(1000, k=3, per_step_accuracy=0.8)
        # Should be roughly 10x
        assert 8 < cost_1000 / cost_100 < 12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
