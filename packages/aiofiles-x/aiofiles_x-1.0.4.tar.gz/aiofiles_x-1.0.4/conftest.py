"""
Pytest configuration for aiofiles-x.
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_configure(config):
    """Configure pytest."""
    # Add custom marks
    config.addinivalue_line(
        "markers", "benchmark: marks tests as benchmarks"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
