import gitlab
import os
import gradio as gr

# These should be set as Secrets in the Hugging Face Space settings
GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
DEFAULT_PROJECT = os.getenv("GITLAB_PROJECT")
# ---------------------

def get_project(gl: gitlab.Gitlab, project_name: str = None):
    """Helper to get project by name or use default."""
    target = project_name or DEFAULT_PROJECT
    if not target:
        raise ValueError("Project name must be provided or GITLAB_PROJECT environment variable must be set.")
    return gl.projects.get(target)

def get_default_project() -> str:
    """
    Get the name of the default GitLab project set in the environment.
    """
    if DEFAULT_PROJECT:
        return f"The default project is: {DEFAULT_PROJECT}"
    return "No default project is set in the GITLAB_PROJECT environment variable."

def get_labels(project_name: str = None) -> str:
    """
    Get the list of all available labels in the repository. 
    Use this tool BEFORE creating an issue to ensure you know the available labels and use an existing label 
    if it is applicable (e.g., sprint-backlog or product-backlog, etc.).
    """
    if not GITLAB_TOKEN:
        return "Error: GITLAB_TOKEN environment variable must be set."
    try:
        gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
        project = get_project(gl, project_name)
        labels = project.labels.list(per_page=100, get_all=True)
        label_names = [l.name for l in labels]
        return f"Available labels: {', '.join(label_names)}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_assignees(project_name: str = None) -> str:
    """
    Extract all available assignees (project members) from the GitLab repository.
    Use this tool to find the correct user ID or username to assign an issue to.
    """
    if not GITLAB_TOKEN:
        return "Error: GITLAB_TOKEN environment variable must be set."
    try:
        gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
        project = get_project(gl, project_name)
        members = project.members.list(all=True)
        member_info = [f"{m.name} (@{m.username}, ID: {m.id})" for m in members]
        return f"Found {len(member_info)} members: {', '.join(member_info)}"
    except Exception as e:
        return f"Error: {str(e)}"

def create_issue(title: str, label: str, assignee_id: int = None, project_name: str = None) -> str:
    """
    Add a new issue to the repository.
    
    Args:
        title: The title of the issue.
        label: The EXACT label name.
        assignee_id: The ID of the user to assign the issue to (optional).
        project_name: The name or ID of the GitLab project (optional).
    """
    if not GITLAB_TOKEN:
        return "Error: GITLAB_TOKEN environment variable must be set."
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

def update_issue(issue_id: int, title: str = None, label: str = None, assignee_id: int = None, project_name: str = None) -> str:
    """
    Update an existing issue's title, label, or assignee.
    
    Args:
        issue_id: The internal ID (IID) of the issue to update.
        title: The new title for the issue (optional).
        label: The new EXACT label name to apply (optional).
        assignee_id: The ID of the user to assign the issue to (optional).
        project_name: The name or ID of the GitLab project (optional).
    """
    if not GITLAB_TOKEN:
        return "Error: GITLAB_TOKEN environment variable must be set."
    try:
        gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
        project = get_project(gl, project_name)
        issue = project.issues.get(issue_id)
        
        if title:
            issue.title = title
        if label:
            issue.labels = [label]
        if assignee_id is not None:
            issue.assignee_ids = [assignee_id] if assignee_id > 0 else []
            
        issue.save()
        return f"Issue #{issue_id} updated successfully: {issue.web_url}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_issue(issue_id: int, project_name: str = None) -> str:
    """
    Get information about a specific issue by its internal ID (IID).
    
    Args:
        issue_id: The internal ID (IID) of the issue.
        project_name: The name or ID of the GitLab project (optional).
    """
    if not GITLAB_TOKEN:
        return "Error: GITLAB_TOKEN environment variable must be set."
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

# Create Gradio app with native MCP support
with gr.Blocks(title="GitLab Management MCP Agent") as demo:
    gr.Markdown("# GitLab Management MCP Agent")
    gr.Markdown("This Space acts as an MCP server for GitLab management. Connect to it using its URL.")
    
    with gr.Tab("Get Labels"):
        project_labels = gr.Textbox(label="Project Name (Optional)")
        btn_labels = gr.Button("Get Labels")
        out_labels = gr.Textbox(label="Result")
        btn_labels.click(get_labels, inputs=[project_labels], outputs=out_labels)
        
    with gr.Tab("Default Project"):
        btn_default = gr.Button("Show Default Project")
        out_default = gr.Textbox(label="Result")
        btn_default.click(get_default_project, inputs=[], outputs=out_default)
        
    with gr.Tab("Get Assignees"):
        project_assignees = gr.Textbox(label="Project Name (Optional)")
        btn_assignees = gr.Button("Get Assignees")
        out_assignees = gr.Textbox(label="Result")
        btn_assignees.click(get_assignees, inputs=[project_assignees], outputs=out_assignees)
        
    with gr.Tab("Create Issue"):
        project_create = gr.Textbox(label="Project Name (Optional)")
        title_in = gr.Textbox(label="Title")
        label_in = gr.Textbox(label="Label")
        assignee_in = gr.Number(label="Assignee ID (Optional)", precision=0)
        btn_create = gr.Button("Create Issue")
        out_create = gr.Textbox(label="Result")
        btn_create.click(create_issue, inputs=[title_in, label_in, assignee_in, project_create], outputs=out_create)
        
    with gr.Tab("Update Issue"):
        project_update = gr.Textbox(label="Project Name (Optional)")
        issue_id_up = gr.Number(label="Issue IID", precision=0)
        title_up = gr.Textbox(label="New Title (Optional)")
        label_up = gr.Textbox(label="New Label (Optional)")
        assignee_up = gr.Number(label="New Assignee ID (Optional)", precision=0)
        btn_update = gr.Button("Update Issue")
        out_update = gr.Textbox(label="Result")
        btn_update.click(update_issue, inputs=[issue_id_up, title_up, label_up, assignee_up, project_update], outputs=out_update)
        
    with gr.Tab("Get Issue"):
        project_get = gr.Textbox(label="Project Name (Optional)")
        issue_id_get = gr.Number(label="Issue IID", precision=0)
        btn_get = gr.Button("Get Issue Details")
        out_get = gr.Textbox(label="Result")
        btn_get.click(get_issue, inputs=[issue_id_get, project_get], outputs=out_get)

if __name__ == "__main__":
    # Launching with mcp=True (Gradio 5.0+ feature)
    demo.launch(mcp_server=True)
