from langchain_core.messages import ToolMessage
import json

from app.agents.state import AgentState
from app.tools.file_tools import read_file, list_files, create_file, edit_file, delete_file
from app.tools.search_tools import search_code
from app.tools.git_tools import git_status, git_diff
from app.tools.test_tools import run_tests
from app.tools.shell_tools import run_command

# Map tool names to functions
TOOL_MAP = {
    "read_file": read_file,
    "list_files": list_files,
    "create_file": create_file,
    "edit_file": edit_file,
    "delete_file": delete_file,
    "search_code": search_code,
    "git_status": git_status,
    "git_diff": git_diff,
    "run_tests": run_tests,
    "run_command": run_command
}

def tool_node(state: AgentState):
    """Executes tools called by the agent."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if not last_message.tool_calls:
        return {"status": "continue"}
        
    tool_responses = []
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Inject context if not present, though we instructed the LLM to provide them
        if "workspace_path" not in tool_args and tool_name in ["read_file", "list_files", "create_file", "edit_file", "delete_file", "git_status", "git_diff", "run_tests", "run_command"]:
            tool_args["workspace_path"] = state["workspace_path"]
            
        if "project_id" not in tool_args and tool_name == "search_code":
            tool_args["project_id"] = state["project_id"]
            
        try:
            if tool_name in TOOL_MAP:
                result = TOOL_MAP[tool_name].invoke(tool_args)
            else:
                result = f"Error: Tool {tool_name} not found."
        except Exception as e:
            result = f"Error executing {tool_name}: {str(e)}"
            
        tool_responses.append(ToolMessage(
            content=str(result),
            name=tool_name,
            tool_call_id=tool_call["id"]
        ))
        
    return {
        "messages": tool_responses,
        "status": "tools_executed"
    }
