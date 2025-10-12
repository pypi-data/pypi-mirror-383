"""
Test sync functions (resolve, from_env) work in async contexts.

This addresses the issue where calling asyncio.run() from within a running
event loop raises RuntimeError. The sync functions should detect this and
run in a thread instead.
"""

import asyncio
import os

import pytest
from pydantic import BaseModel

from python_env_resolver import from_env, resolve


class SampleConfig(BaseModel):
    """Sample configuration model (renamed to avoid pytest collection warning)."""

    test_var: str
    test_num: int = 42


def test_resolve_no_event_loop():
    """Test resolve() works when no event loop is running."""
    os.environ["TEST_VAR"] = "sync_test"
    os.environ["TEST_NUM"] = "100"

    config = from_env(SampleConfig)

    assert config.test_var == "sync_test"
    assert config.test_num == 100


@pytest.mark.asyncio
async def test_resolve_with_running_loop():
    """
    Test resolve() works inside a running event loop.

    This is the FastAPI/uvicorn use case - when the framework imports
    modules, there's already an event loop running. The sync function
    should detect this and execute in a worker thread.
    """
    os.environ["TEST_VAR"] = "async_context_test"
    os.environ["TEST_NUM"] = "200"

    # This should NOT raise RuntimeError!
    config = from_env(SampleConfig)

    assert config.test_var == "async_context_test"
    assert config.test_num == 200


@pytest.mark.asyncio
async def test_resolve_multiple_calls_in_loop():
    """Test multiple sync calls in the same event loop."""
    os.environ["TEST_VAR"] = "multi_test"
    os.environ["TEST_NUM"] = "300"

    # Multiple calls should all work
    config1 = from_env(SampleConfig)
    config2 = from_env(SampleConfig)
    config3 = resolve(SampleConfig)

    assert config1.test_var == config2.test_var == config3.test_var == "multi_test"
    assert config1.test_num == config2.test_num == config3.test_num == 300


def test_module_level_import_simulation():
    """
    Simulate FastAPI module-level import pattern.

    This is what happens when uvicorn imports app/main.py:
    1. Module is imported
    2. from_env() is called at module level
    3. Event loop may or may not be running (depends on timing)
    """
    os.environ["TEST_VAR"] = "module_level"
    os.environ["TEST_NUM"] = "500"

    # Simulate module-level call
    config = from_env(SampleConfig)

    assert config.test_var == "module_level"
    assert config.test_num == 500


@pytest.mark.asyncio
async def test_sync_and_async_mixed():
    """Test mixing sync and async resolve calls in the same loop."""
    from python_env_resolver import from_env_async

    os.environ["TEST_VAR"] = "mixed_test"
    os.environ["TEST_NUM"] = "600"

    # Call sync version first
    sync_config = from_env(SampleConfig)

    # Then async version
    async_config = await from_env_async(SampleConfig)

    # Both should work and return same values
    assert sync_config.test_var == async_config.test_var == "mixed_test"
    assert sync_config.test_num == async_config.test_num == 600


def test_fastapi_startup_simulation():
    """
    Simulate FastAPI startup sequence.

    When uvicorn starts:
    1. Creates event loop
    2. Imports app module (with module-level from_env() call)
    3. Starts the app

    This test simulates that sequence.
    """

    async def simulate_uvicorn():
        # Set env vars before import
        os.environ["TEST_VAR"] = "fastapi_sim"
        os.environ["TEST_NUM"] = "700"

        # This simulates the module being imported after loop starts
        config = from_env(SampleConfig)

        return config

    # Run in a loop (like uvicorn does)
    config = asyncio.run(simulate_uvicorn())

    assert config.test_var == "fastapi_sim"
    assert config.test_num == 700

