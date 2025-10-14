import asyncio
import inspect
from types import MethodType

import pytest
from bisslog.use_cases.use_case_basic_async import AsyncBasicUseCase


class HarnessAsync(AsyncBasicUseCase):
    """Test harness: injects a custom entrypoint without touching BasicUseCase.

    We override `_resolve_entrypoint` so tests do not rely on the real decorator
    or tracing. The injected function must accept `self` as its first argument.
    """
    def __init__(self, entrypoint_fn, *args, **kwargs):
        self._injected = entrypoint_fn
        super().__init__(*args, **kwargs)

    def _resolve_entrypoint(self):
        # Always bind the injected function to this instance.
        return MethodType(self._injected, self)


@pytest.mark.asyncio
async def test_awaits_async_entrypoint():
    async def ep(self, x, *, y=0):
        await asyncio.sleep(0)
        return {"sum": x + y}

    uc = HarnessAsync(entrypoint_fn=ep)
    out = await uc(2, y=3)
    assert out == {"sum": 5}


@pytest.mark.asyncio
async def test_returns_sync_value_directly():
    def ep(self, x, y):
        return {"mul": x * y}

    uc = HarnessAsync(entrypoint_fn=ep)
    out = await uc(4, 7)  # __call__ is async; underlying result is sync
    assert out == {"mul": 28}


@pytest.mark.asyncio
async def test_passes_args_and_kwargs():
    seen = {}

    async def ep(self, a, b, *, flag=False, data=None):
        seen["a"] = a
        seen["b"] = b
        seen["flag"] = flag
        seen["data"] = data
        return "ok"

    uc = HarnessAsync(entrypoint_fn=ep)
    res = await uc(10, 20, flag=True, data={"k": 1})
    assert res == "ok"
    assert seen == {"a": 10, "b": 20, "flag": True, "data": {"k": 1}}


@pytest.mark.asyncio
async def test_exception_propagation():
    class Boom(Exception):
        pass

    async def ep(self):
        raise Boom("bad things happened")

    uc = HarnessAsync(entrypoint_fn=ep)
    with pytest.raises(Boom, match="bad things happened"):
        await uc()


@pytest.mark.asyncio
async def test_instance_is_async_callable():
    """The class-level __call__ must be an async function; bound call produces an awaitable."""
    async def ep(self): return "ok"
    uc = HarnessAsync(entrypoint_fn=ep)

    assert inspect.iscoroutinefunction(type(uc).__call__)
    result_awaitable = uc.__call__()  # do not await yet
    assert inspect.isawaitable(result_awaitable)
    assert await result_awaitable == "ok"



@pytest.mark.asyncio
async def test_resolution_use_async_method():
    class GetItemAsync(AsyncBasicUseCase):
        async def use(self, item_id: int) -> dict:
            await asyncio.sleep(0)
            return {"id": item_id}

    uc = GetItemAsync()
    assert await uc(42) == {"id": 42}


@pytest.mark.asyncio
async def test_resolution_use_sync_method():
    class GetItemSync(AsyncBasicUseCase):
        def use(self, item_id: int) -> dict:
            return {"id": item_id}

    uc = GetItemSync()
    assert await uc(7) == {"id": 7}
