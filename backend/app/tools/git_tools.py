from langchain_core.tools import tool
from git import Repo
import os

@tool
def git_status(workspace_path: str) -> str:
    """Return the git status of the repository."""
    try:
        if not os.path.exists(os.path.join(workspace_path, '.git')):
            # Initialize git if not present to track changes
            repo = Repo.init(workspace_path)
            repo.git.add(A=True)
            repo.index.commit("Initial commit")
            return "Initialized git repository and committed all files."

        repo = Repo(workspace_path)
        return repo.git.status()
    except Exception as e:
        return f"Error running git status: {str(e)}"

@tool
def git_diff(workspace_path: str) -> str:
    """Return the git diff of the current changes."""
    try:
        repo = Repo(workspace_path)
        return repo.git.diff()
    except Exception as e:
        return f"Error running git diff: {str(e)}"
