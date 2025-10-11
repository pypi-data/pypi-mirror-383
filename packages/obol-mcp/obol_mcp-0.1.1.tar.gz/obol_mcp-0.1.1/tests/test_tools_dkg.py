"""Test DKG and cluster definition tools."""

import pytest
from fastmcp import Client


async def test_cluster_definition_tool_exists(obol_server):
    """Test that cluster definition tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_cluster_definition" in tool_names


async def test_operator_definitions_tool_exists(obol_server):
    """Test that operator definitions tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_operator_definitions" in tool_names



