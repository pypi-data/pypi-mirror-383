"""
Unit tests for shared utilities in transactional tracing execution.

Covers:
- prepare_transaction_context
- finalize_success / finalize_error
- call_with_optional_tid_sync / call_with_optional_tid_async
"""

from unittest.mock import MagicMock
import pytest

from bisslog.use_cases.use_case_decorator import utils


def test_prepare_transaction_context_trace_enabled_without_inbound_tid():
    """
    When tracing is enabled and there is no inbound transaction_id in kwargs:
    - A new transaction_id must be created.
    - opener.start must be called with *args and component/keyname.
    - super_transaction_id must equal the created transaction_id.
    - kwargs must be forwarded to start without transaction_id.
    """
    # Arrange
    args = ("a1", "a2")
    kwargs = {"x": 1, "y": 2}
    keyname = "my-key"

    tracing_opener = MagicMock()
    transaction_manager = MagicMock()
    transaction_manager.create_transaction_id.return_value = "tid-123"

    # Act
    super_tid, tid = utils.prepare_transaction_context(
        args=args,
        kwargs=kwargs,
        keyname=keyname,
        do_trace=True,
        _tracing_opener=tracing_opener,
        _transaction_manager=transaction_manager,
    )

    # Assert
    transaction_manager.create_transaction_id.assert_called_once_with(keyname)
    # opener.start must be called with the same positional args
    start_args, start_kwargs = tracing_opener.start.call_args
    assert start_args == args
    assert start_kwargs["component"] == keyname
    assert start_kwargs["transaction_id"] == "tid-123"
    assert start_kwargs["super_transaction_id"] is None
    # Forwarded kwargs are preserved
    assert start_kwargs["x"] == 1
    assert start_kwargs["y"] == 2

    # super == tid when inbound is None and do_trace=True
    assert super_tid == "tid-123"
    assert tid == "tid-123"

    # Original kwargs dict remains without 'transaction_id' key (it was not present)
    assert "transaction_id" not in kwargs


def test_prepare_transaction_context_trace_enabled_with_inbound_tid():
    """
    When tracing is enabled and kwargs includes an inbound transaction_id:
    - The inbound value is popped (not forwarded in **kwargs).
    - A new transaction_id is created for this component.
    - opener.start is called with super_transaction_id=inbound and the new transaction_id.
    - Returned (super, tid) are (inbound, created).
    """
    args = ("only-positional",)
    kwargs = {"x": 1, "transaction_id": "sup-999", "y": 2}
    keyname = "another-key"

    tracing_opener = MagicMock()
    transaction_manager = MagicMock()
    transaction_manager.create_transaction_id.return_value = "tid-new"

    super_tid, tid = utils.prepare_transaction_context(
        args=args,
        kwargs=kwargs,
        keyname=keyname,
        do_trace=True,
        _tracing_opener=tracing_opener,
        _transaction_manager=transaction_manager,
    )

    # inbound was popped out from kwargs before forwarding
    start_args, start_kwargs = tracing_opener.start.call_args
    assert start_args == args
    assert "transaction_id" not in kwargs  # popped from source dict
    assert "transaction_id" in start_kwargs  # injected param for tracing
    assert start_kwargs["transaction_id"] == "tid-new"
    assert start_kwargs["super_transaction_id"] == "sup-999"
    assert start_kwargs["component"] == keyname
    assert start_kwargs["x"] == 1
    assert start_kwargs["y"] == 2

    assert super_tid == "sup-999"
    assert tid == "tid-new"


def test_prepare_transaction_context_trace_disabled_without_inbound_tid():
    """
    When tracing is disabled and inbound transaction_id does not exist:
    - No calls to create_transaction_id or opener.start.
    - Returns (None, None).
    """
    args = ()
    kwargs = {"foo": "bar"}
    keyname = "no-trace-key"

    tracing_opener = MagicMock()
    transaction_manager = MagicMock()

    super_tid, tid = utils.prepare_transaction_context(
        args=args,
        kwargs=kwargs,
        keyname=keyname,
        do_trace=False,
        _tracing_opener=tracing_opener,
        _transaction_manager=transaction_manager,
    )

    transaction_manager.create_transaction_id.assert_not_called()
    tracing_opener.start.assert_not_called()
    assert super_tid is None and tid is None
    assert kwargs == {"foo": "bar"}  # unchanged


def test_prepare_transaction_context_trace_disabled_with_inbound_tid():
    """
    When tracing is disabled and inbound transaction_id exists:
    - The inbound value is popped from kwargs.
    - No tracing calls are made.
    - Returns (inbound, inbound).
    """
    args = ()
    kwargs = {"transaction_id": "sup-1", "foo": "bar"}

    tracing_opener = MagicMock()
    transaction_manager = MagicMock()

    super_tid, tid = utils.prepare_transaction_context(
        args=args,
        kwargs=kwargs,
        keyname="ignored-when-no-trace",
        do_trace=False,
        _tracing_opener=tracing_opener,
        _transaction_manager=transaction_manager,
    )

    transaction_manager.create_transaction_id.assert_not_called()
    tracing_opener.start.assert_not_called()
    assert super_tid == "sup-1"
    assert tid == "sup-1"
    assert "transaction_id" not in kwargs
    assert kwargs["foo"] == "bar"


