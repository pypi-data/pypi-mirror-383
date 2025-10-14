"""Shared utilities for transactional tracing in use case execution.

This module centralizes the common, cross-cutting logic used by both the
synchronous and asynchronous runners:
- extracting/propagating `transaction_id` from kwargs
- starting the trace (when enabled)
- finishing the trace (success/error) and closing the transaction
- invoking the target function with or without injecting `transaction_id`
"""

from typing import Callable, Optional, Tuple, Awaitable, Any

from bisslog.ports.tracing.opener_tracer import OpenerTracer
from bisslog.transactional.transaction_manager import TransactionManager


def prepare_transaction_context(
    *,
    args: tuple,
    kwargs: dict,
    keyname: str,
    do_trace: bool,
    _tracing_opener: OpenerTracer,
    _transaction_manager: TransactionManager,
) -> Tuple[Optional[str], Optional[str]]:
    """Prepare tracing/transaction context before invoking the function.

    Pops a potential inbound `transaction_id` from kwargs (treated as
    a "super transaction"), creates a new transaction id if tracing is enabled,
    and starts the trace accordingly.

    Returns
    -------
    Tuple[Optional[str], Optional[str]]
        (super_transaction_id, transaction_id) after preparation. Note:
        when `do_trace` is False both values may be None. If an inbound
        `transaction_id` existed and `do_trace` is True, the created id is
        returned as `transaction_id` and the inbound one remains as `super`.
    """
    super_transaction_id = kwargs.pop("transaction_id", None)
    transaction_id = super_transaction_id

    if do_trace:
        transaction_id = _transaction_manager.create_transaction_id(keyname)
        _tracing_opener.start(
            *args,
            super_transaction_id=super_transaction_id,
            component=keyname,
            transaction_id=transaction_id,
            **kwargs,
        )

    if super_transaction_id is None:
        super_transaction_id = transaction_id

    return super_transaction_id, transaction_id


def finalize_success(
    *,
    do_trace: bool,
    keyname: str,
    transaction_id: Optional[str],
    super_transaction_id: Optional[str],
    result: Any,
    _tracing_opener: OpenerTracer,
    _transaction_manager: TransactionManager,
) -> None:
    """Finish a successful traced execution and close the transaction if needed."""
    if not do_trace:
        return
    _tracing_opener.end(
        transaction_id=transaction_id,
        component=keyname,
        super_transaction_id=super_transaction_id,
        result=result,
    )
    _transaction_manager.close_transaction()


def finalize_error(
    *,
    do_trace: bool,
    keyname: str,
    transaction_id: Optional[str],
    super_transaction_id: Optional[str],
    error: BaseException,
    _tracing_opener: OpenerTracer,
    _transaction_manager: TransactionManager,
) -> None:
    """Finish a failed traced execution and close the transaction if needed."""
    if not do_trace:
        return
    _tracing_opener.end(
        transaction_id=transaction_id,
        component=keyname,
        super_transaction_id=super_transaction_id,
        result=error,
    )
    _transaction_manager.close_transaction()


def call_with_optional_tid_sync(
    fn: Callable[..., Any],
    *,
    args: tuple,
    kwargs: dict,
    transaction_id: Optional[str],
    accepts_transaction_id: bool,
):
    """Invoke a synchronous function with or without injecting `transaction_id`."""
    if accepts_transaction_id:
        return fn(*args, transaction_id=transaction_id, **kwargs)
    return fn(*args, **kwargs)


async def call_with_optional_tid_async(
    fn: Callable[..., Awaitable[Any]],
    *,
    args: tuple,
    kwargs: dict,
    transaction_id: Optional[str],
    accepts_transaction_id: bool,
):
    """Invoke an asynchronous function with or without injecting `transaction_id`."""
    if accepts_transaction_id:
        return await fn(*args, transaction_id=transaction_id, **kwargs)
    return await fn(*args, **kwargs)
