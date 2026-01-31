# GitLab Management Agent

In our group, we use GitLab not only as our version-control tool but also for planning. However, adding and editing issues on the website involves many clicks, and the interface can be slow. So, I decided to build an agent to help us manage issues more efficiently.

This project provides a GitLab management agent that functions as an MCP (Model Context Protocol) server. It allows AI assistants to interact with GitLab repositories to create and update issues, tag them with labels, and assign them to project members. You can add this agent to Cursor to access it locally, or deploy it to an accessible server to give your favorite LLM (like ChatGPT) or any MCP compatible environment access to it.

## Functionalities

The GitLab Management Agent uses MCP to ensure compatibility with all well-known AI assistants. The agent provides several tools:

- **get_labels**: List all available labels in a project.
- **get_assignees**: List project members and their IDs.
- **create_issue**: Create a new issue with a title, label, and optional assignee.
- **update_issue**: Update an existing issue's title, label, or assignee.
- **get_issue**: Retrieve details for a specific issue.
- **get_default_project**: Check the currently configured default project.

## MCP Configuration

Here are two ways to use this agent.

### GitLab Management (Running Locally on Cursor)

If you use Cursor or similar applications, you can run the agent locally. `gitlab_management_agent.py` uses `FastMCP` to build the agent and the `python-gitlab` library to communicate with GitLab.

#### Setup

1. Clone the repository.
2. Create a virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Add the following to your MCP settings in Cursor (e.g., `.cursor/mcp.json` or through the UI).

```json
{
  "mcpServers": {
    "gitlab-management-agent": {
      "command": "/path/to/the/project/.venv/bin/python",
      "args": ["/path/to/your/project/gitlab_management_agent.py"],
      "env": {
        "PYTHONPATH": "/path/to/your/project",
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_TOKEN": "YOUR_GITLAB_TOKEN",
        "GITLAB_PROJECT": "your-username/your-project"
      }
    }
  }
}
```

To allow the agent to access your repositories, a GitLab personal access token is required. You can create one in your GitLab account settings with the appropriate permissions.

### GitLab Management Agent (Running on Hugging Face Spaces)

You can also deploy the GitLab management agent as an MCP server accessible via a URL, allowing it to be used as a tool in AI assistants like Claude, ChatGPT, and other MCP clients. Hugging Face Spaces is compatible with MCP, providing a free way to host your server.

A Gradio space on Hugging Face supports MCP natively. I have rewritten the agent using the `gradio` library in `gitlab-management-agent-hf.py`.

#### Deployment

1. Create a new Gradio Space on Hugging Face.
2. Upload `gitlab-management-agent-hf.py` and `requirements-hf.txt`, renaming them to `app.py` and `requirements.txt` respectively.
3. Define the following Secrets in your Space settings:
   - `GITLAB_TOKEN`: Your GitLab access token.
   - `GITLAB_PROJECT`: The default GitLab project (optional).
![agent-page](./fig/agent.png)


4. Ensure the Space is public or accessible to your client ([here](https://huggingface.co/settings/mcp)).

Now you can configure your client to access the MCP server. To add the server to Cursor, add the following to your MCP settings:

```json
{
  "mcpServers": {
    "gitlab-management-agent-hf": {
      "url": "https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_HUGGINGFACE_TOKEN"
      }
    }
  }
}
```

You will need to provide `YOUR_HUGGINGFACE_TOKEN`, which you can create in your Hugging Face settings.

