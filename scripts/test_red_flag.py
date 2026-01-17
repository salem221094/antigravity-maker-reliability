#!/usr/bin/env python3
"""Tests for the MAKER red-flag detection utility."""

import pytest
from red_flag import (
    is_red_flagged,
    filter_responses,
    RedFlagType,
    check_length,
    check_format,
    check_confidence,
    check_repetition
)


class TestCheckLength:
    """Tests for length checking."""
    
    def test_too_long(self):
        """Test detection of too-long responses."""
        response = "word " * 500  # ~500 words ≈ 2500 chars ≈ 625 tokens
        result = check_length(response, max_tokens=100)
        assert result is not None
        assert result[0] == RedFlagType.TOO_LONG
    
    def test_too_short(self):
        """Test detection of too-short responses."""
        response = "ok"
        result = check_length(response, min_tokens=10)
        assert result is not None
        assert result[0] == RedFlagType.TOO_SHORT
    
    def test_acceptable_length(self):
        """Test that acceptable length passes."""
        response = "This is a normal length response that should pass."
        result = check_length(response, min_tokens=5, max_tokens=100)
        assert result is None


class TestCheckFormat:
    """Tests for format checking."""
    
    def test_valid_json(self):
        """Test that valid JSON passes."""
        response = '{"action": "move", "target": "C"}'
        result = check_format(response, require_format="json")
        assert result is None
    
    def test_invalid_json(self):
        """Test that invalid JSON is flagged."""
        response = '{not valid json}'
        result = check_format(response, require_format="json")
        assert result is not None
        assert result[0] == RedFlagType.WRONG_FORMAT
    
    def test_json_missing_fields(self):
        """Test that missing required fields are flagged."""
        response = '{"foo": "bar"}'
        result = check_format(response, require_format="json", required_fields=["action"])
        assert result is not None
        assert "action" in result[1]
    
    def test_code_format(self):
        """Test code format detection."""
        response = "def hello(): print('world')"
        result = check_format(response, require_format="code")
        assert result is None
    
    def test_single_line_format(self):
        """Test single line format."""
        response = "single line"
        result = check_format(response, require_format="single_line")
        assert result is None
        
        multiline = "line1\nline2"
        result = check_format(multiline, require_format="single_line")
        assert result is not None


class TestCheckConfidence:
    """Tests for hedging/confidence detection."""
    
    def test_hedging_detected(self):
        """Test that hedging language is detected."""
        hedging_responses = [
            "I'm not sure, but maybe it's A",
            "I think it might be correct",
            "I'm just guessing here",
            "This could be wrong, but...",
        ]
        for response in hedging_responses:
            result = check_confidence(response)
            assert result is not None, f"Should flag: {response}"
    
    def test_confident_response(self):
        """Test that confident responses pass."""
        confident = "The answer is A. Move disk 1 to peg C."
        result = check_confidence(confident)
        assert result is None


class TestCheckRepetition:
    """Tests for repetition detection."""
    
    def test_repetitive_text(self):
        """Test that repetitive text is flagged."""
        repetitive = "move disk move disk move disk move disk " * 10
        result = check_repetition(repetitive)
        assert result is not None
        assert result[0] == RedFlagType.REPETITIVE
    
    def test_normal_text(self):
        """Test that varied text passes."""
        varied = "First we move disk one to C. Then disk two goes to B. Finally disk one goes to B."
        result = check_repetition(varied)
        assert result is None
    
    def test_short_text_skipped(self):
        """Test that short text is not checked."""
        short = "too short to check"
        result = check_repetition(short)
        assert result is None


class TestIsRedFlagged:
    """Integration tests for is_red_flagged."""
    
    def test_good_response(self):
        """Test that a good response passes."""
        response = '{"action": "move", "disk": 1, "to": "C"}'
        result = is_red_flagged(response, require_format="json", max_tokens=100)
        assert not result.is_flagged
        assert result.confidence > 0.9
    
    def test_multiple_flags(self):
        """Test that multiple issues trigger flagging."""
        # Too long + hedging
        response = ("I'm not entirely sure, but " + "maybe " * 200)
        result = is_red_flagged(response, max_tokens=50, check_hedging=True)
        assert result.is_flagged
        assert len(result.flags) >= 2
    
    def test_strict_mode(self):
        """Test strict mode flags on any issue."""
        response = "I'm not sure about this answer"
        result_normal = is_red_flagged(response, strict=False, check_hedging=True)
        result_strict = is_red_flagged(response, strict=True, check_hedging=True)
        
        # Strict should flag on hedging alone
        assert result_strict.is_flagged
    
    def test_confidence_score(self):
        """Test that confidence scores are reasonable."""
        good = "The answer is A."
        bad = "I don't know, maybe, probably not sure"
        
        result_good = is_red_flagged(good)
        result_bad = is_red_flagged(bad, check_hedging=True)
        
        assert result_good.confidence > result_bad.confidence


class TestFilterResponses:
    """Tests for filter_responses utility."""
    
    def test_filters_bad_responses(self):
        """Test that bad responses are filtered out."""
        responses = [
            '{"valid": true}',
            '{invalid json}',
            '{"also": "valid"}',
        ]
        filtered = filter_responses(responses, require_format="json")
        assert len(filtered) == 2
        assert '{invalid json}' not in filtered


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
