import os
import json
import requests
from typing import Optional
from fastmcp import FastMCP

mcp = FastMCP("GitHub MCP Server")
GITHUB_API_BASE = "https://api.github.com"


def _get_headers():
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@mcp.tool()
def get_user_repos(username: str) -> str:
    """Fetch public repositories for a GitHub user."""
    response = requests.get(f"{GITHUB_API_BASE}/users/{username}/repos", headers=_get_headers())
    if response.status_code == 200:
        repos = response.json()
        return "\n".join([repo.get("name", "<unknown>") for repo in repos])
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def get_repo_issues(owner: str, repo: str) -> str:
    """Fetch open issues for a GitHub repository."""
    response = requests.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues", headers=_get_headers())
    if response.status_code == 200:
        issues = response.json()
        return "\n".join([f"{issue['number']}: {issue['title']}" for issue in issues if not issue.get("pull_request")])
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def create_repo(name: str, description: Optional[str] = "", private: bool = False) -> str:
    """Create a new repository for the authenticated user. Requires GITHUB_TOKEN with repo scope."""
    payload = {"name": name, "description": description, "private": private}
    response = requests.post(f"{GITHUB_API_BASE}/user/repos", json=payload, headers=_get_headers())
    if response.status_code in (200, 201):
        repo = response.json()
        return json.dumps({"result": "created", "full_name": repo.get("full_name")})
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def create_issue(owner: str, repo: str, title: str, body: Optional[str] = None) -> str:
    """Create an issue in the specified repository. Requires repo scope for private repos."""
    payload = {"title": title}
    if body:
        payload["body"] = body
    response = requests.post(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues", json=payload, headers=_get_headers())
    if response.status_code in (200, 201):
        issue = response.json()
        return json.dumps({"result": "created", "issue_number": issue.get("number"), "url": issue.get("html_url")})
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def create_pull_request(owner: str, repo: str, head: str, base: str, title: str, body: Optional[str] = None) -> str:
    """Create a pull request. head should be the branch name in the fork or repo (e.g. feature-branch)."""
    payload = {"title": title, "head": head, "base": base}
    if body:
        payload["body"] = body
    response = requests.post(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls", json=payload, headers=_get_headers())
    if response.status_code in (200, 201):
        pr = response.json()
        return json.dumps({"result": "created", "number": pr.get("number"), "url": pr.get("html_url")})
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def get_repo_commits(owner: str, repo: str, per_page: int = 10) -> str:
    """Fetch recent commits for a GitHub repository."""
    response = requests.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits", headers=_get_headers(), params={"per_page": per_page})
    if response.status_code == 200:
        commits = response.json()
        commit_list = []
        for commit in commits:
            sha = commit.get("sha", "")[:7]  # Short SHA
            message = commit.get("commit", {}).get("message", "").split("\n")[0]  # First line of commit message
            author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
            date = commit.get("commit", {}).get("author", {}).get("date", "")
            commit_list.append(f"{sha}: {message} - {author} ({date})")
        return "\n".join(commit_list)
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def get_repo_details(owner: str, repo: str) -> str:
    """Get detailed information about a GitHub repository."""
    response = requests.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}", headers=_get_headers())
    if response.status_code == 200:
        repo_data = response.json()
        details = {
            "name": repo_data.get("full_name"),
            "description": repo_data.get("description"),
            "language": repo_data.get("language"),
            "stars": repo_data.get("stargazers_count"),
            "forks": repo_data.get("forks_count"),
            "open_issues": repo_data.get("open_issues_count"),
            "default_branch": repo_data.get("default_branch"),
            "created_at": repo_data.get("created_at"),
            "updated_at": repo_data.get("updated_at"),
            "clone_url": repo_data.get("clone_url"),
            "html_url": repo_data.get("html_url")
        }
        return json.dumps(details, indent=2)
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def get_repo_branches(owner: str, repo: str) -> str:
    """Get all branches for a GitHub repository."""
    response = requests.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/branches", headers=_get_headers())
    if response.status_code == 200:
        branches = response.json()
        branch_list = []
        for branch in branches:
            name = branch.get("name", "Unknown")
            protected = branch.get("protected", False)
            last_commit = branch.get("commit", {}).get("sha", "")[:7]
            branch_list.append(f"{name} (Protected: {protected}, Last: {last_commit})")
        return "\n".join(branch_list)
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def get_repo_contributors(owner: str, repo: str) -> str:
    """Get contributors for a GitHub repository."""
    response = requests.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors", headers=_get_headers())
    if response.status_code == 200:
        contributors = response.json()
        contributor_list = []
        for contributor in contributors:
            username = contributor.get("login", "Unknown")
            contributions = contributor.get("contributions", 0)
            contributor_list.append(f"{username}: {contributions} contributions")
        return "\n".join(contributor_list)
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def create_comment(owner: str, repo: str, issue_number: int, body: str) -> str:
    """Create a comment on an issue or pull request."""
    payload = {"body": body}
    response = requests.post(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}/comments", json=payload, headers=_get_headers())
    if response.status_code in (200, 201):
        comment = response.json()
        return json.dumps({"result": "created", "comment_id": comment.get("id"), "url": comment.get("html_url")})
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def get_pull_requests(owner: str, repo: str, state: str = "open") -> str:
    """Get pull requests for a repository. State can be 'open', 'closed', or 'all'."""
    response = requests.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls", headers=_get_headers(), params={"state": state})
    if response.status_code == 200:
        prs = response.json()
        pr_list = []
        for pr in prs:
            number = pr.get("number", 0)
            title = pr.get("title", "")
            author = pr.get("user", {}).get("login", "Unknown")
            state = pr.get("state", "Unknown")
            pr_list.append(f"#{number}: {title} by {author} ({state})")
        return "\n".join(pr_list)
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def get_file_content(owner: str, repo: str, path: str, branch: str = "main") -> str:
    """Get content of a specific file from a repository."""
    response = requests.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}", headers=_get_headers(), params={"ref": branch})
    if response.status_code == 200:
        content_data = response.json()
        if content_data.get("type") == "file":
            import base64
            content = base64.b64decode(content_data.get("content", "")).decode('utf-8')
            return f"File: {path}\nSize: {content_data.get('size', 0)} bytes\n\n{content}"
        else:
            return f"Path {path} is a {content_data.get('type', 'unknown')}, not a file"
    return f"Error: {response.status_code} - {response.text}"


