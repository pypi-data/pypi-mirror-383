"""
Use case decorator implementation with transactional tracing support.
Now supports both synchronous and asynchronous (async def) functions.

This module provides a flexible decorator `@use_case` that can be used with or
without parentheses. It wraps a function with transaction lifecycle management,
based on globally available tracing and transaction managers.

Functions decorated will be marked with `__is_use_case__ = True` and traced
automatically using the configured system.

To enable function signature preservation for autocompletion and static analysis
(especially in Python < 3.10), it is recommended to install `typing_extensions`.

Installation
------------
pip install typing_extensions
"""

from .decorator import use_case

__all__ = ["use_case"]
