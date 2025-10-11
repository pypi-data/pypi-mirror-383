"""Test cluster lock and monitoring tools."""

import pytest
from fastmcp import Client
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_cluster_lock():
    """Mock cluster lock response."""
    return {
        "lock_hash": "0xabc123",
        "config_hash": "0xdef456",
        "name": "Test Cluster",
        "operators": [
            {"address": "0x1234", "enr": "enr://..."},
            {"address": "0x5678", "enr": "enr://..."}
        ],
        "validators": [
            {"public_key": "0xaaa", "fee_recipient": "0xbbb"}
        ],
        "network": "holesky"
    }


@pytest.fixture
def mock_effectiveness():
    """Mock effectiveness response."""
    return {
        "lock_hash": "0xabc123",
        "validators": [
            {
                "public_key": "0xaaa",
                "effectiveness": 0.98,
                "attestation_rate": 0.99,
                "proposal_rate": 1.0
            }
        ]
    }


async def test_cluster_lock_tool_exists(obol_server):
    """Test that cluster lock tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_cluster_lock_by_hash" in tool_names


async def test_cluster_effectiveness_tool_exists(obol_server):
    """Test that effectiveness tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_cluster_effectiveness" in tool_names


async def test_cluster_search_tool_exists(obol_server):
    """Test that cluster search tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_cluster_search" in tool_names


async def test_network_summary_tool_exists(obol_server):
    """Test that network summary tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_network_summary" in tool_names


async def test_validator_states_tool_exists(obol_server):
    """Test that validator states tool is registered."""
    tools = await obol_server.get_tools()
    tool_names = list(tools.keys())
    assert "obol_cluster_validator_states" in tool_names
