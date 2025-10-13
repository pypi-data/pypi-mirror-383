"""Utility helpers for dbop_runner."""

import random


def backoff_delay(attempt: int, initial: float, max_delay: float) -> float:
    """Compute exponential backoff delay with full jitter."""
    return min(initial * (2**attempt) + random.uniform(0, initial), max_delay)
