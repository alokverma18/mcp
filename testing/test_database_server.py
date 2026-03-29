import os
import sys
import argparse
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.abspath(os.path.dirname(__file__))
DATABASE_SERVER = os.path.abspath(os.path.join(HERE, "..", "server", "database.py"))


async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """Call MCP tool and return result."""
    params = StdioServerParameters(command=sys.executable, args=[DATABASE_SERVER])
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return str(result.content[0].text)


def create_cli_parser():
    """Create simple CLI parser."""
    parser = argparse.ArgumentParser(description="Database MCP Server - Testing Utility")
    subparsers = parser.add_subparsers(dest="cmd", help="Available commands")

    # Query operations
    query_parser = subparsers.add_parser("query", help="Execute SQL query")
    query_parser.add_argument("sql", help="SQL query")

    return parser


async def execute_command(args):
    """Execute CLI command."""
    if args.cmd == "query":
        tool_name = "query_database"
        tool_args = {"sql": args.sql, "params": None}
        
        print(f"Testing MCP tool: {tool_name} with args: {tool_args}")
        result = await call_mcp_tool(tool_name, tool_args)
        print(f"\nResult:\n{result}")
    else:
        print("Unknown command. Use 'query'.")


def main():
    parser = create_cli_parser()
    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    asyncio.run(execute_command(args))


if __name__ == "__main__":
    main()
