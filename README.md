# MCP Server Project

A simple project demonstrating how to build and use MCP (Model Context Protocol) servers.

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure MCP server in Windsurf/Claude Desktop:**
```json
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": ["/path/to/server/github.py"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here (see .env.example)"
      }
    },
    "database": {
      "command": "python", 
      "args": ["/path/to/server/database.py"]
    }
  }
}
```

3. **Use with LLM:**
- Start Windsurf/Claude Desktop
- Ask: "Show me octocat's repositories"
- LLM will automatically call the MCP server tools

## Testing (Optional)

For development and testing:
```bash
# Test GitHub server
python testing/test_github_server.py get-repos octocat

# Test Database server
python testing/test_database_server.py query "SELECT * FROM users"
```

## Project Structure

```
mcp/
├── server/                 # MCP servers
│   ├── github.py          # GitHub API server
│   └── database.py        # Database server
├── client/                 # Real LLM client
│   └── mcp_client.py      # LLM integration example
├── testing/               # Server testing utilities
│   ├── test_github_server.py   # Test GitHub server
│   └── test_database_server.py # Test Database server
├── simple.db              # Sample database file
├── requirements.txt        # Dependencies
├── README.md             # This file
└── learn.md              # Learning guide
```

## MCP Servers

Both servers are independent and demonstrate different use cases:

### GitHub Server (`server/github.py`)
- **Purpose**: Demonstrates how GitHub MCP servers work in the market
- **Use Case**: Public GitHub API access for general users
- **Tools**: GitHub API operations (get repos, commits, search, etc.)
- **Similar to**: Commercial GitHub MCP integrations

### Database Server (`server/database.py`)  
- **Purpose**: Shows enterprise database integration patterns
- **Use Case**: Internal database access in enterprise environments
- **Tools**: SQL query execution
- **Similar to**: Custom internal MCP servers for company data

## Testing vs Real Usage

### Testing Utilities (`testing/`)
- Direct tool calls to test server functionality
- Manual tool selection

### LLM Client (`client/mcp_client.py`)
- Real MCP usage with LLM integration
- Dynamic tool selection

## Learning

See `learn.md` for detailed explanations of MCP concepts and how this project works.

