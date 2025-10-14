# dbop-runner

**Resilient SQLAlchemy operation runner**
Retry, backoff, SAVEPOINT handling, and backend-specific timeouts — all while using your existing SQLAlchemy sessions.

- Works with `Session` and `AsyncSession`
- Retries transient faults (deadlocks, lock timeouts, disconnects)
- Uses SAVEPOINTs when already inside a transaction
- Supports per-operation `lock_timeout` and `statement_timeout`
- Backends: PostgreSQL, MySQL/MariaDB, SQLite
- Typed, small, and framework-agnostic (FastAPI/Gunicorn friendly)

---

## Why

Typical DB code either:

1. Does not retry (deadlocks bubble up and fail the request), or
2. Retries blindly and risks partial commits within a transaction.

`dbop-runner` provides a simple, safe abstraction:

> Run a single operation function against an existing SQLAlchemy session with retries.
> When already in a transaction, it retries inside a SAVEPOINT so your outer work remains intact.
> You still decide when to commit or rollback.

---

## Installation

```bash
# Minimal
pip install dbop-runner

# With dev tools
pip install "dbop-runner[dev]"

# With drivers used in integration tests
pip install "dbop-runner[postgres,mysql]"
````

Supported environments:

* SQLAlchemy 2.x
* PostgreSQL: `psycopg` (sync), `asyncpg` (async)
* MySQL/MariaDB: `pymysql` (sync), `aiomysql` (async)
* SQLite / `aiosqlite` (for tests)

---

## Quick Start (Async)

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from dbop_runner import DBOpRunner

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db", pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
runner = DBOpRunner(max_retries=5, default_lock_timeout_s=5)

async def update_user(sess: AsyncSession):
    await sess.execute(text("UPDATE users SET seen_at = now() WHERE id=:id"), {"id": 42})

async def main():
    async with SessionLocal() as sess:
        # Standalone run
        await runner.run_async(sess, update_user, name="update-user")

        # Under a managed transaction
        async with sess.begin():
            await runner.run_async(sess, update_user, name="update-user")
```

---

## Quick Start (Sync)

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dbop_runner import DBOpRunner

