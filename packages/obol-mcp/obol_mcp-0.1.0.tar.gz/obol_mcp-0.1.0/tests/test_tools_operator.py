"""Test operator management tools."""

import pytest
from fastmcp import Client
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_operator_info():
    """Mock operator info response."""
    return {
        "address": "0x1234567890abcdef",
        "cluster_count": 5,
        "validator_count": 20,
        "networks": ["mainnet", "holesky"]
    }


async def test_operator_info_tool_exists(obol_server):
    """Test that operator info tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_operator_info" in tool_names


async def test_operator_clusters_tool_exists(obol_server):
    """Test that operator clusters tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_operator_clusters" in tool_names


async def test_operator_badges_tool_exists(obol_server):
    """Test that operator badges tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_operator_badges" in tool_names


async def test_operator_techne_tool_exists(obol_server):
    """Test that operator techne tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_operator_techne" in tool_names


async def test_operator_incentives_tool_exists(obol_server):
    """Test that operator incentives tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_operator_incentives" in tool_names


async def test_search_operators_tool_exists(obol_server):
    """Test that search operators tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_search_operators" in tool_names




