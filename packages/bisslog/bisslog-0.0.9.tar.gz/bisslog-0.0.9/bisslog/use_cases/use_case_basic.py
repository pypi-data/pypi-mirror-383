"""
Use case tracking system class implementation.

This module provides an abstract base class `BasicUseCase` that integrates
transactional tracing into a use case execution flow.
"""

from abc import ABC
from typing import Generic, Callable

from .use_case_entry_resolver import UseCaseEntryResolver
from ..typing_compat import ParamSpec, P, R


if ParamSpec is not None:

    class BasicUseCase(UseCaseEntryResolver, Generic[P, R], ABC):
        """Base class for use cases with optional transactional tracing.

        Automatically looks for a method decorated with @use_case. If none is found, it
        falls back to a method named `use`, which will be decorated dynamically.

        On call, the selected method is executed as the entrypoint.
        """

        @property
        def entrypoint(self) -> Callable[P, R]:
            """Returns the entrypoint method for the use case."""
            return self._entrypoint

        def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
            """
            Invokes the resolved use case entrypoint method.

            Parameters
            ----------
            *args :
                Positional arguments.
            **kwargs :
                Keyword arguments.

            Returns
            -------
            R
                The result of the use case.
            """
            return self._entrypoint(*args, **kwargs)

else:
    class BasicUseCase(UseCaseEntryResolver, ABC):
        """Fallback for use cases without signature preservation (ParamSpec unavailable).

        This version is used on Python versions < 3.10 without typing_extensions installed.
        """
        @property
        def entrypoint(self) -> Callable[..., R]:
            """Returns the entrypoint method for the use case."""
            return self._entrypoint

        def __call__(self, *args, **kwargs):
            """
            Invokes the resolved use case entrypoint method.

            Parameters
            ----------
            *args :
                Positional arguments.
            **kwargs :
                Keyword arguments.

            Returns
            -------
            Any
                The result of the use case.
            """
            return self._entrypoint(*args, **kwargs)
