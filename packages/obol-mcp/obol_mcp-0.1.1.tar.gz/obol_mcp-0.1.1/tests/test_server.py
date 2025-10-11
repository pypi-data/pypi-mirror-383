"""Test server initialization and configuration."""

import pytest
from fastmcp import Client


async def test_server_name(obol_server):
    """Test that server has correct name."""
    assert obol_server.name == "Obol MCP"


async def test_server_has_tools(obol_server):
    """Test that server has registered tools."""
    tools = await obol_server.get_tools()
    assert len(tools) > 0, "Server should have at least one tool"


async def test_server_tool_count(obol_server):
    """Test that server has expected number of tools."""
    tools = await obol_server.get_tools()
    # Based on README: 22 tools total
    assert len(tools) == 22, f"Expected 22 tools, found {len(tools)}"


async def test_all_tools_have_names(obol_server):
    """Test that all tools have valid names."""
    tools = await obol_server.get_tools()
    for tool_name, tool in tools.items():
        assert tool_name, "Tool name should not be empty"
        assert isinstance(tool_name, str), "Tool name should be a string"
        assert tool.name == tool_name, "Tool name should match dict key"


async def test_all_tools_have_descriptions(obol_server):
    """Test that all tools have descriptions."""
    tools = await obol_server.get_tools()
    for tool_name, tool in tools.items():
        assert tool.description, f"Tool {tool_name} should have a description"


async def test_server_client_connection(obol_server):
    """Test that client can connect to server."""
    async with Client(obol_server) as client:
        # Test basic connectivity with ping
        result = await client.ping()
        assert result is True, "Client should be able to ping server"
