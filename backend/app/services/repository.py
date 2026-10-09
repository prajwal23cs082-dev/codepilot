import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from git import Repo

def get_project_workspace(project_id: str) -> Path:
    # Store repos in a 'workspaces' directory
    workspace_dir = Path(os.getcwd()) / "workspaces" / project_id
    return workspace_dir

def setup_github_repository(project_id: str, repo_url: str):
    workspace = get_project_workspace(project_id)
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    
    # Clone the repo
    Repo.clone_from(repo_url, workspace)
    return str(workspace)

def extract_zip_repository(project_id: str, zip_path: str):
    workspace = get_project_workspace(project_id)
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(workspace)
    
    # Check if there is a single root folder in the zip
    items = list(workspace.iterdir())
    if len(items) == 1 and items[0].is_dir():
        # Move all contents up one level
        inner_dir = items[0]
        for item in inner_dir.iterdir():
            shutil.move(str(item), str(workspace))
        inner_dir.rmdir()
        
    return str(workspace)

def get_file_tree(project_id: str):
    workspace = get_project_workspace(project_id)
    if not workspace.exists():
        return []
    
    def _build_tree(dir_path: Path, rel_path: str = ""):
        tree = []
        for path in sorted(dir_path.iterdir(), key=lambda x: (x.is_file(), x.name)):
            # Skip hidden files/folders and specific directories
            if path.name.startswith('.') or path.name in ('node_modules', '__pycache__', 'venv', '.venv'):
                continue
            
            node_rel = os.path.join(rel_path, path.name)
            node = {
                "name": path.name,
                "path": node_rel,
                "type": "file" if path.is_file() else "directory"
            }
            if path.is_dir():
                node["children"] = _build_tree(path, node_rel)
            tree.append(node)
        return tree
    
    return _build_tree(workspace)
