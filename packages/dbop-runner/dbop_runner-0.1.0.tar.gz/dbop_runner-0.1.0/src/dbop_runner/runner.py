from __future__ import annotations

import asyncio
import logging
import random
import time
from collections.abc import Awaitable
from contextlib import asynccontextmanager, contextmanager, suppress
from typing import Callable, TypeVar

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, InvalidRequestError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

T = TypeVar("T")

log = logging.getLogger(__name__)

# ---- backoff -------------------------------------------------------------


def _backoff_delay(attempt: int, initial: float, max_delay: float) -> float:
    # exponential + full jitter
    return min(initial * (2**attempt) + random.uniform(0, initial), max_delay)


# ---- transient classification -------------------------------------------

_PG_DEADLOCK = "40P01"
_PG_LOCK_NOT_AVAILABLE = "55P03"
_MYSQL_DEADLOCK = 1213
_MYSQL_LOCK_WAIT_TIMEOUT = 1205
_MYSQL_LOST_CONN = {2006, 2013}
_SQLITE_LOCK_MSG = "database is locked"


def _is_transient(dialect: str, err: DBAPIError) -> bool:
    orig = getattr(err, "orig", None)
    msg = str(err).lower()

    if dialect == "postgresql":
        code = getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
        if code in (_PG_DEADLOCK, _PG_LOCK_NOT_AVAILABLE):
            return True
        return isinstance(err, OperationalError)

    if dialect in ("mysql", "mariadb"):
        errno = None
        if hasattr(orig, "args") and orig.args:
            with suppress(Exception):
                errno = int(orig.args[0])
        if errno in (_MYSQL_DEADLOCK, _MYSQL_LOCK_WAIT_TIMEOUT) or errno in _MYSQL_LOST_CONN:
            return True
        return isinstance(err, OperationalError)

    if dialect == "sqlite":
        if _SQLITE_LOCK_MSG in msg:
            return True
        return isinstance(err, OperationalError)

    return isinstance(err, OperationalError)


# ---- timeout applicators -------------------------------------------------


def _apply_timeouts_sync(
    sess: Session, dialect: str, lock_timeout_s: int | None, stmt_timeout_s: int | None
) -> None:
    if dialect == "postgresql":
        # Postgres: SET accepts literal, bind parameters are invalid.
        if lock_timeout_s is not None:
            sess.execute(text(f"SET LOCAL lock_timeout = '{int(lock_timeout_s)}s'"))
        if stmt_timeout_s is not None:
            sess.execute(text(f"SET LOCAL statement_timeout = '{int(stmt_timeout_s)}s'"))
    elif dialect in ("mysql", "mariadb"):
        if lock_timeout_s is not None:
            sess.execute(text(f"SET SESSION innodb_lock_wait_timeout = {int(lock_timeout_s)}"))
        if stmt_timeout_s is not None:
            sess.execute(text(f"SET SESSION MAX_EXECUTION_TIME = {int(stmt_timeout_s) * 1000}"))
    elif dialect == "sqlite":
        pass


async def _apply_timeouts_async(
    sess: AsyncSession, dialect: str, lock_timeout_s: int | None, stmt_timeout_s: int | None
) -> None:
    if dialect == "postgresql":
        if lock_timeout_s is not None:
            await sess.execute(text(f"SET LOCAL lock_timeout = '{int(lock_timeout_s)}s'"))
        if stmt_timeout_s is not None:
            await sess.execute(text(f"SET LOCAL statement_timeout = '{int(stmt_timeout_s)}s'"))
    elif dialect in ("mysql", "mariadb"):
        if lock_timeout_s is not None:
            await sess.execute(
                text(f"SET SESSION innodb_lock_wait_timeout = {int(lock_timeout_s)}")
            )
        if stmt_timeout_s is not None:
            await sess.execute(
                text(f"SET SESSION MAX_EXECUTION_TIME = {int(stmt_timeout_s) * 1000}")
            )
    elif dialect == "sqlite":
        pass


# ---- savepoint scopes ----------------------------------------------------


