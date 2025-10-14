"""
Unit tests for run_with_trace_async.

Covers:
- Success path: prepare -> call_with_optional_tid_async -> finalize_success.
- Error path: prepare -> call_with_optional_tid_async raises -> finalize_error + re-raise.
- Forwarding of args/kwargs/flags and identity of kwargs.
- do_trace=False is forwarded to finalizers.
"""

from unittest.mock import MagicMock, AsyncMock
import pytest

# Adjust this import if the path differs in your project
import bisslog.use_cases.use_case_decorator.run_with_trace_async as rta_mod

run_with_trace_async = rta_mod.run_with_trace_async


@pytest.mark.asyncio
async def test_run_with_trace_async_success(monkeypatch):
    """
    When the wrapped async call succeeds:
    - prepare_transaction_context is called with the correct args.
    - call_with_optional_tid_async is awaited with the transaction_id from prepare.
    - finalize_success is called with the result and IDs from prepare.
    - The function returns the result from call_with_optional_tid_async.
    """
    # Arrange
    args = ("p1", 2)
    kwargs = {"x": 1, "y": 2}
    keyname = "UC-key"
    do_trace = True
    accepts_tid = True

    # Mocks for utils
    mock_prepare = MagicMock(return_value=("sup-1", "tid-1"))
    mock_call_async = AsyncMock(return_value="OK")
    mock_finalize_success = MagicMock()
    mock_finalize_error = MagicMock()

    # Inject into the function's globals to avoid aliasing issues
    monkeypatch.setitem(run_with_trace_async.__globals__, "prepare_transaction_context", mock_prepare)
    monkeypatch.setitem(run_with_trace_async.__globals__, "call_with_optional_tid_async", mock_call_async)
    monkeypatch.setitem(run_with_trace_async.__globals__, "finalize_success", mock_finalize_success)
    monkeypatch.setitem(run_with_trace_async.__globals__, "finalize_error", mock_finalize_error)

    # Tracing infra objects (passed through)
    tracing_opener = MagicMock()
    tx_manager = MagicMock()

    async def dummy_fn(*a, **k):
        return "IGNORED"

    # Act
    result = await run_with_trace_async(
        dummy_fn,
        args=args,
        kwargs=kwargs,
        keyname=keyname,
        do_trace=do_trace,
        _tracing_opener=tracing_opener,
        _transaction_manager=tx_manager,
        _accepts_transaction_id=accepts_tid,
    )

    # Assert return value
    assert result == "OK"

    # prepare_transaction_context received the exact args
    mock_prepare.assert_called_once()
    p_args, p_kwargs = mock_prepare.call_args
    assert p_args == ()
    assert p_kwargs["args"] == args
    assert p_kwargs["kwargs"] is kwargs  # same dict object (identity)
    assert p_kwargs["keyname"] == keyname
    assert p_kwargs["do_trace"] is True
    assert p_kwargs["_tracing_opener"] is tracing_opener
    assert p_kwargs["_transaction_manager"] is tx_manager

    # call_with_optional_tid_async awaited with transaction_id from prepare
    c_args, c_kwargs = mock_call_async.call_args
    assert c_args == (dummy_fn,)
    assert c_kwargs["args"] == args
    assert c_kwargs["kwargs"] is kwargs  # identity preserved
    assert c_kwargs["transaction_id"] == "tid-1"
    assert c_kwargs["accepts_transaction_id"] is True

    # finalize_success called with correct IDs and result
    mock_finalize_success.assert_called_once()
    f_args, f_kwargs = mock_finalize_success.call_args
    assert f_kwargs["do_trace"] is True
    assert f_kwargs["keyname"] == keyname
    assert f_kwargs["transaction_id"] == "tid-1"
    assert f_kwargs["super_transaction_id"] == "sup-1"
    assert f_kwargs["result"] == "OK"
    assert f_kwargs["_tracing_opener"] is tracing_opener
    assert f_kwargs["_transaction_manager"] is tx_manager

    # finalize_error must not be called
    mock_finalize_error.assert_not_called()


