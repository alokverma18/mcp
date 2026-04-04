import os
import json
import httpx
from typing import Optional

from fastmcp import FastMCP
from fastapi import Request, Depends

mcp = FastMCP("GitHub MCP Server")
GITHUB_API_BASE = "https://api.github.com"


# -------------------------
# Dependency Injection
# -------------------------
def get_request(request: Request):
    return request


# -------------------------
# Auth Helpers
# -------------------------
def _extract_token(request: Optional[Request] = None) -> str:
    # 1. Try Authorization header (REMOTE MCP)
    if request:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.replace("Bearer ", "")

    # 2. Fallback to env (LOCAL MCP)
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token

    raise Exception("Missing GitHub token (no Authorization header or env var)")


def _get_headers(request: Optional[Request] = None):
    token = _extract_token(request)

    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }


async def _request(method: str, url: str, request: Optional[Request], **kwargs):
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.request(
            method,
            url,
            headers=_get_headers(request),
            **kwargs
        )

    if response.status_code >= 400:
        return None, f"Error: {response.status_code} - {response.text}"

    return response.json(), None


# -------------------------
# Basic Tools
# -------------------------

@mcp.tool()
async def get_user_repos(
    username: str,
    request: Request = Depends(get_request)
) -> str:
    data, err = await _request("GET", f"{GITHUB_API_BASE}/users/{username}/repos", request)
    if err:
        return err
    return "\n".join([repo.get("name", "<unknown>") for repo in data])


@mcp.tool()
async def get_repo_details(
    owner: str,
    repo: str,
    request: Request = Depends(get_request)
) -> str:
    data, err = await _request("GET", f"{GITHUB_API_BASE}/repos/{owner}/{repo}", request)
    if err:
        return err

    return json.dumps({
        "name": data.get("full_name"),
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
    }, indent=2)


@mcp.tool()
async def get_repo_commits(
    owner: str,
    repo: str,
    per_page: int = 5,
    request: Request = Depends(get_request)
) -> str:
    data, err = await _request(
        "GET",
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits",
        request,
        params={"per_page": per_page}
    )
    if err:
        return err

    return "\n".join([
        f"{c['sha'][:7]}: {c['commit']['message'].splitlines()[0]}"
        for c in data
    ])


@mcp.tool()
async def get_repo_issues(
    owner: str,
    repo: str,
    request: Request = Depends(get_request)
) -> str:
    data, err = await _request(
        "GET",
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues",
        request
    )
    if err:
        return err

    return "\n".join([
        f"{i['number']}: {i['title']}"
        for i in data if not i.get("pull_request")
    ])


# -------------------------
# Write Tools
# -------------------------

@mcp.tool()
async def create_repo(
    name: str,
    description: Optional[str] = "",
    private: bool = False,
    request: Request = Depends(get_request)
) -> str:
    payload = {"name": name, "description": description, "private": private}
    data, err = await _request("POST", f"{GITHUB_API_BASE}/user/repos", request, json=payload)
    if err:
        return err
    return json.dumps({"created": data.get("full_name")})


@mcp.tool()
async def create_issue(
    owner: str,
    repo: str,
    title: str,
    body: Optional[str] = None,
    request: Request = Depends(get_request)
) -> str:
    payload = {"title": title, "body": body}
    data, err = await _request(
        "POST",
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues",
        request,
        json=payload
    )
    if err:
        return err

    return json.dumps({
        "issue": data.get("number"),
        "url": data.get("html_url")
    })


# -------------------------
# WOW Tool 🚀 1
# -------------------------

@mcp.tool()
async def summarize_repo(
    owner: str,
    repo: str,
    request: Request = Depends(get_request)
) -> str:
    repo_data, err = await _request("GET", f"{GITHUB_API_BASE}/repos/{owner}/{repo}", request)
    if err:
        return err

    commits, _ = await _request(
        "GET",
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits",
        request,
        params={"per_page": 5}
    )

    contributors, _ = await _request(
        "GET",
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors",
        request,
        params={"per_page": 5}
    )

    return f"""
📦 {repo_data.get("full_name")}
⭐ {repo_data.get("stargazers_count")} stars | 🍴 {repo_data.get("forks_count")} forks
🧑‍💻 Language: {repo_data.get("language")}

📝 {repo_data.get("description")}

🚀 Recent commits:
{chr(10).join(["- " + c["commit"]["message"].splitlines()[0] for c in (commits or [])])}

👥 Top contributors:
{chr(10).join(["- " + c["login"] for c in (contributors or [])])}
""".strip()


# -------------------------
# WOW Tool 🚀 2
# -------------------------

@mcp.tool()
async def analyze_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
    request: Request = Depends(get_request)
) -> str:
    pr, err = await _request(
        "GET",
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}",
        request
    )
    if err:
        return err

    files, _ = await _request(
        "GET",
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/files",
        request
    )

    return f"""
🔀 PR #{pr.get("number")}: {pr.get("title")}
👤 {pr.get("user", {}).get("login")}

📊 +{pr.get("additions")} / -{pr.get("deletions")}
📁 Files changed: {pr.get("changed_files")}

📝 {pr.get("body") or "No description"}

📂 Files:
{chr(10).join([f"- {f['filename']}" for f in (files or [])[:10]])}
""".strip()


# -------------------------
# Resource (no auth needed)
# -------------------------

@mcp.resource("file://github_info.txt")
def get_github_info() -> str:
    return """
GitHub MCP Server

- Uses GitHub REST API
- Token passed via MCP headers
- Supports repos, issues, commits, PRs
- Includes smart analysis tools
"""


# -------------------------
# Prompt (optional)
# -------------------------

@mcp.prompt("github_assistant")
def github_prompt(user_query: str) -> str:
    return f"""
You are a GitHub assistant.

User request: {user_query}

- Use tools when needed
- Prefer real data over assumptions
- Keep responses concise
"""

if __name__ == "__main__":
    mcp.run()