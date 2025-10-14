"""Use Case Entry Resolver definition."""
from abc import ABCMeta
from types import MethodType
from typing import Optional, Iterator

from .use_case_base import UseCaseBase
from .use_case_decorator.decorator import use_case
from ..transactional.transaction_traceable import TransactionTraceable


class UseCaseEntryResolver(UseCaseBase, TransactionTraceable, metaclass=ABCMeta):
    """Abstract base class for use case entry resolvers."""

    def __init__(self, keyname: Optional[str] = None, *, do_trace: bool = True) -> None:
        UseCaseBase.__init__(self, keyname)
        self._do_trace = do_trace
        self._entrypoint = self._resolve_entrypoint()

    def entrypoint_candidate(self) -> Iterator[MethodType]:
        """Checks if the given attribute is a candidate for use as the use case entrypoint."""
        for attr_name in dir(self):
            if attr_name.startswith("_") or attr_name in ("entrypoint", "__call__"):  # avoid recursion
                continue

            attr = getattr(self, attr_name)

            if not isinstance(attr, MethodType) or getattr(attr, "__self__", None) is None:
                continue
            func = attr.__func__
            if hasattr(func, "__is_use_case__"):  # marker set by @use_case
                yield attr
        return

    def _resolve_entrypoint(self):
        """Resolves the method to be used as the use case entrypoint.

        Parameters
        ----------
        self: BasicUseCase

        """
        use_fn = getattr(self, "use", None) or getattr(self, "run", None)
        if use_fn is not None and callable(use_fn):
            # Decorating the use function with @use_case if not already decorated
            use_fn = use_case(keyname=use_fn.__name__, do_trace=self._do_trace)(
                use_fn)
            return use_fn

        for attr in self.entrypoint_candidate():
            return attr
        raise AttributeError(
            f"No method decorated with @use_case or named 'use'/'run' "
            f"found in {self.__class__.__name__}"
        )
