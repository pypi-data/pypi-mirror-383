# pylint: disable=cell-var-from-loop, too-many-locals
import json

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .conftest import (
    USER_ATTRS,
    USER_NAME,
    USER_STATE,
    execute_query,
)

# tests/test_db_op_basic.py


async def _reset_user(sess_or_async, user_id: int) -> None:
    """
    Reset the seeded user row back to the original values.
    Works for both AsyncSession and sync Session.
    """
    params = {
        "id": user_id,  # <-- include id!
        "n": USER_NAME,
        "s": USER_STATE,
        "a": json.dumps(USER_ATTRS),  # <-- plain JSON string value, not sa.text(...)
    }
    stmt = sa.text("UPDATE users SET name=:n, state=:s, attrs=:a WHERE id=:id")

    if isinstance(sess_or_async, AsyncSession):
        await sess_or_async.execute(stmt, params)
        await sess_or_async.commit()
    else:
        sess_or_async.execute(stmt, params)
        sess_or_async.commit()


@pytest.mark.parametrize("setup_test_environment", ["async", "sync"], indirect=True)
@pytest.mark.asyncio
async def test_db_operation_with_full_setup_success(setup_test_environment):
    ids, sess_or_async, _runner = setup_test_environment
    user_id = ids["user_id"]
    await _reset_user(sess_or_async, user_id)

    rows = await execute_query(sess_or_async, "SELECT * FROM users WHERE id = :id", user_id)
    assert rows and len(rows) == 1
    rec = rows[0]
    assert rec["id"] == user_id
    assert rec["name"] == USER_NAME
    assert rec["state"] == USER_STATE
    assert json.loads(rec["attrs"]) == USER_ATTRS


@pytest.mark.parametrize("setup_test_environment", ["async"], indirect=True)
@pytest.mark.asyncio
async def test_db_operation_custom_row_factory(setup_test_environment):
    ids, async_sess, runner = setup_test_environment
    user_id = ids["user_id"]
    await _reset_user(async_sess, user_id)
    assert isinstance(async_sess, AsyncSession)

    async def custom_fn(s: AsyncSession):
        res = await s.execute(
            sa.text("SELECT id, state FROM users WHERE id = :id"), {"id": user_id}
        )
        rows = res.all()
        return [{"user_id": r[0], "status": r[1]} for r in rows]

    result = await runner.run_async(async_sess, custom_fn, name="custom-row-factory")
    assert result and len(result) == 1
    assert result[0]["user_id"] == user_id
    assert result[0]["status"] == USER_STATE


@pytest.mark.parametrize("setup_test_environment", ["sync", "async"], indirect=True)
@pytest.mark.asyncio
async def test_db_operation_with_default_return(setup_test_environment):
    _ids, sess_or_async, runner = setup_test_environment
    if isinstance(sess_or_async, AsyncSession):

        async def faulty(s: AsyncSession):
            await s.execute(sa.text("SELECT * FROM non_existent_table"))

        default_value = []
        result = await runner.run_async(
            sess_or_async, faulty, name="expected-fault", raises=False, default=default_value
        )
        assert result == default_value
    else:

        def faulty(s):
            s.execute(sa.text("SELECT * FROM non_existent_table"))

        default_value = []
        result = runner.run(
            sess_or_async, faulty, name="expected-fault", raises=False, default=default_value
        )
        assert result == default_value


@pytest.mark.parametrize("setup_test_environment", ["async"], indirect=True)
@pytest.mark.asyncio
async def test_db_operation_exception_handling(setup_test_environment):
    _ids, async_sess, runner = setup_test_environment

    async def faulty(s: AsyncSession):
        await s.execute(sa.text("SELECT * FROM non_existent_table"))

    with pytest.raises(sa.exc.DBAPIError):
        await runner.run_async(async_sess, faulty, name="exception-expected")


@pytest.mark.parametrize("setup_test_environment", ["async"], indirect=True)
@pytest.mark.asyncio
async def test_retry_then_success_async(setup_test_environment, caplog):
    _ids, async_sess, runner = setup_test_environment
    runner.max_retries = 1
    calls = {"n": 0}

    async def op(s: AsyncSession):
        calls["n"] += 1
        if calls["n"] == 1:
            # simulate transient
            raise sa.exc.OperationalError("database is locked", None, None)
        await s.execute(sa.text("SELECT 1"))

    with caplog.at_level("WARNING"):
        await runner.run_async(async_sess, op, name="retry-once")
    assert calls["n"] == 2
    assert any("retry-once failed" in r.message for r in caplog.records)