@mcp.tool()
def search_repositories(query: str, sort: str = "stars", order: str = "desc", per_page: int = 10) -> str:
    """Search GitHub repositories. Sort can be 'stars', 'forks', 'updated', 'created'. Order can be 'asc' or 'desc'."""
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": per_page
    }
    response = requests.get(f"{GITHUB_API_BASE}/search/repositories", headers=_get_headers(), params=params)
    if response.status_code == 200:
        search_results = response.json()
        repos = search_results.get("items", [])
        repo_list = []
        for repo in repos:
            name = repo.get("full_name", "")
            description = repo.get("description", "")
            stars = repo.get("stargazers_count", 0)
            language = repo.get("language", "Unknown")
            repo_list.append(f"{name} ({language}) - {stars} stars\n  {description}")
        return "\n\n".join(repo_list)
    return f"Error: {response.status_code} - {response.text}"


@mcp.resource("file://github_info.txt")
def get_github_info() -> str:
    """GitHub platform overview and key concepts."""
    return """GitHub is a platform for version control, collaboration, and code hosting using Git.

Key Concepts:
- Repository: Project containing files, folders, and revision history
- Commit: Snapshot of changes made to files
- Branch: Parallel version of a repository
- Pull Request: Proposed changes to be merged into a branch
- Issue: Tracker for bugs, enhancements, or tasks
- Fork: Personal copy of another user's repository

GitHub API:
- Base URL: https://api.github.com
- Authentication: Personal access tokens for higher rate limits
- Rate Limits: 60/hour (unauth), 5000/hour (auth)

Best Practices:
- Check response status codes
- Handle pagination for large result sets
- Use appropriate HTTP methods
- Include descriptive commit messages and issue titles"""


