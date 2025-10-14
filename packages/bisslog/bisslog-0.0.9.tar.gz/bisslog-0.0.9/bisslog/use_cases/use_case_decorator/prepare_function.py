"""Prepares a function for use case decoration."""

import inspect

from typing import Callable, Optional, Tuple

from bisslog.utils.is_free_function import is_free_function


def prepare_function(fn: Callable, keyname: Optional[str], do_trace: bool) -> Tuple[str, bool]:
    """Prepares the function for use case decoration.

    Parameters
    ----------
    fn : Callable
        The function to decorate.
    keyname : Optional[str]
        The keyname for tracing, or None to use the function name.
    do_trace : bool
        Whether tracing is enabled.

    Returns
    -------
    Tuple[str, bool]
        The resolved keyname and whether the function accepts a transaction_id.
    """
    m_keyname = keyname or fn.__name__
    sig = inspect.signature(fn)
    accepts_transaction_id = (
            do_trace and
            ("transaction_id" in sig.parameters
             or any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values()))
    )
    if is_free_function(fn):
        fn.__is_use_case__ = True
    return m_keyname, accepts_transaction_id
