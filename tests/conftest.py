"""Configuration for pytest."""
import asyncio
import pytest
from aiogram.fsm.storage.memory import MemoryStorage
from utils_for_tests import MockedBot

@pytest.fixture()
def bot():
    """Bot fixture."""
    return MockedBot()


@pytest.fixture()
def storage():
    """Storage fixture."""
    return MemoryStorage()

@pytest.fixture()
def event_loop():
    """Fixture for event loop."""
    return asyncio.new_event_loop()