@mcp.prompt("github_query_prompt")
def github_prompt(github_request: str) -> str:
    """Prompt for handling GitHub-related queries."""
    return f"""Assist with this GitHub request: {github_request}. 

Available GitHub Tools:
- get_user_repos(username): Get all repositories for a user
- get_repo_details(owner, repo): Get detailed repository information
- get_repo_commits(owner, repo, per_page): Get recent commits
- get_repo_branches(owner, repo): Get all branches
- get_repo_contributors(owner, repo): Get contributors list
- get_repo_issues(owner, repo): Get open issues
- get_pull_requests(owner, repo, state): Get pull requests
- get_file_content(owner, repo, path, branch): Read file contents
- search_repositories(query, sort, order): Search repositories
- create_repo(name, description, private): Create new repository
- create_issue(owner, repo, title, body): Create an issue
- create_pull_request(owner, repo, head, base, title, body): Create PR
- create_comment(owner, repo, issue_number, body): Add comment

Use these tools to fetch or create GitHub resources. Always provide clear, formatted responses."""


@mcp.prompt("github_learning_prompt")
def github_learning_prompt(topic: str) -> str:
    """Learning prompt for GitHub concepts and best practices."""
    return f"""Teach about this GitHub topic: {topic}

Cover these aspects:
1. Definition and purpose
2. Key concepts and terminology
3. Common use cases and examples
4. Best practices and recommendations
5. Related GitHub features or tools
6. Practical tips for effective usage

Provide clear explanations with examples where helpful. Consider the user's experience level and provide appropriate depth."""


@mcp.prompt("github_workflow_prompt")
def github_workflow_prompt(workflow: str) -> str:
    """Prompt for GitHub workflow guidance."""
    return f"""Guide through this GitHub workflow: {workflow}

Provide step-by-step instructions covering:
1. Prerequisites and setup
2. Detailed process steps
3. Commands or API calls needed
4. Common issues and troubleshooting
5. Verification and success criteria
6. Next steps or related workflows

Be specific and actionable. Include examples and best practices."""


@mcp.resource("file://github_best_practices.txt")
def get_github_best_practices() -> str:
    """Resource with GitHub best practices and guidelines."""
    return """GitHub Best Practices Guide

Repository Management:
• Use clear, descriptive repository names
• Write comprehensive README files
• Include appropriate license files
• Use .gitignore to exclude unnecessary files
• Maintain consistent branch naming conventions

Commit Practices:
• Write clear, descriptive commit messages
• Follow conventional commit format (type: description)
• Keep commits focused and atomic
• Use present tense ("Add feature" not "Added feature")
• Include issue references when applicable

Branch Strategy:
• Use main/master for production code
• Create feature branches for new work
• Use develop for integration testing
• Delete merged branches to keep repository clean
• Protect important branches with required reviews

Pull Request Management:
• Write descriptive PR titles and descriptions
• Include screenshots for UI changes
• Link related issues in PR descriptions
• Request appropriate reviewers
• Address feedback promptly and thoroughly

Issue Management:
• Use clear, actionable issue titles
• Provide detailed reproduction steps for bugs
• Include environment and version information
• Use labels to categorize issues
• Close issues with reference comments when fixed

Collaboration:
• Be respectful in all communications
• Provide constructive feedback
• Help newcomers get started
• Document decisions and discussions
• Follow project contribution guidelines

Security:
• Use strong, unique passwords
• Enable two-factor authentication
• Review access permissions regularly
• Use personal access tokens instead of passwords
• Keep sensitive data out of repositories
• Use Dependabot for vulnerability scanning

Performance:
• Keep repository size reasonable
• Use Git LFS for large files
• Archive inactive repositories
• Monitor API rate limits
• Cache frequently accessed data"""