@pytest.mark.asyncio
async def test_run_with_trace_async_error(monkeypatch):
    """
    When the wrapped async call raises:
    - finalize_error is called with the exception and IDs from prepare.
    - The exception is re-raised.
    - finalize_success is not called.
    """
    args = ()
    kwargs = {}
    keyname = "Err-UC"
    do_trace = True
    accepts_tid = False

    mock_prepare = MagicMock(return_value=("superX", "tidX"))
    boom = ValueError("boom")
    mock_call_async = AsyncMock(side_effect=boom)
    mock_finalize_success = MagicMock()
    mock_finalize_error = MagicMock()

    monkeypatch.setitem(run_with_trace_async.__globals__, "prepare_transaction_context", mock_prepare)
    monkeypatch.setitem(run_with_trace_async.__globals__, "call_with_optional_tid_async", mock_call_async)
    monkeypatch.setitem(run_with_trace_async.__globals__, "finalize_success", mock_finalize_success)
    monkeypatch.setitem(run_with_trace_async.__globals__, "finalize_error", mock_finalize_error)

    tracing_opener = MagicMock()
    tx_manager = MagicMock()

    async def failing_fn():
        raise AssertionError("should not be called directly")

    with pytest.raises(ValueError) as excinfo:
        await run_with_trace_async(
            failing_fn,
            args=args,
            kwargs=kwargs,
            keyname=keyname,
            do_trace=do_trace,
            _tracing_opener=tracing_opener,
            _transaction_manager=tx_manager,
            _accepts_transaction_id=accepts_tid,
        )
    assert str(excinfo.value) == "boom"

    # finalize_error called with the original exception
    mock_finalize_error.assert_called_once()
    e_args, e_kwargs = mock_finalize_error.call_args
    assert e_kwargs["do_trace"] is True
    assert e_kwargs["keyname"] == keyname
    assert e_kwargs["transaction_id"] == "tidX"
    assert e_kwargs["super_transaction_id"] == "superX"
    assert e_kwargs["error"] is boom
    assert e_kwargs["_tracing_opener"] is tracing_opener
    assert e_kwargs["_transaction_manager"] is tx_manager

    # finalize_success not called
    mock_finalize_success.assert_not_called()


@pytest.mark.asyncio
async def test_run_with_trace_async_forwards_do_trace_false(monkeypatch):
    """
    Ensure the do_trace flag is forwarded to finalize_success when False.
    (The actual no-op behavior is responsibility of the finalizer itself.)
    """
    args = ("a",)
    kwargs = {"k": "v"}
    keyname = "NoTrace"
    do_trace = False
    accepts_tid = True

    mock_prepare = MagicMock(return_value=(None, None))
    mock_call_async = AsyncMock(return_value="RES")
    mock_finalize_success = MagicMock()
    mock_finalize_error = MagicMock()

    monkeypatch.setitem(run_with_trace_async.__globals__, "prepare_transaction_context", mock_prepare)
    monkeypatch.setitem(run_with_trace_async.__globals__, "call_with_optional_tid_async", mock_call_async)
    monkeypatch.setitem(run_with_trace_async.__globals__, "finalize_success", mock_finalize_success)
    monkeypatch.setitem(run_with_trace_async.__globals__, "finalize_error", mock_finalize_error)

    tracing_opener = MagicMock()
    tx_manager = MagicMock()

    async def fn(a, k=None):
        return "IGNORED"

    res = await run_with_trace_async(
        fn,
        args=args,
        kwargs=kwargs,
        keyname=keyname,
        do_trace=do_trace,
        _tracing_opener=tracing_opener,
        _transaction_manager=tx_manager,
        _accepts_transaction_id=accepts_tid,
    )
    assert res == "RES"

    # finalize_success receives do_trace=False
    mock_finalize_success.assert_called_once()
    _, f_kwargs = mock_finalize_success.call_args
    assert f_kwargs["do_trace"] is False
    assert f_kwargs["keyname"] == keyname
    assert f_kwargs["transaction_id"] is None
    assert f_kwargs["super_transaction_id"] is None
    assert f_kwargs["result"] == "RES"
    assert f_kwargs["_tracing_opener"] is tracing_opener
    assert f_kwargs["_transaction_manager"] is tx_manager

    # No error finalization
    mock_finalize_error.assert_not_called()

    # call was awaited with accepts flag forwarded
    c_args, c_kwargs = mock_call_async.call_args
    assert c_args == (fn,)
    assert c_kwargs["accepts_transaction_id"] is True
    assert c_kwargs["transaction_id"] is None
    assert c_kwargs["args"] == args
    assert c_kwargs["kwargs"] is kwargs  # identity preserved
