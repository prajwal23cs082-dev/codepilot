import subprocess
import os
import shlex
from app.core.config import settings

def run_in_sandbox(workspace_path: str, command: str, timeout: int = None) -> dict:
    """
    Executes a command safely.
    In a real production environment, this should spin up an ephemeral Docker container.
    """
    if timeout is None:
        timeout = settings.SANDBOX_TIMEOUT
        
    try:
        # Note: If docker is available, we could do:
        # docker run --rm -v {workspace_path}:/app -w /app python:3.11-slim {command}
        
        # For this prototype, we'll run it locally via subprocess with a timeout.
        # This allows it to work inside the outer Docker compose environment.
        process = subprocess.run(
            command,
            shell=True,
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            "status": "success" if process.returncode == 0 else "failed",
            "exit_code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "duration": 0 # We'd measure time accurately here
        }
    except subprocess.TimeoutExpired as e:
        return {
            "status": "failed",
            "exit_code": -1,
            "stdout": e.stdout.decode('utf-8') if e.stdout else "",
            "stderr": f"Command timed out after {timeout} seconds",
            "duration": timeout
        }
    except Exception as e:
        return {
            "status": "error",
            "exit_code": -2,
            "stdout": "",
            "stderr": str(e),
            "duration": 0
        }