@mcp.resource("file://github_api_reference.txt")
def get_github_api_reference() -> str:
    """Resource with GitHub API reference information."""
    return """GitHub API Reference Guide

Authentication:
• Personal Access Tokens: Recommended for scripts
• OAuth Apps: For applications with user login
• GitHub Apps: For integration across organizations
• Basic Auth: Username/password (not recommended)

Rate Limits:
• Unauthenticated: 60 requests/hour
• Authenticated: 5,000 requests/hour
• Check rate limit: GET /rate_limit
• Reset time: Unix timestamp in response headers

Common Endpoints:
• User: GET /user, GET /users/{username}
• Repositories: GET /user/repos, GET /repos/{owner}/{repo}
• Commits: GET /repos/{owner}/{repo}/commits
• Issues: GET /repos/{owner}/{repo}/issues
• Pull Requests: GET /repos/{owner}/{repo}/pulls
• Search: GET /search/repositories, GET /search/issues

Response Format:
• JSON responses with standard HTTP status codes
• Pagination with Link header or page parameter
• Error responses include error message
• Use conditional requests with ETag headers

HTTP Methods:
• GET: Retrieve data
• POST: Create new resources
• PUT/PATCH: Update existing resources
• DELETE: Remove resources

Query Parameters:
• per_page: Number of results (max 100)
• page: Page number for pagination
• sort: Sort field (created, updated, comments)
• direction: asc or desc
• state: open, closed, all

Error Handling:
• 200 OK: Successful request
• 201 Created: Resource created successfully
• 400 Bad Request: Invalid parameters
• 401 Unauthorized: Authentication required
• 403 Forbidden: Permission denied
• 404 Not Found: Resource doesn't exist
• 422 Unprocessable Entity: Validation failed
• 429 Too Many Requests: Rate limit exceeded"""


@mcp.resource("file://github_workflow_examples.txt")
def get_github_workflow_examples() -> str:
    """Resource with common GitHub workflow examples."""
    return """GitHub Workflow Examples

1. Feature Development Workflow:
   1. Fork the repository
   2. Clone fork locally: git clone <fork-url>
   3. Create feature branch: git checkout -b feature-name
   4. Make changes and commit: git add . && git commit -m "feat: add feature"
   5. Push to fork: git push origin feature-name
   6. Create Pull Request from fork to upstream
   7. Address feedback and update as needed
   8. Merge when approved

2. Bug Fix Workflow:
   1. Create issue describing the bug
   2. Assign issue to yourself
   3. Create bugfix branch: git checkout -b fix/issue-number-description
   4. Implement fix with tests
   5. Commit with fix prefix: git commit -m "fix: resolve issue #123"
   6. Create PR linking to issue
   7. Ensure tests pass
   8. Merge and close issue

3. Release Workflow:
   1. Update version numbers
   2. Update CHANGELOG.md
   3. Create release branch: git checkout -b release/v1.2.0
   4. Run full test suite
   5. Merge to main branch
   6. Create tag: git tag v1.2.0
   7. Push tag: git push origin v1.2.0
   8. Create GitHub Release with notes

4. Documentation Update Workflow:
   1. Identify documentation gaps
   2. Create docs branch: git checkout -b docs/update-guide
   3. Update documentation files
   4. Review for clarity and accuracy
   5. Commit with docs prefix: git commit -m "docs: update API guide"
   6. Create PR for review
   7. Merge to documentation branch
   8. Deploy documentation if needed

5. Code Review Workflow:
   1. Receive PR notification
   2. Review code changes and logic
   3. Check tests and documentation
   4. Leave constructive feedback
   5. Request changes if needed
   6. Approve when ready
   7. Merge or delegate merge authority

6. Repository Maintenance:
   1. Review and triage new issues
   2. Update labels and milestones
   3. Close stale issues and PRs
   4. Update dependencies
   5. Archive inactive branches
   6. Update documentation
   7. Review and update permissions

7. Security Issue Response:
   1. Receive security report privately
   2. Create security fix branch
   3. Implement fix privately
   4. Coordinate disclosure timeline
   5. Release security update
   6. Publish security advisory
   7. Update public documentation"""


# Run as MCP stdio server
if __name__ == "__main__":
    mcp.run()