def test_finalize_success_with_trace_enabled():
    """
    finalize_success should call opener.end and then transaction_manager.close_transaction
    when tracing is enabled.
    """
    tracing_opener = MagicMock()
    transaction_manager = MagicMock()

    utils.finalize_success(
        do_trace=True,
        keyname="k",
        transaction_id="tid-1",
        super_transaction_id="sup-1",
        result={"ok": True},
        _tracing_opener=tracing_opener,
        _transaction_manager=transaction_manager,
    )

    # end first, then close
    tracing_opener.end.assert_called_once()
    transaction_manager.close_transaction.assert_called_once()

    end_args, end_kwargs = tracing_opener.end.call_args
    assert end_args == ()
    assert end_kwargs["transaction_id"] == "tid-1"
    assert end_kwargs["component"] == "k"
    assert end_kwargs["super_transaction_id"] == "sup-1"
    assert end_kwargs["result"] == {"ok": True}


def test_finalize_success_with_trace_disabled():
    """
    finalize_success should be a no-op when tracing is disabled.
    """
    tracing_opener = MagicMock()
    transaction_manager = MagicMock()

    utils.finalize_success(
        do_trace=False,
        keyname="k",
        transaction_id="tid-1",
        super_transaction_id="sup-1",
        result="ignored",
        _tracing_opener=tracing_opener,
        _transaction_manager=transaction_manager,
    )

    tracing_opener.end.assert_not_called()
    transaction_manager.close_transaction.assert_not_called()


def test_finalize_error_with_trace_enabled():
    """
    finalize_error should call opener.end and close_transaction when tracing is enabled,
    forwarding the error object as the result.
    """
    tracing_opener = MagicMock()
    transaction_manager = MagicMock()

    err = RuntimeError("boom")
    utils.finalize_error(
        do_trace=True,
        keyname="k",
        transaction_id="tid-err",
        super_transaction_id="sup-err",
        error=err,
        _tracing_opener=tracing_opener,
        _transaction_manager=transaction_manager,
    )

    tracing_opener.end.assert_called_once()
    transaction_manager.close_transaction.assert_called_once()

    _, end_kwargs = tracing_opener.end.call_args
    assert end_kwargs["transaction_id"] == "tid-err"
    assert end_kwargs["component"] == "k"
    assert end_kwargs["super_transaction_id"] == "sup-err"
    assert end_kwargs["result"] is err


def test_finalize_error_with_trace_disabled():
    """
    finalize_error should be a no-op when tracing is disabled.
    """
    tracing_opener = MagicMock()
    transaction_manager = MagicMock()

    utils.finalize_error(
        do_trace=False,
        keyname="k",
        transaction_id="tid-err",
        super_transaction_id="sup-err",
        error=ValueError("nope"),
        _tracing_opener=tracing_opener,
        _transaction_manager=transaction_manager,
    )

    tracing_opener.end.assert_not_called()
    transaction_manager.close_transaction.assert_not_called()


def test_call_with_optional_tid_sync_injects_when_flag_true():
    """
    call_with_optional_tid_sync should inject transaction_id into kwargs when
    accepts_transaction_id=True.
    """
    captured = {}

    def fn(a, *, transaction_id=None, **kw):
        captured["a"] = a
        captured["tid"] = transaction_id
        captured["kw"] = kw
        return "ok"

    result = utils.call_with_optional_tid_sync(
        fn,
        args=(7,),
        kwargs={"x": 1},
        transaction_id="tid-777",
        accepts_transaction_id=True,
    )

    assert result == "ok"
    assert captured == {"a": 7, "tid": "tid-777", "kw": {"x": 1}}


def test_call_with_optional_tid_sync_does_not_inject_when_flag_false():
    """
    call_with_optional_tid_sync should not inject transaction_id when
    accepts_transaction_id=False.
    """
    captured = {}

    def fn(a, **kw):
        captured["a"] = a
        captured["kw"] = kw
        return "ok"

    result = utils.call_with_optional_tid_sync(
        fn,
        args=(5,),
        kwargs={"x": 1},
        transaction_id="tid-ignored",
        accepts_transaction_id=False,
    )

    assert result == "ok"
    assert captured == {"a": 5, "kw": {"x": 1}}


@pytest.mark.asyncio
async def test_call_with_optional_tid_async_injects_when_flag_true():
    """
    call_with_optional_tid_async should await the function and inject transaction_id
    when accepts_transaction_id=True.
    """
    captured = {}

    async def fn(a, *, transaction_id=None, **kw):
        captured["a"] = a
        captured["tid"] = transaction_id
        captured["kw"] = kw
        return "ok-async"

    result = await utils.call_with_optional_tid_async(
        fn,
        args=(1,),
        kwargs={"foo": "bar"},
        transaction_id="tid-abc",
        accepts_transaction_id=True,
    )

    assert result == "ok-async"
    assert captured == {"a": 1, "tid": "tid-abc", "kw": {"foo": "bar"}}


@pytest.mark.asyncio
async def test_call_with_optional_tid_async_does_not_inject_when_flag_false():
    """
    call_with_optional_tid_async should await the function without injecting
    transaction_id when accepts_transaction_id=False.
    """
    captured = {}

    async def fn(a, **kw):
        captured["a"] = a
        captured["kw"] = kw
        return "ok-async"

    result = await utils.call_with_optional_tid_async(
        fn,
        args=(2,),
        kwargs={"foo": "bar"},
        transaction_id="tid-ignored",
        accepts_transaction_id=False,
    )

    assert result == "ok-async"
    assert captured == {"a": 2, "kw": {"foo": "bar"}}
