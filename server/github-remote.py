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
    # 1. Try MCP headers (REMOTE)
    if ctx:
        try:
            headers = ctx.request.headers
            auth_header = headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                return auth_header.replace("Bearer ", "")
        except Exception:
            pass

    # 2. Fallback (LOCAL)
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token

    raise Exception("Missing GitHub token")


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


# -------------------------
# ENTRYPOINT (REQUIRED FOR DEPLOY)
# -------------------------
if __name__ == "__main__":
    mcp.run()