"""
Pytest configuration file for the Minecraft MCP GDPC tests.
"""

import pytest

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "minecraft: mark test as requiring a running Minecraft server"
    )