"""Async wrapper for `BasicUseCase`.

This module defines class `AsyncBasicUseCase`, an asynchronous variant of
``BasicUseCase`` that awaits the result of the resolved entrypoint on
invocation. It allows existing synchronous use cases to continue working
unchanged while enabling coroutine-based entrypoints to be awaited
transparently.

Notes
-----
- The actual entrypoint resolution (e.g., choosing a `use`/`run` method or a
  method decorated with ``@use_case``) is delegated to ``BasicUseCase``.
- If the resolved entrypoint returns a coroutine or any awaitable, it will be
  awaited. Otherwise, the value is returned as-is (no offloading to a thread
  pool is performed).
"""
from abc import ABC
from typing import Generic, Callable
import inspect

from .use_case_entry_resolver import UseCaseEntryResolver
from ..typing_compat import ParamSpec, P, R


if ParamSpec is not None:
    class AsyncBasicUseCase(UseCaseEntryResolver, Generic[P, R], ABC):
        """
        Asynchronous variant of class `BasicUseCase`.

        This class preserves the entrypoint resolution behavior of
        class `BasicUseCase` but modifies the invocation semantics: calling the
        use case will await the result if it is awaitable.

        See Also
        --------
        BasicUseCase
            Base implementation that resolves the entrypoint and supports both
            synchronous and asynchronous methods without enforcing an async call.

        Examples
        --------
        Define an asynchronous use case and invoke it with ``await``:
            ```python
            class GetItem(AsyncBasicUseCase):
                async def use(self, item_id: int) -> dict:
                    return {"id": item_id}

            uc = GetItem()
            result = await uc(42)
            ```

        Define a synchronous use case; the result is returned directly without awaiting:

            ```python
            class GetItemSync(AsyncBasicUseCase):
                def use(self, item_id: int) -> dict:
                    return {"id": item_id}

            uc = GetItemSync()
            result = await uc(42)  # Allowed; result is not awaitable and is returned as-is.
            ```
        """

        @property
        def entrypoint(self) -> Callable[P, R]:
            """Returns the entrypoint method for the use case."""
            return self._entrypoint

        async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
            """
            Invoke the resolved entrypoint and await if necessary.

            Parameters
            ----------
            *args : P.args
                Positional arguments forwarded to the resolved entrypoint.
            **kwargs : P.kwargs
                Keyword arguments forwarded to the resolved entrypoint.

            Returns
            -------
            R
                The entrypoint result. If the entrypoint returned an awaitable,
                this method returns its awaited value; otherwise, it returns the
                value directly.

            Notes
            -----
            - No thread offloading is performed for synchronous entrypoints.
            - The entrypoint is obtained from class `BasicUseCase` (e.g., a
              ``use``/``run`` method or a method decorated with ``@use_case``).
            """
            res = self.entrypoint(*args, **kwargs)
            if inspect.isawaitable(res):
                return await res
            return res

else:
    class AsyncBasicUseCase(UseCaseEntryResolver, ABC):
        """
        Asynchronous variant of class `BasicUseCase` (fallback without ParamSpec).

        Behaves like the generic version but without type parameter preservation.
        On invocation, if the resolved entrypoint returns an awaitable, it is
        awaited; otherwise the value is returned as-is.

        See Also
        --------
        BasicUseCase
            Base implementation responsible for resolving the entrypoint.

        Examples
        --------
        Define an asynchronous use case and invoke it with ``await``:

            ```python
            class GetItem(AsyncBasicUseCase):
                async def use(self, item_id: int) -> dict:
                    return {"id": item_id}

            uc = GetItem()
            result = await uc(42)
            ```
        """
        @property
        def entrypoint(self) -> Callable[..., R]:
            """Returns the entrypoint method for the use case."""
            return self._entrypoint

        async def __call__(self, *args, **kwargs):
            """
            Invoke the resolved entrypoint and await if necessary.

            Parameters
            ----------
            *args :
                Positional arguments forwarded to the resolved entrypoint.
            **kwargs :
                Keyword arguments forwarded to the resolved entrypoint.

            Returns
            -------
            Any
                The entrypoint result. If the entrypoint returned an awaitable,
                this method returns its awaited value; otherwise, it returns the
                value directly.
            """
            res = self.entrypoint(*args, **kwargs)
            if inspect.isawaitable(res):
                return await res
            return res
