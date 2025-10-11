# Changelog

## [2.1.0] - 2025-01-XX - PyPI Package Release

### Added
- **PyPI Distribution**: Package now available on PyPI as `obol-mcp`
- **One-Command Installation**: `fastmcp install obol-mcp --name "Obol MCP"`
- **Python Package Structure**: Proper package with `obol_mcp` module
- **CLI Entry Point**: `obol-mcp` command for easy execution
- **Module Execution**: Run with `python -m obol_mcp`
- **Development Mode**: Support for `pip install -e .`

### Changed
- **Renamed**: "Obol DVT MCP Server" → "Obol MCP" (cleaner branding)
- **Restructured**: Moved server code to `obol_mcp/` package directory
- **Updated Documentation**: Comprehensive installation guide for PyPI, GitHub, and development

### Package Files
- Added `pyproject.toml` for Python packaging
- Added `obol_mcp/__init__.py` with version and main entry point
- Added `obol_mcp/__main__.py` for module execution
- Added `MANIFEST.in` for package distribution
- Original `server.py` preserved in root for backwards compatibility

## [2.0.1] - FastMCP 2.x Update

### Updated
- Updated to FastMCP 2.x (tested with 2.11.3) with modern installation practices
- Updated README with FastMCP Cloud hosting information
- Added FastMCP version verification steps
- Updated all FastMCP documentation links to official site (https://gofastmcp.com)
- Updated installation instructions to use `uv` best practices
- Added production deployment guidance with version pinning

### Documentation
- Added FastMCP Cloud hosting section with free tier information
- Improved installation verification steps
- Updated Claude Desktop integration instructions
- Enhanced deployment options documentation

## [2.0.0] - 2025 Refresh

### Major Enhancements

This release significantly expands the Obol MCP server from 5 basic tools to **22 comprehensive tools** for DVT cluster troubleshooting, monitoring, and operator management.

### Added Tools

#### Health & System Status (2 tools)
- `obol_api_health` - Enhanced with database and beacon node connectivity info
- `obol_api_metrics` - NEW: Prometheus-style metrics endpoint

#### Cluster Lock Operations (5 tools)
- `obol_cluster_lock_by_hash` - NEW: Primary method to get cluster lock by lock_hash
- `obol_lock_by_config_hash` - Existing, now enhanced
- `obol_locks_by_network` - Existing, now enhanced with better pagination
- `obol_cluster_search` - NEW: Search clusters by partial lock_hash or name
- `obol_network_summary` - NEW: Network-wide cluster statistics

#### Cluster Health & Monitoring (2 tools)
- `obol_cluster_effectiveness` - Existing, enhanced documentation
- `obol_cluster_validator_states` - NEW: Get beacon chain states for all validators

#### Operator Management (5 tools)
- `obol_operator_clusters` - NEW: List all clusters for an operator
- `obol_operator_info` - NEW: Get operator statistics on a network
- `obol_search_operators` - NEW: Search operators by partial address
- `obol_operator_badges` - NEW: Get operator badges (lido, etherfi, etc.)
- `obol_operator_techne` - NEW: Get Techne credentials (bronze, silver, gold)
- `obol_operator_incentives` - NEW: Get Obol token incentives

#### Exit Coordination (2 tools)
- `obol_cluster_exit_status_summary` - NEW: Exit status summary for cluster
- `obol_cluster_exit_status` - NEW: Detailed exit status with filtering

#### DKG & Cluster Definitions (2 tools)
- `obol_cluster_definition` - NEW: Get cluster definition/proposal
- `obol_operator_definitions` - NEW: List definitions an operator is part of

#### Advanced Features (4 tools)
- `obol_migrateable_validators` - NEW: Get validators eligible for migration
- `obol_owr_tranches` - NEW: Get OWR tranche information
- `obol_terms_signed_status` - Existing, enhanced

### Documentation Improvements

- Completely rewritten README with:
  - Tool categorization by use case
  - Comprehensive troubleshooting scenarios
  - Network support documentation
  - Common issues and solutions
  - Real-world usage examples
- Added .gitignore enhancements for Python artifacts
- Improved tool descriptions with DVT troubleshooting context

### Breaking Changes

- Server name changed from "Obol API Reader" to "Obol DVT Cluster Monitor"
- All tools now include comprehensive docstrings explaining DVT troubleshooting use cases

## [1.0.0] - Initial Release

### Initial Tools (5)
- `obol_api_health`
- `obol_cluster_effectiveness`
- `obol_lock_by_config_hash`
- `obol_locks_by_network`
- `obol_terms_signed_status`
