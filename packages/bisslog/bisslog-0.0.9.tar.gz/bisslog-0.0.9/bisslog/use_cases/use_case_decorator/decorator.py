"""Use-case decorator that supports both sync and async functions with optional parameters."""
import inspect
from functools import wraps
from typing import Optional, Union, Callable

from bisslog.domain_context import domain_context
from bisslog.transactional.transaction_manager import transaction_manager
from bisslog.typing_compat import P, R, ParamSpec
from .prepare_function import prepare_function
from .run_with_trace_async import run_with_trace_async
from .run_with_trace_sync import run_with_trace_sync

tracing_opener = domain_context.opener


if ParamSpec is not None:

    def use_case(
            _fn: Optional[Callable[P, R]] = None,
            *,
            keyname: Optional[str] = None,
            do_trace: bool = True
    ) -> Union[Callable[P, R], Callable[[Callable[P, R]], Callable[P, R]]]:
        """
        Flexible use case decorator that supports usage with or without parentheses.
        Works for both synchronous and asynchronous functions.

        Usage examples
        --------------
        @use_case
        def my_sync(...): ...

        @use_case(keyname="custom", do_trace=False)
        async def my_async(...): ...

        Parameters
        ----------
        _fn : Callable, optional
            Internal-only argument. Do not pass manually.
        keyname : Optional[str], optional
            Tracing keyname. Defaults to the function name.
        do_trace : bool, optional
            Whether to trace the execution. Defaults to True.

        Returns
        -------
        Callable
            A function decorator or the decorated function, depending on usage.
        """

        def decorator(fn: Callable[P, R]) -> Callable[P, R]:
            m_keyname, accepts_transaction_id = prepare_function(fn, keyname, do_trace)

            if inspect.iscoroutinefunction(fn):
                @wraps(fn)
                async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                    """Async wrapper that delegates to `run_with_trace_async`.

                    This wrapper is created only when the decorated function is a coroutine
                    function. It ensures transaction lifecycle management is preserved for
                    asynchronous use cases.
                    """
                    return await run_with_trace_async(
                        fn, args, kwargs, m_keyname, do_trace,
                        _tracing_opener=tracing_opener,
                        _transaction_manager=transaction_manager,
                        _accepts_transaction_id=accepts_transaction_id
                    )
                wrapper._is_coroutine = True  # pylint: disable=protected-access
            else:
                @wraps(fn)
                def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                    """Sync wrapper that delegates to `run_with_trace_sync`.

                    This wrapper is created only when the decorated function is a regular
                    (non-async) function. It ensures transaction lifecycle management is
                    preserved for synchronous use cases.
                    """
                    return run_with_trace_sync(
                        fn, args, kwargs, m_keyname, do_trace,
                        _tracing_opener=tracing_opener,
                        _transaction_manager=transaction_manager,
                        _accepts_transaction_id=accepts_transaction_id
                    )

            return wrapper

        if _fn is not None:
            return decorator(_fn)

        return decorator
else:
    def use_case(
            _fn: Optional[Callable[..., R]] = None,
            *,
            keyname: Optional[str] = None,
            do_trace: bool = True
    ) -> Union[Callable[..., R], Callable[[Callable[..., R]], Callable[..., R]]]:
        """
        Fallback version of the use_case decorator without signature preservation.
        Works for both synchronous and asynchronous functions.

        Parameters
        ----------
        _fn : Callable, optional
            Internal-only argument. Do not pass manually.
        keyname : Optional[str], optional
            Tracing keyname. Defaults to the function name.
        do_trace : bool, optional
            Whether to trace the execution. Defaults to True.

        Returns
        -------
        Callable
            A function decorator or the decorated function, depending on usage.
        """

        def decorator(fn: Callable[..., R]) -> Callable[..., R]:
            m_keyname, accepts_transaction_id = prepare_function(fn, keyname, do_trace)

            if inspect.iscoroutinefunction(fn):
                @wraps(fn)
                async def wrapper(*args, **kwargs) -> R:
                    """Async wrapper that delegates to `run_with_trace_async`.

                    This wrapper is created only when the decorated function is a coroutine
                    function. It ensures transaction lifecycle management is preserved for
                    asynchronous use cases.
                    """
                    return await run_with_trace_async(
                        fn, args, kwargs, m_keyname, do_trace,
                        _tracing_opener=tracing_opener,
                        _transaction_manager=transaction_manager,
                        _accepts_transaction_id=accepts_transaction_id
                    )
                wrapper._is_coroutine = True  # pylint: disable=protected-access
            else:
                @wraps(fn)
                def wrapper(*args, **kwargs) -> R:
                    """Sync wrapper that delegates to `run_with_trace_sync`.

                    This wrapper is created only when the decorated function is a regular
                    (non-async) function. It ensures transaction lifecycle management is
                    preserved for synchronous use cases.
                    """
                    return run_with_trace_sync(
                        fn, args, kwargs, m_keyname, do_trace,
                        _tracing_opener=tracing_opener,
                        _transaction_manager=transaction_manager,
                        _accepts_transaction_id=accepts_transaction_id
                    )

            return wrapper

        if _fn is not None:
            return decorator(_fn)

        return decorator