@pytest.mark.parametrize("setup_test_environment", ["sync"], indirect=True)
@pytest.mark.asyncio
async def test_retry_then_success_sync(setup_test_environment, caplog):
    _ids, sess, runner = setup_test_environment
    runner.max_retries = 1
    calls = {"n": 0}

    def op(s):
        calls["n"] += 1
        if calls["n"] == 1:
            raise sa.exc.OperationalError("database is locked", None, None)
        s.execute(sa.text("SELECT 1"))

    with caplog.at_level("WARNING"):
        runner.run(sess, op, name="retry-once-sync")
    assert calls["n"] == 2
    assert any("retry-once-sync failed" in r.message for r in caplog.records)


@pytest.mark.parametrize("setup_test_environment", ["async"], indirect=True)
@pytest.mark.asyncio
async def test_savepoint_isolates_step_failures_async(setup_test_environment):
    _ids, s, runner = setup_test_environment
    runner.max_retries = 1

    async with s.begin():

        async def step_a(sess):
            await sess.execute(sa.text("UPDATE users SET state='A' WHERE id=1"))

        await runner.run_async(s, step_a, name="step-a")

        tries = {"n": 0}

        async def step_b(sess):
            tries["n"] += 1
            if tries["n"] == 1:
                raise sa.exc.OperationalError("transient", None, None)
            await sess.execute(sa.text("UPDATE users SET name='OK' WHERE id=1"))

        await runner.run_async(s, step_b, name="step-b")

    res = await s.execute(sa.text("SELECT state, name FROM users WHERE id=1"))
    assert res.first() == ("A", "OK")


@pytest.mark.parametrize("setup_test_environment", ["sync"], indirect=True)
@pytest.mark.asyncio
async def test_read_only_path_sync(setup_test_environment):
    _ids, sess, runner = setup_test_environment
    val = runner.run(
        sess, lambda ss: ss.execute(sa.text("SELECT 1")).scalar(), name="ro", read_only=True
    )
    assert val == 1


@pytest.mark.parametrize("setup_test_environment", ["sync", "async"], indirect=True)
@pytest.mark.asyncio
async def test_timeout_args_do_not_crash(setup_test_environment):
    _ids, s, runner = setup_test_environment
    if isinstance(s, AsyncSession):

        async def op(sess):
            await sess.execute(sa.text("SELECT 1"))

        await runner.run_async(s, op, name="t", lock_timeout_s=1, stmt_timeout_s=2)
    else:

        def op(sess):
            sess.execute(sa.text("SELECT 1"))

        runner.run(s, op, name="t", lock_timeout_s=1, stmt_timeout_s=2)


@pytest.mark.parametrize("setup_test_environment", ["sync"], indirect=True)
@pytest.mark.asyncio
async def test_default_return_and_logging_sync(setup_test_environment, caplog):
    _ids, sess, runner = setup_test_environment

    def faulty(s):
        s.execute(sa.text("SELECT * FROM does_not_exist"))

    with caplog.at_level("WARNING"):
        result = runner.run(sess, faulty, name="expected-fault", raises=False, default=["x"])
    assert result == ["x"]
    assert any("expected-fault failed" in r.message for r in caplog.records)


@pytest.mark.parametrize("setup_test_environment", ["sync"], indirect=True)
@pytest.mark.asyncio
async def test_non_transient_error_logs_error_sync(setup_test_environment, caplog):
    _ids, sess, runner = setup_test_environment

    def boom(_: Session):
        raise ValueError("boom")  # non-DBAPIError => non-transient

    with caplog.at_level("ERROR"):
        out = runner.run(sess, boom, name="non-transient", raises=False, default=None)
    assert out is None
    assert any("non-transient failed" in r.message for r in caplog.records)


@pytest.mark.parametrize("setup_test_environment", ["async"], indirect=True)
@pytest.mark.asyncio
async def test_non_transient_error_logs_error_async(setup_test_environment, caplog):
    _ids, s, runner = setup_test_environment

    async def boom(_: AsyncSession):
        raise ValueError("boom")

    with caplog.at_level("ERROR"):
        out = await runner.run_async(
            s, boom, name="non-transient-async", raises=False, default=None
        )
    assert out is None
    assert any("non-transient-async failed" in r.message for r in caplog.records)
