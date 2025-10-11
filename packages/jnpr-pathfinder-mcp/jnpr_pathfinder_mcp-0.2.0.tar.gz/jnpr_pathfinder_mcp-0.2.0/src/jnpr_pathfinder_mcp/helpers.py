import argparse

def parse_args(prog='jnpr_pathfinder_mcp'):
    parser = argparse.ArgumentParser(
            prog=prog,
            description="An MCP Server for interacting with Juniper's Pathfinder Apps.")
    parser.add_argument(
        "--transport", choices=["stdio", "http"], default="stdio", help="transport to use"
    )
    parser.add_argument("--host", help="host for http transport", default=None)
    parser.add_argument("--port", help="port for http transport", type=int, default=None)
    return parser.parse_args()


def run_cli(prog, server):
    args = parse_args(prog)
    kwargs = {'transport': args.transport}

    if args.transport == "stdio":
        if (args.host is not None or args.port is not None):
            raise ValueError("host/port cannot be used with stdio transport")
    elif args.transport == "http":
        kwargs['host'] = args.host
        kwargs['port'] = args.port
    else:
        raise ValueError(f"transport must be 'stdio' or 'http'")

    server.run(**kwargs)
