import gitlab
import os
from fastmcp import FastMCP

GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
DEFAULT_PROJECT = os.getenv("GITLAB_PROJECT")
# ---------------------

# Create a FastMCP instance
mcp = FastMCP("gitlab-management-agent")

def get_project(gl: gitlab.Gitlab, project_name: str = None):
    """Helper to get project by name or use default."""
    target = project_name or DEFAULT_PROJECT
    if not target:
        raise ValueError("Project name must be provided or GITLAB_PROJECT environment variable must be set.")
    return gl.projects.get(target)

@mcp.tool()
def get_default_project() -> str:
    """
    Get the name of the default GitLab project set in the environment.
    """
    if DEFAULT_PROJECT:
        return f"The default project is: {DEFAULT_PROJECT}"
    return "No default project is set in the GITLAB_PROJECT environment variable."

@mcp.tool()
def get_labels(project_name: str = None) -> str:
    """
    Get the list of all available labels in the repository. 
    Use this tool BEFORE creating an issue to ensure you know the available labels and use an existing label 
    if it is applicable (e.g., sprint-backlog or product-backlog, etc.).

    Args:
        project_name: Optional. The name or ID of the GitLab project. If not provided, uses the default project.
    """
    try:
        gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
        project = get_project(gl, project_name)
        labels = project.labels.list(per_page=100, get_all=True)
        label_names = [l.name for l in labels]
        return f"Available labels: {', '.join(label_names)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_assignees(project_name: str = None) -> str:
    """
    Extract all available assignees (project members) from the GitLab repository.
    Use this tool to find the correct user ID or username to assign an issue to.

    Args:
        project_name: Optional. The name or ID of the GitLab project. If not provided, uses the default project.
    """
    try:
        gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
        project = get_project(gl, project_name)
        members = project.members.list(all=True)
        member_info = [f"{m.name} (@{m.username}, ID: {m.id})" for m in members]
        return f"Found {len(member_info)} members: {', '.join(member_info)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def create_issue(title: str, label: str, assignee_id: int = None, project_name: str = None) -> str:
    """
    Add a new issue to the repository.
    You MUST be sure about the label, if not, call get_labels first and suggest the user to use an existing label. 
    Only after the user confirms the label, you can create the issue.

    You MUST be sure about the assignee, if not, ask the user to provide the assignee. You can call get_assignees first to find the correct ID for a person.
    If the user confirms there is no assignee, you can leave it blank.
    
    Args:
        title: The title of the issue.
        label: The EXACT label name. If you are unsure of the exact label name, call get_labels first to find the correct match.
        assignee_id: The ID of the user to assign the issue to. Call get_assignees to find the correct ID for a person.
        project_name: Optional. The name or ID of the GitLab project. If not provided, uses the default project.
    """
    try:
        gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
        project = get_project(gl, project_name)
        
        issue_data = {
            'title': title,
            'labels': [label]
        }
        if assignee_id:
            issue_data['assignee_ids'] = [assignee_id]
            
        issue = project.issues.create(issue_data)
        
        return f"Issue created successfully: {issue.web_url}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def update_issue(issue_id: int, title: str = None, label: str = None, assignee_id: int = None, project_name: str = None) -> str:
    """
    Update an existing issue's title, label, or assignee.
    
    Args:
        issue_id: The internal ID (IID) of the issue to update (e.g., 1086).
        title: The new title for the issue (optional).
        label: The new EXACT label name to apply (optional).
        assignee_id: The ID of the user to assign the issue to (optional).
        project_name: Optional. The name or ID of the GitLab project. If not provided, uses the default project.
    """
    try:
        gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
        project = get_project(gl, project_name)
        issue = project.issues.get(issue_id)
        
        if title:
            issue.title = title
        if label:
            issue.labels = [label]
        if assignee_id is not None:
            # Using assignee_ids (list) for consistency with create_issue
            issue.assignee_ids = [assignee_id] if assignee_id > 0 else []
            
        issue.save()
        return f"Issue #{issue_id} updated successfully: {issue.web_url}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_issue(issue_id: int, project_name: str = None) -> str:
    """
    Get information about a specific issue by its internal ID (IID).
    
    Args:
        issue_id: The internal ID (IID) of the issue (e.g., 1086).
        project_name: Optional. The name or ID of the GitLab project. If not provided, uses the default project.
    """
    try:
        gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
        project = get_project(gl, project_name)
        issue = project.issues.get(issue_id)
        
        info = [
            f"Title: {issue.title}",
            f"IID: {issue.iid}",
            f"Status: {issue.state}",
            f"Labels: {', '.join(issue.labels)}",
            f"Assignees: {', '.join([a['name'] for a in issue.assignees])}",
            f"Web URL: {issue.web_url}"
        ]
        return "\n".join(info)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(
        transport="sse", 
        host="0.0.0.0", 
        port=7860
    )
