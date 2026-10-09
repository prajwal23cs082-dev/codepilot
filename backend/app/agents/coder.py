from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
import json

from app.core.config import settings
from app.agents.state import AgentState
from app.tools.file_tools import read_file, list_files, create_file, edit_file, delete_file
from app.tools.search_tools import search_code
from app.tools.git_tools import git_status, git_diff

def create_coder_tools(project_id: str, workspace_path: str):
    # We bind the workspace_path and project_id to the tools so the agent doesn't need to provide them
    from functools import partial
    
    bound_read_file = tool_wrapper(read_file, workspace_path=workspace_path)
    bound_list_files = tool_wrapper(list_files, workspace_path=workspace_path)
    bound_create_file = tool_wrapper(create_file, workspace_path=workspace_path)
    bound_edit_file = tool_wrapper(edit_file, workspace_path=workspace_path)
    bound_delete_file = tool_wrapper(delete_file, workspace_path=workspace_path)
    bound_git_status = tool_wrapper(git_status, workspace_path=workspace_path)
    bound_git_diff = tool_wrapper(git_diff, workspace_path=workspace_path)
    bound_search_code = tool_wrapper(search_code, project_id=project_id)
    
    return [
        bound_read_file, bound_list_files, bound_create_file, bound_edit_file, 
        bound_delete_file, bound_git_status, bound_git_diff, bound_search_code
    ]

def tool_wrapper(original_tool, **kwargs):
    # This is a hacky way to pre-fill arguments for Langchain tools
    # A better way is using StructuredTool.from_function, but let's keep it simple.
    from langchain_core.tools import StructuredTool
    
    def func(**inner_kwargs):
        return original_tool.invoke({**kwargs, **inner_kwargs})
        
    return StructuredTool.from_function(
        func=func,
        name=original_tool.name,
        description=original_tool.description,
        # We'd need to extract the correct schema here in a full implementation.
        # But LangGraph's ToolExecutor handles this if we use bind_tools with ChatModels
    )

# Since mapping args dynamically is complex with StructuredTool without pydantic models,
# let's just use the raw tools and let the agent provide the paths, but we override it in execution.

def coder_node(state: AgentState):
    llm = ChatOpenAI(model=settings.LLM_MODEL, openai_api_key=settings.OPENAI_API_KEY)
    
    # We will pass the raw tools to the LLM and intercept the execution in the tool node.
    tools = [read_file, list_files, create_file, edit_file, delete_file, search_code, git_status, git_diff]
    llm_with_tools = llm.bind_tools(tools)
    
    sys_prompt = f"""You are an expert AI software engineer.
    Task: {state['task']}
    
    Plan:
    {json.dumps(state.get('plan', {}), indent=2)}
    
    You have tools to read, search, edit, create and delete files.
    When you call tools, you must provide 'workspace_path'='{state['workspace_path']}' and 'project_id'='{state['project_id']}'.
    
    Implement the task step by step. When you are done implementing, return a final response summarizing what you did, and do not call any more tools.
    """
    
    messages = [SystemMessage(content=sys_prompt)] + state['messages']
    
    try:
        response = llm_with_tools.invoke(messages)
        
        return {
            "messages": [response],
            "status": "tool_calls_pending" if response.tool_calls else "coding_complete"
        }
    except Exception as e:
        return {
            "status": "error",
            "errors": [f"Coder failed: {str(e)}"]
        }
