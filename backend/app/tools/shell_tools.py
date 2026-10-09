from langchain_core.tools import tool
from app.execution.sandbox import run_in_sandbox

@tool
def run_command(workspace_path: str, command: str) -> str:
    """Run a shell command inside the sandbox."""
    result = run_in_sandbox(workspace_path, command)
    
    output = f"Exit code: {result['exit_code']}\n"
    if result['stdout']:
        output += f"STDOUT:\n{result['stdout']}\n"
    if result['stderr']:
        output += f"STDERR:\n{result['stderr']}\n"
        
    return output
