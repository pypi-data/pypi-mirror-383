"""Synchronous function execution with transactional tracing logic."""

from typing import Callable

from bisslog.ports.tracing.opener_tracer import OpenerTracer
from bisslog.transactional.transaction_manager import TransactionManager
from bisslog.typing_compat import R
from .utils import (
    prepare_transaction_context,
    finalize_success,
    finalize_error,
    call_with_optional_tid_sync,
)


def run_with_trace_sync(
    fn: Callable[..., R],
    args: tuple,
    kwargs: dict,
    keyname: str,
    do_trace: bool,
    *,
    _tracing_opener: OpenerTracer,
    _transaction_manager: TransactionManager,
    _accepts_transaction_id: bool,
) -> R:
    """
    Executes a synchronous function with transactional tracing logic.

    This is the synchronous counterpart of the async runner. It handles the
    transaction lifecycle (start/end/close) and error tracing while invoking a
    regular (non-async) callable.
    """
    super_transaction_id, transaction_id = prepare_transaction_context(
        args=args,
        kwargs=kwargs,
        keyname=keyname,
        do_trace=do_trace,
        _tracing_opener=_tracing_opener,
        _transaction_manager=_transaction_manager,
    )

    try:
        result = call_with_optional_tid_sync(
            fn,
            args=args,
            kwargs=kwargs,
            transaction_id=transaction_id,
            accepts_transaction_id=_accepts_transaction_id,
        )
    except BaseException as ex:
        finalize_error(
            do_trace=do_trace,
            keyname=keyname,
            transaction_id=transaction_id,
            super_transaction_id=super_transaction_id,
            error=ex,
            _tracing_opener=_tracing_opener,
            _transaction_manager=_transaction_manager,
        )
        raise

    finalize_success(
        do_trace=do_trace,
        keyname=keyname,
        transaction_id=transaction_id,
        super_transaction_id=super_transaction_id,
        result=result,
        _tracing_opener=_tracing_opener,
        _transaction_manager=_transaction_manager,
    )
    return result