engine = create_engine("postgresql+psycopg://user:pass@localhost/db", pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
runner = DBOpRunner(max_retries=3, default_lock_timeout_s=5)

def rename(sess: Session):
    sess.execute(text("UPDATE projects SET name=:n WHERE id=:id"), {"id": 1, "n": "Demo"})

with SessionLocal() as sess, sess.begin():
    runner.run(sess, rename, name="rename-project")
```

---

## How It Works

* You own the outer transaction (`with sess.begin(): ...`) — `dbop-runner` never commits for you.
* Each operation runs inside a SAVEPOINT using `begin_nested()`.
* Transient errors (deadlocks, timeouts) rollback only the inner step and retry cleanly.
* If no transaction is open, the runner opens one automatically.

This pattern fits production systems where multiple steps form one atomic unit of work.

---

## Common Patterns

Use **dbop-runner** whenever you want to run database operations *safely and predictably* — especially when you’re dealing with transient issues like deadlocks, lock waits, or query timeouts.
It gives you a **consistent retry and timeout layer** across PostgreSQL, MySQL/MariaDB, and SQLite — without having to change your ORM or connection code.

### Batch of steps

Run multiple operations as a transaction, letting `dbop-runner` manage per-step retries:

```python
with sess.begin():
    runner.run(sess, step_a, name="step-a")
    runner.run(sess, step_b, name="step-b")
```

Ideal when each step might temporarily fail (e.g., due to lock contention), but you still want the entire batch to commit atomically once all succeed.

---

### Read-only operation

For queries or analytics tasks that don’t modify data:

```python
rows = runner.run(sess, lambda s: s.execute(text("SELECT ...")), name="read-x", read_only=True)
```

Enables safer parallel read access while enforcing retry and timeout policies.

---

### Conditional abort

Abort gracefully within a transaction when business logic requires it:

```python
with sess.begin():
    runner.run(sess, step_a, name="step-a")
    if should_abort:
        raise RuntimeError("abort")
    runner.run(sess, step_b, name="step-b")
```

If an exception occurs, `dbop-runner` automatically rolls back and logs context for debugging.

---

### Per-operation timeouts

Fine-tune lock and statement timeouts *per call* instead of globally:

```python
runner.run(sess, step_fn, name="step", lock_timeout_s=3, stmt_timeout_s=10)
```

This is perfect for isolating slow or high-contention queries without affecting the rest of the workload.

| Backend       | Timeout Parameters                                      |
| ------------- | ------------------------------------------------------- |
| PostgreSQL    | `SET LOCAL lock_timeout`, `SET LOCAL statement_timeout` |
| MySQL/MariaDB | `innodb_lock_wait_timeout`, `MAX_EXECUTION_TIME`        |
| SQLite        | `connect_args={"timeout": …}`                           |

---

## Logging

`DBOpRunner` emits structured log records.

Example failure:

```python
{
  "message": "update-user failed",
  "dialect": "postgresql",
  "attempt": 0,
  "transient": True,
  "sync": False,
  "exception": "DBAPIError('...')"
}
```

Inject a custom logger:

```python
runner = DBOpRunner(logger=my_logger)
```

Log levels:

* `INFO` — final “done” record
* `WARNING` — transient, retryable error
* `ERROR` — non-retryable error

---

## Transient Error Detection

| Backend       | Retryable conditions                                                     |
| ------------- | ------------------------------------------------------------------------ |
| PostgreSQL    | deadlock (`40P01`), lock unavailable (`55P03`), `OperationalError`       |
| MySQL/MariaDB | deadlock (1213), lock wait timeout (1205), connection errors (2006/2013) |
| SQLite        | "database is locked", generic `OperationalError`                         |

Everything else is non-transient (no retry).

---

## API Overview

```python
class DBOpRunner:
    def __init__(
        *,
        max_retries: int = 5,
        initial_delay: float = 0.1,
        max_delay: float = 1.0,
        default_lock_timeout_s: int | None = 10,
        default_stmt_timeout_s: int | None = None,
        default_raises: bool = True,
        logger: logging.Logger | None = None,
    )

    def run(...): ...
    async def run_async(...): ...
```

---

## Recipes

**Read and write in one transaction**

```python
def read(sess):
    return sess.execute(text("SELECT id FROM users WHERE state=:s"), {"s": "active"}).scalars().all()

def write(sess):
    sess.execute(text("UPDATE users SET state='active' WHERE id=:id"), {"id": 7})

with sess.begin():
    ids = runner.run(sess, read, name="list-active", read_only=True, stmt_timeout_s=5)
    runner.run(sess, write, name="activate-user", lock_timeout_s=3)
```

**Async batch**

```python
async def step_a(s): await s.execute(text("UPDATE t1 SET val='a' WHERE id=1"))
async def step_b(s): await s.execute(text("UPDATE t2 SET val='b' WHERE id=1"))

async with async_sess.begin():
    await runner.run_async(async_sess, step_a, name="step-a")
    await runner.run_async(async_sess, step_b, name="step-b")
```

---

## Testing

### Unit (SQLite)

```bash
make test
make cov
```

### Integration (Docker)

Install deps (includes drivers):
```bash
make install-all
````

#### One-shot runs

```bash
make integration-pg        # bring up Postgres, run PG tests, keep container up
make integration-mysql     # bring up MySQL, run MySQL tests, keep container up
make integration-mariadb   # bring up MariaDB, run MariaDB tests, keep container up
make integration-all       # run PG -> MySQL -> MariaDB tests sequentially
```

#### Granular control

```bash
make integration-up            # start Postgres
make integration-test-pg       # run Postgres tests
make integration-down          # stop and clean up

make integration-up-mysql      # start MySQL
make integration-test-mysql    # run MySQL tests
make integration-down          # stop and clean up

make integration-up-mariadb    # start MariaDB
make integration-test-mariadb  # run MariaDB tests
make integration-down          # stop and clean up
```

#### Logs (tail/follow)

```bash
make integration-logs        # last 200 lines for all services
make integration-logs-pg     # follow Postgres logs
make integration-logs-mysql  # follow MySQL logs
make integration-logs-mariadb# follow MariaDB logs
```
---

## Local Development

### 1. Install Dependencies

```bash
# Using uv (fast)
uv venv .venv
uv pip install -e '.[dev,postgres,mysql]'
```

Or with pip:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev,postgres,mysql]'
```

### 2. Create `.env` (ignored by Git)

```dotenv
TEST_SYNC_DB_URL=sqlite:///./.pytest-sqlite.db
TEST_ASYNC_DB_URL=sqlite+aiosqlite:///./.pytest-sqlite.db
PYTHONPATH=src
```

Keep `.env` ignored and commit `env.example` instead.

### 3. Run Tests

```bash
make test
make cov
```

---

## Migration Examples

Examples of migrating from explicit commit/rollback flows to `DBOpRunner` are available in the full documentation. Examples can be used as a small poc environment for trials.

---

## Compatibility

* Python 3.9 – 3.13
* SQLAlchemy 2.x
* PostgreSQL, MySQL/MariaDB, SQLite

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

---

## License

MIT © 2025–present.
See [LICENSE](LICENSE) for full terms.

---

## Support and Contact

For questions or issues, open an issue or discussion at
[https://github.com/yokha/dbop-runner](https://github.com/yokha/dbop-runner)

---

**Developed by Youssef Khaya**
[LinkedIn](https://www.linkedin.com/in/youssef-khaya-88a1a128)
---
