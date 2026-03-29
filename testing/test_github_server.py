import os
import sys
import subprocess
import argparse
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.abspath(os.path.dirname(__file__))
GITHUB_SERVER = os.path.abspath(os.path.join(HERE, "..", "server", "github.py"))


async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """Call MCP tool and return result."""
    params = StdioServerParameters(command=sys.executable, args=[GITHUB_SERVER])
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return str(result.content[0].text)


def create_cli_parser():
    """Create CLI parser for GitHub MCP tools."""
    parser = argparse.ArgumentParser(description="GitHub MCP Server - Testing Utility")
    subparsers = parser.add_subparsers(dest="cmd", help="Available commands")

    # Repository Operations
    repos_parser = subparsers.add_parser("get-repos", help="Get repositories for a user")
    repos_parser.add_argument("username", help="GitHub username")

    details_parser = subparsers.add_parser("get-repo-details", help="Get detailed repository information")
    details_parser.add_argument("owner", help="Repository owner")
    details_parser.add_argument("repo", help="Repository name")

    commits_parser = subparsers.add_parser("get-commits", help="Get recent commits")
    commits_parser.add_argument("owner", help="Repository owner")
    commits_parser.add_argument("repo", help="Repository name")
    commits_parser.add_argument("--per-page", type=int, default=10, help="Number of commits to fetch")

    search_parser = subparsers.add_parser("search-repos", help="Search repositories")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--sort", default="stars", choices=["stars", "forks", "updated", "created"], help="Sort by")
    search_parser.add_argument("--per-page", type=int, default=10, help="Number of results")

    return parser


async def execute_command(args):
    """Execute the CLI command by calling the appropriate MCP tool."""
    # Map CLI commands to MCP tool calls
    tool_mapping = {
        "get-repos": lambda: ("get_user_repos", {"username": args.username}),
        "get-repo-details": lambda: ("get_repo_details", {"owner": args.owner, "repo": args.repo}),
        "get-commits": lambda: ("get_repo_commits", {"owner": args.owner, "repo": args.repo, "per_page": args.per_page}),
        "search-repos": lambda: ("search_repositories", {"query": args.query, "sort": args.sort, "order": "desc", "per_page": args.per_page}),
    }

    if args.cmd not in tool_mapping:
        print(f"Unknown command: {args.cmd}")
        return

    try:
        tool_name, tool_args = tool_mapping[args.cmd]()
        print(f"Testing MCP tool: {tool_name} with args: {tool_args}")
        
        result = await call_mcp_tool(tool_name, tool_args)
        print(f"\nResult:\n{result}")
        
    except AttributeError as e:
        print(f"Missing required arguments for {args.cmd}: {e}")
        print(f"Use: python testing/test_github_server.py {args.cmd} --help")
    except Exception as e:
        print(f"Error executing {args.cmd}: {e}")


def main():
    parser = create_cli_parser()
    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    # Run the async command
    asyncio.run(execute_command(args))


if __name__ == "__main__":
    main()
