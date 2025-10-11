"""Test health and system status tools."""

import pytest
from fastmcp import Client


async def test_obol_api_health_tool_exists(obol_server):
    """Test that health check tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_api_health" in tool_names



async def test_obol_api_metrics_tool_exists(obol_server):
    """Test that metrics tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_api_metrics" in tool_names
