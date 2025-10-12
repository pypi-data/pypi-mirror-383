import pytest
import time

from novita_sandbox.core import AsyncSandbox


@pytest.mark.skip_debug()
async def test_snapshot(async_sandbox: AsyncSandbox):
    assert await async_sandbox.is_running()

    await async_sandbox.beta_pause()
    assert not await async_sandbox.is_running()

    resumed_sandbox = await async_sandbox.connect()
    assert await async_sandbox.is_running()
    assert await resumed_sandbox.is_running()
    assert resumed_sandbox.sandbox_id == async_sandbox.sandbox_id

@pytest.mark.skip_debug()
async def test_snapshot_with_sync(async_sandbox: AsyncSandbox):
    assert await async_sandbox.is_running()

    start_time = time.time()
    await async_sandbox.beta_pause(sync=True)
    assert not await async_sandbox.is_running()

    duration = time.time() - start_time
    assert duration > 1
