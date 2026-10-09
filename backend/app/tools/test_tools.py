from langchain_core.tools import tool
from app.execution.sandbox import run_in_sandbox

@tool
def run_tests(workspace_path: str, test_command: str = "pytest") -> str:
    """Run tests in the repository."""
    result = run_in_sandbox(workspace_path, test_command)
    
    # In a real implementation, we would parse pytest output to get passed/failed metrics.
    # We can just return the raw output for the agent.
    output = f"Test Command: {test_command}\n"
    output += f"Exit code: {result['exit_code']}\n"
    if result['stdout']:
        output += f"STDOUT:\n{result['stdout']}\n"
    if result['stderr']:
        output += f"STDERR:\n{result['stderr']}\n"
        
    return output
