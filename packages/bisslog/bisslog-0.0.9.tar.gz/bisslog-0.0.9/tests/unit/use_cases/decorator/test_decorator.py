"""Unit tests for the @use_case decorator."""
import sys
import importlib
from unittest.mock import MagicMock, AsyncMock
import pytest

import bisslog.use_cases.use_case_decorator as uc_mod

use_case_decorator = uc_mod.use_case


def import_fallback_use_case(monkeypatch):
    import bisslog.typing_compat as typing_compat

    monkeypatch.setattr(typing_compat, "ParamSpec", None, raising=True)

    sys.modules.pop("bisslog.use_cases.use_case_decorator.decorator", None)

    dec_mod = importlib.import_module("bisslog.use_cases.use_case_decorator.decorator")

    assert dec_mod.ParamSpec is None

    return dec_mod, dec_mod.use_case


@pytest.mark.asyncio
async def test_async_wrapper_calls_run_with_trace_async_with_params(monkeypatch):
    prepared_key = "prepared-key"
    accepts_tid = True

    mock_prepare = MagicMock(return_value=(prepared_key, accepts_tid))
    mock_runner_async = AsyncMock(return_value="async-result")
    mock_runner_sync = MagicMock()

    monkeypatch.setitem(use_case_decorator.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_async", mock_runner_async)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_sync", mock_runner_sync)

    @use_case_decorator
    async def my_async(a, b, *, kw=None):
        """original async doc"""
        return a + b

    result = await my_async(1, 2, kw="x")
    assert result == "async-result"

    mock_prepare.assert_called_once()
    args, kwargs = mock_prepare.call_args
    assert args[1] is None   # keyname default
    assert args[2] is True   # do_trace default

    mock_runner_async.assert_awaited_once()
    r_args, r_kwargs = mock_runner_async.call_args
    assert callable(r_args[0])          # fn
    assert isinstance(r_args[1], tuple) # args tuple
    assert isinstance(r_args[2], dict)  # kwargs dict
    assert r_args[3] == prepared_key
    assert r_args[4] is True
    assert "_tracing_opener" in r_kwargs
    assert "_transaction_manager" in r_kwargs
    assert r_kwargs["_accepts_transaction_id"] is accepts_tid

    mock_runner_sync.assert_not_called()
    assert my_async.__name__ == "my_async"
    assert my_async.__doc__ == "original async doc"


def test_sync_wrapper_calls_run_with_trace_sync_with_params(monkeypatch):
    prepared_key = "prepared-key-sync"
    accepts_tid = False

    mock_prepare = MagicMock(return_value=(prepared_key, accepts_tid))
    mock_runner_sync = MagicMock(return_value="sync-result")
    mock_runner_async = AsyncMock()

    monkeypatch.setitem(use_case_decorator.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_sync", mock_runner_sync)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_async", mock_runner_async)

    @use_case_decorator
    def my_sync(a, b, *, kw=None):
        """original sync doc"""
        return a + b

    result = my_sync(10, 5, kw="zzz")
    assert result == "sync-result"

    mock_prepare.assert_called_once()
    args, kwargs = mock_prepare.call_args
    assert args[1] is None
    assert args[2] is True

    mock_runner_sync.assert_called_once()
    r_args, r_kwargs = mock_runner_sync.call_args
    assert callable(r_args[0])
    assert isinstance(r_args[1], tuple)
    assert isinstance(r_args[2], dict)
    assert r_args[3] == prepared_key
    assert r_args[4] is True
    assert r_kwargs["_accepts_transaction_id"] is accepts_tid

    mock_runner_async.assert_not_called()
    assert my_sync.__name__ == "my_sync"
    assert my_sync.__doc__ == "original sync doc"


