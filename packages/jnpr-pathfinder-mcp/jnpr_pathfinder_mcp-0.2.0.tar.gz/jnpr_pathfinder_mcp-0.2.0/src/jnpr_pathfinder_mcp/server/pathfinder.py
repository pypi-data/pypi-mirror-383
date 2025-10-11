
from fastmcp import FastMCP  # type: ignore

from jnpr_pathfinder_mcp.server.cli_explorer import mcp as cli_explorer_mcp
from jnpr_pathfinder_mcp.server.feature_explorer import mcp as feature_explorer_mcp
from jnpr_pathfinder_mcp.server.hct import mcp as hct_mcp

# Create the MCP instance and expose tools
mcp = FastMCP("jnpr_pathfinder_mcp")

mcp.mount(hct_mcp, prefix="juniper_hardware_compatibility_tool")
mcp.mount(cli_explorer_mcp, prefix="juniper_cli_explorer")
mcp.mount(feature_explorer_mcp, prefix="juniper_feature_explorer")
