"""Test advanced features tools."""

import pytest
from fastmcp import Client


async def test_migrateable_validators_tool_exists(obol_server):
    """Test that migrateable validators tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_migrateable_validators" in tool_names


async def test_owr_tranches_tool_exists(obol_server):
    """Test that OWR tranches tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_owr_tranches" in tool_names


async def test_terms_signed_status_tool_exists(obol_server):
    """Test that terms signed status tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_terms_signed_status" in tool_names


