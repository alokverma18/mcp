# Learning MCP

This guide explains the MCP (Model Context Protocol) concepts used in this project.

## What is MCP?

MCP is a protocol that allows AI models (like GPT) to securely interact with external tools and data. Think of it as a bridge between LLMs and your applications.

## Core MCP Concepts

### 1. Tools
**What they are**: Functions that LLMs can call to perform actions.
**In this project**:
- `get_user_repos()` - Fetch GitHub repositories
- `query_database()` - Execute SQL queries
- `search_repositories()` - Search GitHub

**How they work**:
```python
@mcp.tool()
def get_user_repos(username: str) -> str:
    """Fetch public repositories for a GitHub user."""
    # Implementation here
    return "Repository list"
```

### 2. Resources
**What they are**: Static data/files that provide context to LLMs.
**In this project**:
- `github_info.txt` - GitHub platform information
- Used to give LLMs background knowledge about GitHub

**How they work**:
```python
@mcp.resource("file://github_info.txt")
def get_github_info() -> str:
    """GitHub platform overview."""
    return "GitHub is a platform for..."
```

### 3. Prompts
**What they are**: Templates that guide LLM responses.
**In this project**:
- `github_query_prompt` - Helps LLM handle GitHub requests

**How they work**:
```python
@mcp.prompt("github_query_prompt")
def github_prompt(request: str) -> str:
    return f"Help with this GitHub request: {request}"
```

## How MCP Works

### Server-Client Communication
1. **Server**: Exposes tools, resources, and prompts
2. **Client**: Connects to server and discovers available tools
3. **LLM**: Chooses which tools to call based on user request
4. **Execution**: Client calls tools on behalf of LLM
5. **Response**: Results are sent back to LLM

### Communication Flow
```
User Request → LLM → MCP Client → MCP Server → Tool Execution → Result → LLM → User
```

## This Project's Architecture

### Two MCP Servers

#### GitHub Server (`server/github.py`)
- **Tools**: 15 GitHub API functions
- **Resources**: GitHub platform information
- **Prompts**: GitHub-specific guidance

#### Database Server (`server/database.py`)
- **Tools**: 1 SQL query function
- **Resources**: None (minimal example)
- **Prompts**: None

### LLM Integration (`client/mcp_client.py`)
- **Purpose**: Show real MCP usage with AI models
- **How**: LLM discovers tools and decides which to call
- **Features**: Uses resources + prompts for context

### Real-World Relevance
- **LLM integration** = How actual AI applications use MCP
- **Servers** = How you'd build MCP for your own tools

## Development & Testing

### Development Testing (`testing/`)
- **Purpose**: Verify servers work correctly during development
- **How**: Direct tool calls with predefined arguments
- **Example**: `python testing/test_github_server.py get-repos octocat`
- **Usage**: Development tool, not for end users

## Why This Structure?

### Learning Progression
1. **Start simple** - Database server with 1 tool
2. **Add complexity** - GitHub server with many tools
3. **Testing** - Verify servers work correctly
4. **Understand LLM integration** - Real MCP usage


## Key Takeaways

### MCP Benefits
- **Secure**: LLMs don't directly access your systems
- **Flexible**: Any tool can be exposed as an MCP tool
- **Standardized**: Works across different LLM platforms
- **Controlled**: You decide what LLMs can do

### When to Use MCP
- **External APIs**: GitHub, databases, cloud services
- **Internal systems**: Company databases, internal tools
- **File operations**: Reading/writing files with permissions
- **Any functionality**: You want LLMs to access safely

### Building Your Own MCP Server
1. **Start with tools** - What functions do you need?
2. **Add resources** - What context does the LLM need?
3. **Create prompts** - How should the LLM behave?
4. **Test thoroughly** - Use testing clients
5. **Deploy** - Run as stdio server

## Next Steps

1. **Experiment**: Try the testing clients
2. **Modify**: Add your own tools to servers
3. **Integrate**: Use with your favorite LLM platform
4. **Deploy**: Run servers for production use

This project is a starting point for understanding and building with MCP!
