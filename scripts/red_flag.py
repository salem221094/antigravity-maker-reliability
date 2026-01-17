#!/usr/bin/env python3
"""
MAKER Red-Flag Detection: Output validation and suspicious response filtering.

Based on the MAKER framework from "Solving a Million-Step LLM Task with Zero Errors".
Red-flagging increases effective per-step accuracy by discarding responses that
show signs of confusion or error, before they corrupt the pipeline.
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class RedFlagType(Enum):
    """Types of red flags that can be detected."""
    TOO_LONG = "too_long"
    TOO_SHORT = "too_short"
    WRONG_FORMAT = "wrong_format"
    LOW_CONFIDENCE = "low_confidence"
    REPETITIVE = "repetitive"
    OFF_TOPIC = "off_topic"


@dataclass
class RedFlagResult:
    """Result of red-flag detection."""
    is_flagged: bool
    flags: List[RedFlagType]
    reasons: List[str]
    confidence: float  # 0.0 = definitely bad, 1.0 = definitely good
    
    def __bool__(self) -> bool:
        return self.is_flagged


# Patterns indicating low confidence / hedging
HEDGING_PATTERNS = [
    r"\bi(?:'m| am) not (?:entirely |completely |totally )?(?:sure|certain)\b",
    r"\bi think (?:it )?might\b",
    r"\bprobably\b.*\bmaybe\b",
    r"\bi(?:'m| am) (?:just )?guessing\b",
    r"\bthis (?:could|might|may) be wrong\b",
    r"\bi don't (?:really )?know\b",
    r"\bI'm uncertain\b",
    r"\bhard to say\b",
]

# Patterns indicating the model went off-rails
OFF_RAILS_PATTERNS = [
    r"(?:as an ai|as a language model)",  # Self-referential hedging
    r"i (?:cannot|can't|am unable to) (?:actually |really )?(?:do|perform|execute)",
    r"(?:let me|allow me to) (?:think|consider|reflect)",  # Excessive deliberation
    r"(?:wait|hold on|actually),? (?:let me|I need to) (?:reconsider|rethink)",
]


def check_length(
    response: str,
    min_tokens: Optional[int] = None,
    max_tokens: Optional[int] = None,
    chars_per_token: float = 4.0
) -> Optional[tuple[RedFlagType, str]]:
    """Check if response length is within acceptable bounds."""
    estimated_tokens = len(response) / chars_per_token
    
    if max_tokens and estimated_tokens > max_tokens:
        return (
            RedFlagType.TOO_LONG,
            f"Response too long: ~{int(estimated_tokens)} tokens (max: {max_tokens})"
        )
    
    if min_tokens and estimated_tokens < min_tokens:
        return (
            RedFlagType.TOO_SHORT,
            f"Response too short: ~{int(estimated_tokens)} tokens (min: {min_tokens})"
        )
    
    return None


def check_format(
    response: str,
    require_format: Optional[str] = None,
    required_fields: Optional[List[str]] = None
) -> Optional[tuple[RedFlagType, str]]:
    """Check if response matches expected format."""
    if require_format == "json":
        response_stripped = response.strip()
        # Check for JSON structure
        if not (response_stripped.startswith('{') or response_stripped.startswith('[')):
            return (RedFlagType.WRONG_FORMAT, "Expected JSON but response doesn't start with { or [")
        
        try:
            import json
            parsed = json.loads(response_stripped)
            
            # Check required fields if specified
            if required_fields and isinstance(parsed, dict):
                missing = [f for f in required_fields if f not in parsed]
                if missing:
                    return (
                        RedFlagType.WRONG_FORMAT,
                        f"Missing required JSON fields: {missing}"
                    )
        except json.JSONDecodeError as e:
            return (RedFlagType.WRONG_FORMAT, f"Invalid JSON: {e}")
    
    elif require_format == "code":
        # Check for code block markers or typical code patterns
        has_code_block = "```" in response
        has_code_patterns = bool(re.search(r'(?:def |class |function |const |let |var |import |from )', response))
        
        if not (has_code_block or has_code_patterns):
            return (RedFlagType.WRONG_FORMAT, "Expected code but no code patterns found")
    
    elif require_format == "single_line":
        if '\n' in response.strip():
            return (RedFlagType.WRONG_FORMAT, "Expected single line but got multiple lines")
    
    return None


def check_confidence(response: str) -> Optional[tuple[RedFlagType, str]]:
    """Check for hedging language indicating low confidence."""
    response_lower = response.lower()
    
    for pattern in HEDGING_PATTERNS:
        if re.search(pattern, response_lower):
            return (
                RedFlagType.LOW_CONFIDENCE,
                f"Hedging language detected: matches pattern '{pattern}'"
            )
    
    return None


def check_off_rails(response: str) -> Optional[tuple[RedFlagType, str]]:
    """Check for patterns indicating the model went off-topic or confused."""
    response_lower = response.lower()
    
    for pattern in OFF_RAILS_PATTERNS:
        if re.search(pattern, response_lower):
            return (
                RedFlagType.OFF_TOPIC,
                f"Off-rails pattern detected: matches '{pattern}'"
            )
    
    return None


def check_repetition(response: str, threshold: float = 0.3) -> Optional[tuple[RedFlagType, str]]:
    """Check for excessive repetition (a sign of confusion/looping)."""
    words = response.lower().split()
    if len(words) < 20:
        return None  # Too short to meaningfully check
    
    # Check for repeated phrases (3-grams)
    trigrams = [' '.join(words[i:i+3]) for i in range(len(words) - 2)]
    unique_ratio = len(set(trigrams)) / len(trigrams) if trigrams else 1.0
    
    if unique_ratio < (1 - threshold):
        return (
            RedFlagType.REPETITIVE,
            f"High repetition detected: {(1-unique_ratio)*100:.1f}% repeated trigrams"
        )
    
    return None


def is_red_flagged(
    response: str,
    min_tokens: Optional[int] = None,
    max_tokens: Optional[int] = None,
    require_format: Optional[str] = None,
    required_fields: Optional[List[str]] = None,
    check_hedging: bool = True,
    check_off_topic: bool = True,
    check_repetitive: bool = True,
    strict: bool = False
) -> RedFlagResult:
    """
    Check if a response should be red-flagged (discarded and resampled).
    
    Args:
        response: The LLM response to check
        min_tokens: Minimum expected tokens (approximate)
        max_tokens: Maximum expected tokens (approximate)
        require_format: Expected format ("json", "code", "single_line", or None)
        required_fields: For JSON format, list of required field names
        check_hedging: Whether to flag hedging/uncertainty language
        check_off_topic: Whether to flag off-rails patterns
        check_repetitive: Whether to flag excessive repetition
        strict: If True, any single flag triggers rejection
    
    Returns:
        RedFlagResult with is_flagged, flags list, reasons, and confidence score
    
    Example:
        >>> result = is_red_flagged("I'm not sure, but maybe...", check_hedging=True)
        >>> if result.is_flagged:
        ...     response = resample()  # Discard and try again
    """
    flags: List[RedFlagType] = []
    reasons: List[str] = []
    
    # Run all applicable checks
    checks = [
        check_length(response, min_tokens, max_tokens),
        check_format(response, require_format, required_fields),
    ]
    
    if check_hedging:
        checks.append(check_confidence(response))
    
    if check_off_topic:
        checks.append(check_off_rails(response))
    
    if check_repetitive:
        checks.append(check_repetition(response))
    
    # Collect all flags
    for result in checks:
        if result:
            flag_type, reason = result
            flags.append(flag_type)
            reasons.append(reason)
    
    # Calculate confidence (inverse of flag severity)
    if not flags:
        confidence = 1.0
    else:
        # Weight different flag types
        weights = {
            RedFlagType.WRONG_FORMAT: 0.0,  # Format errors are critical
            RedFlagType.TOO_LONG: 0.3,
            RedFlagType.TOO_SHORT: 0.3,
            RedFlagType.LOW_CONFIDENCE: 0.4,
            RedFlagType.REPETITIVE: 0.2,
            RedFlagType.OFF_TOPIC: 0.3,
        }
        confidence = min(weights.get(f, 0.5) for f in flags)
    
    # Determine if flagged
    if strict:
        is_flagged = len(flags) > 0
    else:
        # In non-strict mode, only flag on format errors or multiple issues
        critical_flags = {RedFlagType.WRONG_FORMAT, RedFlagType.REPETITIVE}
        is_flagged = bool(set(flags) & critical_flags) or len(flags) >= 2
    
    return RedFlagResult(
        is_flagged=is_flagged,
        flags=flags,
        reasons=reasons,
        confidence=confidence
    )


def filter_responses(
    responses: List[str],
    **kwargs
) -> List[str]:
    """
    Filter a list of responses, removing red-flagged ones.
    
    Args:
        responses: List of responses to filter
        **kwargs: Arguments passed to is_red_flagged()
    
    Returns:
        List of responses that passed red-flag checks
    """
    return [r for r in responses if not is_red_flagged(r, **kwargs).is_flagged]


if __name__ == "__main__":
    # Demo
    print("=== MAKER Red-Flag Detection Demo ===\n")
    
    # Example 1: Length check
    long_response = "word " * 1000
    result = is_red_flagged(long_response, max_tokens=100)
    print(f"Long response flagged: {result.is_flagged}")
    print(f"Reasons: {result.reasons}\n")
    
    # Example 2: Hedging detection
    hedging = "I'm not entirely sure, but I think it might be option A, probably."
    result = is_red_flagged(hedging, check_hedging=True)
    print(f"Hedging response flagged: {result.is_flagged}")
    print(f"Flags: {result.flags}")
    print(f"Confidence: {result.confidence}\n")
    
    # Example 3: JSON format check
    bad_json = "Here's the JSON: {invalid json}"
    result = is_red_flagged(bad_json, require_format="json")
    print(f"Bad JSON flagged: {result.is_flagged}")
    print(f"Reasons: {result.reasons}\n")
    
    # Example 4: Good response
    good = '{"action": "move", "from": "A", "to": "C"}'
    result = is_red_flagged(good, require_format="json", required_fields=["action"])
    print(f"Good response flagged: {result.is_flagged}")
    print(f"Confidence: {result.confidence}")
