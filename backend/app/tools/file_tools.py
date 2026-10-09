import os
from pathlib import Path
from typing import List
from langchain_core.tools import tool
from app.services.repository import get_project_workspace

# We need a way to pass the project_id to these tools. 
# In LangGraph, we can bind arguments or pass state.
# Alternatively, we can use a class-based approach or inject the workspace path.
# For simplicity, these functions will take `workspace_path` as an argument.

@tool
def read_file(workspace_path: str, file_path: str) -> str:
    """Read the contents of a file."""
    full_path = Path(workspace_path) / file_path
    if not full_path.exists():
        return f"Error: File {file_path} does not exist."
    if not full_path.is_file():
        return f"Error: {file_path} is not a file."
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def list_files(workspace_path: str, directory: str = ".") -> str:
    """List files in a directory."""
    full_path = Path(workspace_path) / directory
    if not full_path.exists():
        return f"Error: Directory {directory} does not exist."
    if not full_path.is_dir():
        return f"Error: {directory} is not a directory."
        
    try:
        items = os.listdir(full_path)
        return "\n".join(sorted(items))
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@tool
def create_file(workspace_path: str, file_path: str, content: str) -> str:
    """Create a new file with the given content."""
    full_path = Path(workspace_path) / file_path
    if full_path.exists():
        return f"Error: File {file_path} already exists. Use edit_file instead."
        
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully created {file_path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

@tool
def edit_file(workspace_path: str, file_path: str, new_content: str) -> str:
    """Replace the entire contents of a file."""
    full_path = Path(workspace_path) / file_path
    if not full_path.exists():
        return f"Error: File {file_path} does not exist. Use create_file instead."
        
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"Successfully updated {file_path}"
    except Exception as e:
        return f"Error updating file: {str(e)}"

@tool
def delete_file(workspace_path: str, file_path: str) -> str:
    """Delete a file."""
    full_path = Path(workspace_path) / file_path
    if not full_path.exists():
        return f"Error: File {file_path} does not exist."
        
    try:
        full_path.unlink()
        return f"Successfully deleted {file_path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"
