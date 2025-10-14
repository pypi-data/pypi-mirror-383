"""
dbop_runner
===========

Resilient SQLAlchemy operation runner with retry, backoff, SAVEPOINT handling,
and per-operation lock/statement timeouts.

Supports both sync and async SQLAlchemy 2.x sessions.
"""

from .runner import DBOpRunner

__all__ = ["DBOpRunner"]
__version__ = "1.0.2"