def _is_mysql_missing_savepoint(err: Exception) -> bool:
    # MySQL/MariaDB: SAVEPOINT ... does not exist (1305) — happens when the
    # server killed the whole outer transaction (e.g., deadlock victim),
    # so the SAVEPOINT we're rolling back to is gone.
    if not isinstance(err, DBAPIError):
        return False
    orig = getattr(err, "orig", None)
    try:
        code = orig.args[0] if orig and getattr(orig, "args", None) else None
    except Exception:
        code = None
    msg = (str(orig or err) or "").lower()
    return code == 1305 or ("savepoint" in msg and "does not exist" in msg)


@contextmanager
def _attempt_scope_sync(sess: Session, read_only: bool):
    """
    Prefer SAVEPOINT (begin_nested). If there's no outer transaction,
    fall back to begin(). On MySQL/MariaDB tolerate 'SAVEPOINT ... does not exist'
    during rollback (deadlock victim nuked the outer txn).
    """
    # --- try nested (SAVEPOINT) first ---
    try:
        tx = sess.begin_nested()
        try:
            if read_only:
                with suppress(Exception):
                    sess.execute(text("SET TRANSACTION READ ONLY"))
            yield
            tx.commit()
            return
        except InvalidRequestError:
            # e.g. no txn active; fall through to outer begin
            with suppress(Exception):
                tx.rollback()
            # continue to fallback below
        except Exception:
            # explicit rollback; swallow only the MySQL missing-savepoint case
            try:
                tx.rollback()
            except Exception as rb_exc:
                if not _is_mysql_missing_savepoint(rb_exc):
                    raise
            raise
    except InvalidRequestError:
        # couldn't create nested; fallback to outer begin
        pass

    # --- fallback: outer transaction ---
    tx = sess.begin()
    try:
        if read_only:
            with suppress(Exception):
                sess.execute(text("SET TRANSACTION READ ONLY"))
        yield
        tx.commit()
    except Exception:
        try:
            tx.rollback()
        except Exception as rb_exc:
            if not _is_mysql_missing_savepoint(rb_exc):
                raise
        raise


@asynccontextmanager
async def _attempt_scope_async(sess: AsyncSession, read_only: bool):
    """
    Async twin of the sync attempt scope with the same MySQL/MariaDB tolerance
    for missing savepoint during rollback.
    """
    # --- try nested (SAVEPOINT) first ---
    try:
        tx = await sess.begin_nested()
        try:
            if read_only:
                with suppress(Exception):
                    await sess.execute(text("SET TRANSACTION READ ONLY"))
            yield
            await tx.commit()
            return
        except InvalidRequestError:
            with suppress(Exception):
                await tx.rollback()
        except Exception:
            try:
                await tx.rollback()
            except Exception as rb_exc:
                if not _is_mysql_missing_savepoint(rb_exc):
                    raise
            raise
    except InvalidRequestError:
        pass

    # --- fallback: outer transaction ---
    tx = await sess.begin()
    try:
        if read_only:
            with suppress(Exception):
                await sess.execute(text("SET TRANSACTION READ ONLY"))
        yield
        await tx.commit()
    except Exception:
        try:
            await tx.rollback()
        except Exception as rb_exc:
            if not _is_mysql_missing_savepoint(rb_exc):
                raise
        raise


# ---- public runner -------------------------------------------------------


