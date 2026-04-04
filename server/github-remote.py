import os
import httpx
from fastmcp import FastMCP
import anyio

mcp = FastMCP("GitHub MCP Server")
GITHUB_API_BASE = "https://api.github.com"


# -------------------------
# Auth (HEADER + ENV)
# -------------------------
def _extract_token(ctx=None) -> str:
    # 1. Try MCP headers
    if ctx:
        try:
            headers = getattr(ctx.request, "headers", {})
            auth_header = headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                return auth_header.replace("Bearer ", "")
        except Exception:
            pass

    # 2. Try query params (some clients send this way)
    if ctx:
        try:
            query = getattr(ctx.request, "query_params", {})
            token = query.get("token")
            if token:
                return token
        except Exception:
            pass

    # 3. Fallback env (VERY IMPORTANT)
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token

    raise Exception(
        "Missing GitHub token. Pass via headers or set GITHUB_TOKEN env."
    )


def _get_headers(ctx=None):
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {_extract_token(ctx)}",
    }


# -------------------------
# HTTP Helper
# -------------------------
async def _request(method: str, url: str, ctx=None, **kwargs):
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.request(
            method,
            url,
            headers=_get_headers(ctx),
            **kwargs
        )

    if response.status_code >= 400:
        return None, f"Error: {response.status_code} - {response.text}"

    return response.json(), None


# -------------------------
# TOOL 1
# -------------------------
@mcp.tool()
async def get_user_repos(username: str, ctx=None) -> str:
    """Get public repositories of a GitHub user"""
    data, err = await _request(
        "GET",
        f"{GITHUB_API_BASE}/users/{username}/repos",
        ctx
    )
    if err:
        return err

    return "\n".join([repo.get("name", "<unknown>") for repo in data])


# -------------------------
# TOOL 2
# -------------------------
@mcp.tool()
async def get_repo_details(owner: str, repo: str, ctx=None) -> str:
    """Get repository details"""
    data, err = await _request(
        "GET",
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}",
        ctx
    )
    if err:
        return err

    return f"""
Name: {data.get("full_name")}
Description: {data.get("description")}
Language: {data.get("language")}
Stars: {data.get("stargazers_count")}
Forks: {data.get("forks_count")}
""".strip()

@mcp.resource("info://server")
def info():
    return "GitHub MCP server is running"

# -------------------------
# ENTRYPOINT (REQUIRED FOR DEPLOY)
# -------------------------

if __name__ == "__main__":
    if os.getenv("MCP_TRANSPORT") == "local":
        anyio.run(mcp.run_stdio_async)
    
    else:
        async def run_http():
            port = int(os.getenv("PORT", 8000))
            await mcp.run_http_async(
                host="0.0.0.0",
                port=port,
                transport="sse"
            )

        anyio.run(run_http)