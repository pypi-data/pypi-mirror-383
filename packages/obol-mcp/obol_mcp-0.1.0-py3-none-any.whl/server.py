# server.py
import httpx
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP

# --- Configuration ---
OBOL_API_BASE_URL = "https://api.obol.tech"

# --- FastMCP Server Setup ---
mcp = FastMCP(
    name="Obol MCP",
    instructions="Provides comprehensive read-only access to Obol API for DVT cluster troubleshooting, monitoring, and operator management."
)

# --- Helper Function for API Calls ---
async def _call_obol_api(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper function to make GET requests to the Obol API."""
    url = f"{OBOL_API_BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=15.0)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            # Ensure we return a dictionary, even if the response is empty or not JSON
            try:
                return response.json()
            except Exception:
                return {"status_code": response.status_code, "content": response.text}
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_detail = e.response.json()
            except Exception:
                pass
            return {
                "error": f"HTTP error {e.response.status_code} calling Obol API",
                "endpoint": endpoint,
                "details": error_detail
            }
        except httpx.RequestError as e:
            return {
                "error": "Request error calling Obol API",
                "endpoint": endpoint,
                "details": str(e)
            }
        except Exception as e:
            return {
                "error": "An unexpected error occurred",
                 "endpoint": endpoint,
                 "details": str(e)
             }

# --- Tools based on Obol API GET Endpoints ---

# ==================== HEALTH & SYSTEM STATUS ====================

@mcp.tool("obol_api_health")
async def get_health() -> Dict[str, Any]:
    """
    Check the Obol API health status including database and beacon node connectivity.
    Useful for diagnosing API availability issues.
    Corresponds to GET /v1/_health.
    """
    return await _call_obol_api("/v1/_health")

@mcp.tool("obol_api_metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Retrieve Prometheus-style metrics from the Obol API.
    Useful for monitoring API performance and usage statistics.
    Corresponds to GET /metrics.
    """
    return await _call_obol_api("/metrics")

# ==================== CLUSTER LOCK OPERATIONS ====================

@mcp.tool("obol_cluster_lock_by_hash")
async def get_cluster_lock_by_hash(lock_hash: str) -> Dict[str, Any]:
    """
    Retrieve a complete Distributed Validator Cluster Lock Object by its lock_hash.
    This is the primary way to get cluster configuration after DKG completion.
    Corresponds to GET /v1/lock/{lockHash}.
    
    Args:
        lock_hash: The lock_hash calculated for the cluster lock.
    """
    if not lock_hash:
        return {"error": "lock_hash argument is required."}
    return await _call_obol_api(f"/v1/lock/{lock_hash}")

@mcp.tool("obol_lock_by_config_hash")
async def get_lock_by_config_hash(config_hash: str) -> Dict[str, Any]:
    """
    Retrieve a Distributed Validator Cluster Lock Object by its config_hash.
    Useful when you have the cluster definition hash but not the lock hash.
    Corresponds to GET /v1/lock/configHash/{configHash}.

    Args:
        config_hash: The config_hash calculated for the cluster configuration.
    """
    if not config_hash:
        return {"error": "config_hash argument is required."}
    return await _call_obol_api(f"/v1/lock/configHash/{config_hash}")

@mcp.tool("obol_locks_by_network")
async def get_locks_by_network(
    network: str,
    page: int = 0,
    limit: int = 100,
    sortBy: str = "", 
    sortOrder: str = "", 
    pool: str = "", 
    details: bool = False,
) -> Dict[str, Any]:
    """
    Retrieve a paginated list of Distributed Validator Cluster Lock Objects for a network.
    Useful for discovering clusters and analyzing network-wide patterns.
    Corresponds to GET /v1/lock/network/{network}.

    Args:
        network: The network to retrieve clusters on (e.g., 'mainnet', 'holesky', 'sepolia').
        page: The page number to retrieve (0-indexed).
        limit: The number of cluster lock objects to return per page (max 100).
        sortBy: Field to sort by (e.g., 'avg_effectiveness', 'created_at').
        sortOrder: Sort order ('asc' or 'desc').
        pool: Filter by cluster type or pool (e.g., 'lido', 'etherfi').
        details: Flag to populate full cluster definition information.
    """
    if not network:
        return {"error": "network argument is required."}
    params: Dict[str, Any] = {
        "page": page,
        "limit": limit,
        "details": str(details).lower(),
    }
    if sortBy:
        params["sortBy"] = sortBy
    if sortOrder:
        params["sortOrder"] = sortOrder
    if pool:
        params["pool"] = pool

    return await _call_obol_api(f"/v1/lock/network/{network}", params=params)

@mcp.tool("obol_cluster_search")
async def search_cluster_locks(
    network: str,
    partialLockHash: str = "",
    partialClusterName: str = "",
    page: int = 0,
    limit: int = 100,
) -> Dict[str, Any]:
    """
    Search for Distributed Validator Cluster Lock Objects by partial lock_hash or cluster name.
    Useful for finding specific clusters when you only know part of the identifier.
    Corresponds to GET /v1/lock/search/{network}.

    Args:
        network: The network to search on (e.g., 'mainnet', 'holesky', 'sepolia').
        partialLockHash: A substring of the lock_hash to search for.
        partialClusterName: A substring of the cluster name to search for.
        page: The page number to retrieve (0-indexed).
        limit: The number of results to return per page (max 100).
    """
    if not network:
        return {"error": "network argument is required."}
    params: Dict[str, Any] = {"page": page, "limit": limit}
    if partialLockHash:
        params["partialLockHash"] = partialLockHash
    if partialClusterName:
        params["partialClusterName"] = partialClusterName
    
    return await _call_obol_api(f"/v1/lock/search/{network}", params=params)

@mcp.tool("obol_network_summary")
async def get_network_summary(network: str) -> Dict[str, Any]:
    """
    Retrieve a summary of all Distributed Validator clusters on a given network.
    Provides aggregate statistics like total clusters, validators, and effectiveness.
    Corresponds to GET /v1/lock/network/summary/{network}.

    Args:
        network: The network to get summary for (e.g., 'mainnet', 'holesky').
    """
    if not network:
        return {"error": "network argument is required."}
    return await _call_obol_api(f"/v1/lock/network/summary/{network}")

# ==================== CLUSTER HEALTH & MONITORING ====================

@mcp.tool("obol_cluster_effectiveness")
async def get_cluster_effectiveness(lock_hash: str) -> Dict[str, Any]:
    """
    Retrieve effectiveness metrics for a specific Distributed Validator Cluster.
    Shows per-validator performance metrics critical for troubleshooting poor cluster performance.
    Corresponds to GET /v1/effectiveness/{lockHash}.

    Args:
        lock_hash: The lock_hash calculated for the cluster lock.
    """
    if not lock_hash:
         return {"error": "lock_hash argument is required."}
    return await _call_obol_api(f"/v1/effectiveness/{lock_hash}")

@mcp.tool("obol_cluster_validator_states")
async def get_cluster_validator_states(lock_hash: str) -> Dict[str, Any]:
    """
    Retrieve the current beacon chain states of all validators in a DV Cluster.
    Shows validator index, status (active_ongoing, exiting, slashed, etc.), and balance.
    Critical for troubleshooting validator lifecycle issues.
    Corresponds to GET /v1/state/{lockHash}.

    Args:
        lock_hash: The lock_hash calculated for the cluster lock.
    """
    if not lock_hash:
        return {"error": "lock_hash argument is required."}
    return await _call_obol_api(f"/v1/state/{lock_hash}")

# ==================== OPERATOR MANAGEMENT ====================

@mcp.tool("obol_operator_clusters")
async def get_operator_clusters(
    address: str,
    page: int = 0,
    limit: int = 100,
) -> Dict[str, Any]:
    """
    Retrieve all Distributed Validator Clusters where the given address is an operator.
    Useful for auditing an operator's participation and troubleshooting operator-specific issues.
    Corresponds to GET /v1/lock/operator/{address}.

    Args:
        address: The operator's Ethereum address.
        page: The page number to retrieve (0-indexed).
        limit: The number of cluster lock objects to return per page (max 100).
    """
    if not address:
        return {"error": "address argument is required."}
    params: Dict[str, Any] = {"page": page, "limit": limit}
    return await _call_obol_api(f"/v1/lock/operator/{address}", params=params)

@mcp.tool("obol_operator_info")
async def get_operators_by_network(
    network: str,
    page: int = 0,
    limit: int = 100,
    details: bool = False,
    sortBy: str = "",
    sortOrder: str = "",
) -> Dict[str, Any]:
    """
    Retrieve a list of operators on a given network with their statistics.
    Shows active validator counts, effectiveness, and other metrics per operator.
    Corresponds to GET /v1/address/network/{network}.

    Args:
        network: The network to retrieve operators on (e.g., 'mainnet', 'holesky', 'sepolia').
        page: The page number to retrieve (0-indexed).
        limit: The number of operators to return per page (max 100).
        details: Flag to populate full operator information.
        sortBy: Field to sort by (e.g., 'active_validators_count', 'avg_effectiveness').
        sortOrder: Sort order ('asc' or 'desc').
    """
    if not network:
        return {"error": "network argument is required."}
    params: Dict[str, Any] = {
        "page": page,
        "limit": limit,
        "details": str(details).lower(),
    }
    if sortBy:
        params["sortBy"] = sortBy
    if sortOrder:
        params["sortOrder"] = sortOrder
    
    return await _call_obol_api(f"/v1/address/network/{network}", params=params)

@mcp.tool("obol_search_operators")
async def search_operators(
    network: str,
    partialAddress: str = "",
    page: int = 0,
    limit: int = 100,
) -> Dict[str, Any]:
    """
    Search for operators by partial address match on a given network.
    Useful for finding operator information when you only know part of their address.
    Corresponds to GET /v1/address/search/{network}.

    Args:
        network: The network to search on (e.g., 'mainnet', 'holesky', 'sepolia').
        partialAddress: A substring of the operator's address to search for.
        page: The page number to retrieve (0-indexed).
        limit: The number of results to return per page (max 100).
    """
    if not network:
        return {"error": "network argument is required."}
    params: Dict[str, Any] = {"page": page, "limit": limit}
    if partialAddress:
        params["partialAddress"] = partialAddress
    
    return await _call_obol_api(f"/v1/address/search/{network}", params=params)

@mcp.tool("obol_operator_badges")
async def get_operator_badges(address: str) -> Dict[str, Any]:
    """
    Retrieve badges associated with an operator address.
    Badges indicate participation in specific protocols (e.g., lido, etherfi).
    Corresponds to GET /v1/address/badges/{address}.

    Args:
        address: The operator's Ethereum address.
    """
    if not address:
        return {"error": "address argument is required."}
    return await _call_obol_api(f"/v1/address/badges/{address}")

@mcp.tool("obol_operator_techne")
async def get_operator_techne(address: str) -> Dict[str, Any]:
    """
    Retrieve Obol Techne credentials for an operator address.
    Techne credentials (base, bronze, silver, gold) indicate operator experience and reliability.
    Corresponds to GET /v1/address/techne/{address}.

    Args:
        address: The operator's Ethereum address.
    """
    if not address:
        return {"error": "address argument is required."}
    return await _call_obol_api(f"/v1/address/techne/{address}")

@mcp.tool("obol_operator_incentives")
async def get_operator_incentives(network: str, address: str) -> Dict[str, Any]:
    """
    Retrieve Obol incentives (token rewards) for an operator address on a specific network.
    Shows current incentive balance and eligibility.
    Corresponds to GET /v1/address/incentives/{network}/{address}.

    Args:
        network: The network (e.g., 'mainnet', 'sepolia').
        address: The operator's Ethereum address.
    """
    if not network or not address:
        return {"error": "network and address arguments are required."}
    return await _call_obol_api(f"/v1/address/incentives/{network}/{address}")

# ==================== EXIT COORDINATION ====================

@mcp.tool("obol_cluster_exit_status_summary")
async def get_cluster_exit_status_summary(lock_hash: str) -> Dict[str, Any]:
    """
    Retrieve a summary of exit status for a cluster.
    Shows which operators have signed exit messages and how many validators are ready to exit.
    Critical for coordinating voluntary exits across distributed validators.
    Corresponds to GET /v1/exp/exit/status/summary/{lockHash}.

    Args:
        lock_hash: The lock_hash of the cluster.
    """
    if not lock_hash:
        return {"error": "lock_hash argument is required."}
    return await _call_obol_api(f"/v1/exp/exit/status/summary/{lock_hash}")

@mcp.tool("obol_cluster_exit_status")
async def get_cluster_exit_status(
    lock_hash: str,
    page: int = 1,
    limit: int = 10,
    operatorAddress: str = "",
    validatorPubkey: str = "",
) -> Dict[str, Any]:
    """
    Retrieve detailed exit status for validators in a cluster with optional filtering.
    Shows per-validator and per-operator exit signature status.
    Corresponds to GET /v1/exp/exit/status/{lockHash}.

    Args:
        lock_hash: The lock_hash of the cluster.
        page: The page number to retrieve (1-indexed for this endpoint).
        limit: The number of validators to return per page.
        operatorAddress: Optional filter by operator address.
        validatorPubkey: Optional filter by validator public key.
    """
    if not lock_hash:
        return {"error": "lock_hash argument is required."}
    params: Dict[str, Any] = {"page": page, "limit": limit}
    if operatorAddress:
        params["operatorAddress"] = operatorAddress
    if validatorPubkey:
        params["validatorPubkey"] = validatorPubkey
    
    return await _call_obol_api(f"/v1/exp/exit/status/{lock_hash}", params=params)

# ==================== DKG & CLUSTER DEFINITIONS ====================

@mcp.tool("obol_cluster_definition")
async def get_cluster_definition(config_hash: str) -> Dict[str, Any]:
    """
    Retrieve a Distributed Validator Cluster definition (proposal) by config_hash.
    Shows the cluster configuration before DKG, including operator approval status.
    Useful for troubleshooting DKG ceremony issues.
    Corresponds to GET /v1/definition/{configHash}.

    Args:
        config_hash: The config_hash of the cluster definition.
    """
    if not config_hash:
        return {"error": "config_hash argument is required."}
    return await _call_obol_api(f"/v1/definition/{config_hash}")

@mcp.tool("obol_operator_definitions")
async def get_operator_definitions(
    address: str,
    page: int = 0,
    limit: int = 100,
) -> Dict[str, Any]:
    """
    Retrieve cluster definitions that an operator is part of.
    Shows pending and completed cluster proposals for an operator.
    Corresponds to GET /v1/definition/operator/{address}.

    Args:
        address: The operator's Ethereum address.
        page: The page number to retrieve (0-indexed).
        limit: The number of definitions to return per page (max 100).
    """
    if not address:
        return {"error": "address argument is required."}
    params: Dict[str, Any] = {"page": page, "limit": limit}
    return await _call_obol_api(f"/v1/definition/operator/{address}", params=params)

# ==================== ADVANCED FEATURES ====================

@mcp.tool("obol_migrateable_validators")
async def get_migrateable_validators(
    network: str,
    withdrawal_address: str,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Retrieve validators eligible for migration to a DVT cluster by withdrawal address.
    Shows active validators that can be migrated from solo staking to distributed validation.
    Corresponds to GET /v1/address/migrateable-validators/{network}/{withdrawalAddress}.

    Args:
        network: The network (e.g., 'mainnet', 'holesky', 'sepolia').
        withdrawal_address: The withdrawal address of the source validators.
        limit: The number of validators to return (max 50).
        offset: The offset for pagination.
    """
    if not network or not withdrawal_address:
        return {"error": "network and withdrawal_address arguments are required."}
    params: Dict[str, Any] = {"limit": limit, "offset": offset}
    return await _call_obol_api(
        f"/v1/address/migrateable-validators/{network}/{withdrawal_address}",
        params=params
    )

@mcp.tool("obol_owr_tranches")
async def get_owr_tranches(network: str, address: str) -> Dict[str, Any]:
    """
    Retrieve OWR (Optimistic Withdrawal Recipient) tranche information.
    Shows principal and reward recipient addresses and thresholds for reward splitting.
    Corresponds to GET /v1/owr/{network}/{address}.

    Args:
        network: The network (e.g., 'mainnet', 'holesky').
        address: The address of the OWR contract.
    """
    if not network or not address:
        return {"error": "network and address arguments are required."}
    return await _call_obol_api(f"/v1/owr/{network}/{address}")

@mcp.tool("obol_terms_signed_status")
async def get_terms_signed_status(address: str) -> Dict[str, Any]:
    """
    Check if the given address has signed the latest Obol Terms and Conditions.
    Required before an address can create or participate in clusters.
    Corresponds to GET /v1/termsAndConditions/{address}.

    Args:
        address: The Ethereum address to check.
    """
    if not address:
        return {"error": "address argument is required."}
    return await _call_obol_api(f"/v1/termsAndConditions/{address}")

# --- Main Execution Block ---
def main():
    """Main entry point for the server."""
    print("Starting Obol MCP Server...")
    print("Total tools available: 22")
    mcp.run()

if __name__ == "__main__":
    main()