class DBOpRunner:
    """
    Stateless runner that executes a fn against an EXISTING Session/AsyncSession,
    with retry/backoff, per-attempt timeouts, and savepoint-based retries.

    You own the session lifecycle (Gunicorn multi-process, scoped/session proxy, etc.).
    """

    def __init__(
        self,
        *,
        max_retries: int = 5,
        initial_delay: float = 0.1,
        max_delay: float = 1.0,
        default_lock_timeout_s: int | None = 10,
        default_stmt_timeout_s: int | None = None,
        default_raises: bool = True,
        logger: logging.Logger | None = None,
    ) -> None:
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.default_lock_timeout_s = default_lock_timeout_s
        self.default_stmt_timeout_s = default_stmt_timeout_s
        self.default_raises = default_raises
        self.log = logger or log

    # --- sync ---
    def run(
        self,
        sess: Session,
        fn: Callable[[Session], T],
        *,
        name: str = "db-op",
        read_only: bool = False,
        lock_timeout_s: int | None = None,
        stmt_timeout_s: int | None = None,
        default: T | None = None,
        raises: bool | None = None,
    ) -> T | None:
        dialect = sess.bind.dialect.name  # type: ignore[union-attr]
        attempts = self.max_retries
        should_raise = self.default_raises if raises is None else raises
        start = time.perf_counter()

        for attempt in range(attempts + 1):
            try:
                with _attempt_scope_sync(sess, read_only):
                    _apply_timeouts_sync(
                        sess,
                        dialect,
                        self.default_lock_timeout_s if lock_timeout_s is None else lock_timeout_s,
                        self.default_stmt_timeout_s if stmt_timeout_s is None else stmt_timeout_s,
                    )
                    return fn(sess)

            except DBAPIError as e:  # noqa: PERF203
                transient = _is_transient(dialect, e)
                self._log_attempt(name, dialect, attempt, e, transient, sync=True)
                if transient and attempt < attempts:
                    time.sleep(_backoff_delay(attempt, self.initial_delay, self.max_delay))
                    continue
                if should_raise:
                    raise
                return default

            except Exception as e:  # noqa: PERF203
                self._log_attempt(name, dialect, attempt, e, False, sync=True)
                if should_raise:
                    raise
                return default
            finally:
                if attempt == attempts:
                    self._log_done(name, dialect, start, attempt)

        return default

    # --- async ---
    async def run_async(
        self,
        sess: AsyncSession,
        fn: Callable[[AsyncSession], Awaitable[T]],
        *,
        name: str = "db-op",
        read_only: bool = False,
        lock_timeout_s: int | None = None,
        stmt_timeout_s: int | None = None,
        default: T | None = None,
        raises: bool | None = None,
    ) -> T | None:
        dialect = sess.bind.dialect.name  # type: ignore[union-attr]
        attempts = self.max_retries
        should_raise = self.default_raises if raises is None else raises
        start = time.perf_counter()

        for attempt in range(attempts + 1):
            try:
                async with _attempt_scope_async(sess, read_only):
                    await _apply_timeouts_async(
                        sess,
                        dialect,
                        self.default_lock_timeout_s if lock_timeout_s is None else lock_timeout_s,
                        self.default_stmt_timeout_s if stmt_timeout_s is None else stmt_timeout_s,
                    )
                    return await fn(sess)

            except DBAPIError as e:  # noqa: PERF203
                transient = _is_transient(dialect, e)
                self._log_attempt(name, dialect, attempt, e, transient, sync=False)
                if transient and attempt < attempts:
                    await asyncio.sleep(_backoff_delay(attempt, self.initial_delay, self.max_delay))
                    continue
                if should_raise:
                    raise
                return default

            except Exception as e:  # noqa: PERF203
                self._log_attempt(name, dialect, attempt, e, False, sync=False)
                if should_raise:
                    raise
                return default
            finally:
                if attempt == attempts:
                    self._log_done(name, dialect, start, attempt)

        return default

    # --- logging ---
    def _log_attempt(
        self, name: str, dialect: str, attempt: int, exc: Exception, transient: bool, *, sync: bool
    ) -> None:
        lvl = logging.WARNING if transient else logging.ERROR
        self.log.log(
            lvl,
            {
                "message": f"{name} failed",
                "dialect": dialect,
                "attempt": attempt,
                "transient": transient,
                "sync": sync,
                "exception": repr(exc),
            },
        )

    def _log_done(self, name: str, dialect: str, start: float, attempts_used: int) -> None:
        elapsed = time.perf_counter() - start
        self.log.info({
            "message": f"{name} done",
            "dialect": dialect,
            "attempts_used": attempts_used + 1,
            "elapsed_s": round(elapsed, 6),
        })
