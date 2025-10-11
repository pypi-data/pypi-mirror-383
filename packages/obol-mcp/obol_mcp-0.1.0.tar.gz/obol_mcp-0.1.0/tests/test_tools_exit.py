"""Test exit coordination tools."""

import pytest
from fastmcp import Client


async def test_exit_status_summary_tool_exists(obol_server):
    """Test that exit status summary tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_cluster_exit_status_summary" in tool_names


async def test_exit_status_tool_exists(obol_server):
    """Test that exit status tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_cluster_exit_status" in tool_names