def test_with_parentheses_overrides_keyname_and_do_trace_with_params(monkeypatch):
    prepared_key = "prepared-key-custom"
    accepts_tid = True

    mock_prepare = MagicMock(return_value=(prepared_key, accepts_tid))
    mock_runner_sync = MagicMock(return_value="ok")

    monkeypatch.setitem(use_case_decorator.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_sync", mock_runner_sync)

    @use_case_decorator(keyname="custom", do_trace=False)
    def my_sync(a):
        return a

    _ = my_sync(123)

    mock_prepare.assert_called_once()
    args, kwargs = mock_prepare.call_args
    assert args[1] == "custom"
    assert args[2] is False

    r_args, r_kwargs = mock_runner_sync.call_args
    assert r_args[3] == prepared_key
    assert r_args[4] is False
    assert r_kwargs["_accepts_transaction_id"] is accepts_tid


@pytest.mark.asyncio
async def test_async_with_parentheses_and_accepts_tid_passthrough_with_params(monkeypatch):
    prepared_key = "k-async"
    accepts_tid = False

    mock_prepare = MagicMock(return_value=(prepared_key, accepts_tid))
    mock_runner_async = AsyncMock(return_value="value")

    monkeypatch.setitem(use_case_decorator.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_async", mock_runner_async)

    @use_case_decorator(keyname=None, do_trace=True)
    async def my_async(a, b):
        return a + b

    res = await my_async(3, 4)
    assert res == "value"

    r_args, r_kwargs = mock_runner_async.call_args
    assert r_args[3] == prepared_key
    assert r_args[4] is True
    assert r_kwargs["_accepts_transaction_id"] is accepts_tid


def test_prepare_function_receives_original_fn_reference_with_params(monkeypatch):
    marker = object()
    captured_fn = {"fn": None}

    def _capture(fn, keyname, do_trace):
        captured_fn["fn"] = fn
        return ("k", False)

    mock_prepare = MagicMock(side_effect=_capture)
    mock_runner_sync = MagicMock(return_value="ok")

    monkeypatch.setitem(use_case_decorator.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_sync", mock_runner_sync)

    def my_sync(a):
        return a

    my_sync._marker = marker

    decorated = use_case_decorator(my_sync)
    _ = decorated(1)

    assert getattr(captured_fn["fn"], "_marker", None) is marker


def test_wrapper_passes_through_args_and_kwargs_with_params(monkeypatch):
    mock_prepare = MagicMock(return_value=("k", False))
    mock_runner_sync = MagicMock(return_value="ok")

    monkeypatch.setitem(use_case_decorator.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_sync", mock_runner_sync)

    @use_case_decorator
    def f(a, b, *, c=None, **kw):
        return (a, b, c, kw)

    _ = f(1, 2, c=3, d=4, e=5)

    assert mock_runner_sync.called
    r_args, r_kwargs = mock_runner_sync.call_args
    assert r_args[1] == (1, 2)
    assert r_args[2]["c"] == 3
    assert r_args[2]["d"] == 4
    assert r_args[2]["e"] == 5


def test_decorator_returns_function_when_called_without_parens_with_params(monkeypatch):
    mock_prepare = MagicMock(return_value=("k", False))
    mock_runner_sync = MagicMock(return_value="X")

    monkeypatch.setitem(use_case_decorator.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_sync", mock_runner_sync)

    @use_case_decorator
    def g(x):
        return x

    assert g(7) == "X"


def test_decorator_factory_returns_decorator_when_called_with_parens_with_params(monkeypatch):
    mock_prepare = MagicMock(return_value=("k", False))
    mock_runner_sync = MagicMock(return_value="Y")

    monkeypatch.setitem(use_case_decorator.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_sync", mock_runner_sync)

    dec = use_case_decorator(keyname="k2", do_trace=False)
    assert callable(dec)

    @dec
    def h(y):
        return y

    assert h(9) == "Y"
    args, kwargs = mock_prepare.call_args
    assert args[1] == "k2"
    assert args[2] is False


@pytest.mark.asyncio
async def test_async_wrapper_calls_run_with_trace_async_with_params(monkeypatch):
    prepared_key = "prepared-key"
    accepts_tid = True

    mock_prepare = MagicMock(return_value=(prepared_key, accepts_tid))
    mock_runner_async = AsyncMock(return_value="async-result")
    mock_runner_sync = MagicMock()

    monkeypatch.setitem(use_case_decorator.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_async", mock_runner_async)
    monkeypatch.setitem(use_case_decorator.__globals__, "run_with_trace_sync", mock_runner_sync)

    @use_case_decorator
    async def my_async(a, b, *, kw=None):
        """original async doc"""
        return a + b

    result = await my_async(1, 2, kw="x")
    assert result == "async-result"

    mock_prepare.assert_called_once()
    args, kwargs = mock_prepare.call_args
    assert args[1] is None   # keyname default
    assert args[2] is True   # do_trace default

    mock_runner_async.assert_awaited_once()
    r_args, r_kwargs = mock_runner_async.call_args
    assert callable(r_args[0])          # fn
    assert isinstance(r_args[1], tuple) # args tuple
    assert isinstance(r_args[2], dict)  # kwargs dict
    assert r_args[3] == prepared_key
    assert r_args[4] is True
    assert "_tracing_opener" in r_kwargs
    assert "_transaction_manager" in r_kwargs
    assert r_kwargs["_accepts_transaction_id"] is accepts_tid

    mock_runner_sync.assert_not_called()
    assert my_async.__name__ == "my_async"
    assert my_async.__doc__ == "original async doc"




def test_sync_wrapper_calls_run_with_trace_sync_without_params(monkeypatch):
    prepared_key = "prepared-key-sync"
    accepts_tid = False

    dec_mod, use_case = import_fallback_use_case(monkeypatch)
    mock_prepare = MagicMock(return_value=(prepared_key, accepts_tid))
    mock_runner_sync = MagicMock(return_value="sync-result")
    mock_runner_async = AsyncMock()

    monkeypatch.setitem(use_case.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case.__globals__, "run_with_trace_sync", mock_runner_sync)
    monkeypatch.setitem(use_case.__globals__, "run_with_trace_async", mock_runner_async)

    @use_case
    def my_sync(a, b, *, kw=None):
        """original sync doc"""
        return a + b

    result = my_sync(10, 5, kw="zzz")
    assert result == "sync-result"

    mock_prepare.assert_called_once()
    args, kwargs = mock_prepare.call_args
    assert args[1] is None
    assert args[2] is True

    mock_runner_sync.assert_called_once()
    r_args, r_kwargs = mock_runner_sync.call_args
    assert callable(r_args[0])
    assert isinstance(r_args[1], tuple)
    assert isinstance(r_args[2], dict)
    assert r_args[3] == prepared_key
    assert r_args[4] is True
    assert r_kwargs["_accepts_transaction_id"] is accepts_tid

    mock_runner_async.assert_not_called()
    assert my_sync.__name__ == "my_sync"
    assert my_sync.__doc__ == "original sync doc"


def test_with_parentheses_overrides_keyname_and_do_trace_without_params(monkeypatch):
    dec_mod, use_case = import_fallback_use_case(monkeypatch)
    prepared_key = "prepared-key-custom"
    accepts_tid = True

    mock_prepare = MagicMock(return_value=(prepared_key, accepts_tid))
    mock_runner_sync = MagicMock(return_value="ok")

    monkeypatch.setitem(use_case.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case.__globals__, "run_with_trace_sync", mock_runner_sync)

    @use_case(keyname="custom", do_trace=False)
    def my_sync(a):
        return a

    _ = my_sync(123)

    mock_prepare.assert_called_once()
    args, kwargs = mock_prepare.call_args
    assert args[1] == "custom"
    assert args[2] is False

    r_args, r_kwargs = mock_runner_sync.call_args
    assert r_args[3] == prepared_key
    assert r_args[4] is False
    assert r_kwargs["_accepts_transaction_id"] is accepts_tid


@pytest.mark.asyncio
async def test_async_with_parentheses_and_accepts_tid_passthrough_without_params(monkeypatch):
    prepared_key = "k-async"
    accepts_tid = False
    dec_mod, use_case = import_fallback_use_case(monkeypatch)

    mock_prepare = MagicMock(return_value=(prepared_key, accepts_tid))
    mock_runner_async = AsyncMock(return_value="value")

    monkeypatch.setitem(use_case.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case.__globals__, "run_with_trace_async", mock_runner_async)

    @use_case(keyname=None, do_trace=True)
    async def my_async(a, b):
        return a + b

    res = await my_async(3, 4)
    assert res == "value"

    r_args, r_kwargs = mock_runner_async.call_args
    assert r_args[3] == prepared_key
    assert r_args[4] is True
    assert r_kwargs["_accepts_transaction_id"] is accepts_tid


def test_prepare_function_receives_original_fn_reference_without_params(monkeypatch):
    marker = object()
    captured_fn = {"fn": None}
    dec_mod, use_case = import_fallback_use_case(monkeypatch)

    def _capture(fn, keyname, do_trace):
        captured_fn["fn"] = fn
        return ("k", False)

    mock_prepare = MagicMock(side_effect=_capture)
    mock_runner_sync = MagicMock(return_value="ok")

    monkeypatch.setitem(use_case.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case.__globals__, "run_with_trace_sync", mock_runner_sync)

    def my_sync(a):
        return a

    my_sync._marker = marker

    decorated = use_case(my_sync)
    _ = decorated(1)

    assert getattr(captured_fn["fn"], "_marker", None) is marker


def test_wrapper_passes_through_args_and_kwargs_without_params(monkeypatch):
    dec_mod, use_case = import_fallback_use_case(monkeypatch)
    mock_prepare = MagicMock(return_value=("k", False))
    mock_runner_sync = MagicMock(return_value="ok")

    monkeypatch.setitem(use_case.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case.__globals__, "run_with_trace_sync", mock_runner_sync)

    @use_case
    def f(a, b, *, c=None, **kw):
        return (a, b, c, kw)

    _ = f(1, 2, c=3, d=4, e=5)

    assert mock_runner_sync.called
    r_args, r_kwargs = mock_runner_sync.call_args
    assert r_args[1] == (1, 2)
    assert r_args[2]["c"] == 3
    assert r_args[2]["d"] == 4
    assert r_args[2]["e"] == 5


def test_decorator_returns_function_when_called_without_parens_without_params(monkeypatch):
    dec_mod, use_case = import_fallback_use_case(monkeypatch)
    mock_prepare = MagicMock(return_value=("k", False))
    mock_runner_sync = MagicMock(return_value="X")

    monkeypatch.setitem(use_case.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case.__globals__, "run_with_trace_sync", mock_runner_sync)

    @use_case
    def g(x):
        return x

    assert g(7) == "X"


def test_decorator_factory_returns_decorator_when_called_with_parens_without_params(monkeypatch):
    dec_mod, use_case = import_fallback_use_case(monkeypatch)
    mock_prepare = MagicMock(return_value=("k", False))
    mock_runner_sync = MagicMock(return_value="Y")

    monkeypatch.setitem(use_case.__globals__, "prepare_function", mock_prepare)
    monkeypatch.setitem(use_case.__globals__, "run_with_trace_sync", mock_runner_sync)

    dec = use_case(keyname="k2", do_trace=False)
    assert callable(dec)

    @dec
    def h(y):
        return y

    assert h(9) == "Y"
    args, kwargs = mock_prepare.call_args
    assert args[1] == "k2"
    assert args[2] is False
