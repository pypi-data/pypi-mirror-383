import argparse

from jnpr_pathfinder_mcp.server.pathfinder import mcp
from jnpr_pathfinder_mcp.helpers import run_cli

def main():
    run_cli(prog="Juniper Pathfinder Apps MCP Server", server=mcp)

if __name__ == "__main__":  # pragma: no cover
    main()
