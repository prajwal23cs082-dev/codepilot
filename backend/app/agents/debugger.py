from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
import json

from app.core.config import settings
from app.agents.state import AgentState
from app.tools.test_tools import run_tests

def run_tests_node(state: AgentState):
    """Runs tests and stores results."""
    try:
        result = run_tests.invoke({"workspace_path": state["workspace_path"]})
        
        # Simple heuristic to determine if tests passed
        passed = "FAILED" not in result and "ERRORS" not in result and "Exit code: 0" in result
        
        return {
            "test_results": {
                "output": result,
                "passed": passed
            },
            "status": "tests_passed" if passed else "tests_failed"
        }
    except Exception as e:
        return {
            "status": "error",
            "errors": [f"Test runner failed: {str(e)}"]
        }

def debugger_node(state: AgentState):
    """Analyzes test failures and proposes a fix strategy."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, openai_api_key=settings.OPENAI_API_KEY)
    
    sys_prompt = f"""You are an expert AI software debugger.
    The tests have failed. Analyze the failure and provide instructions to the coder on how to fix it.
    
    Task: {state['task']}
    
    Test Results:
    {state.get('test_results', {}).get('output', 'No output')}
    
    Iteration: {state['iteration']}/{state['max_iterations']}
    
    Provide a clear, concise analysis and a specific strategy to fix the issue.
    """
    
    try:
        response = llm.invoke([SystemMessage(content=sys_prompt)] + state['messages'])
        
        # Increment iteration counter
        next_iter = state["iteration"] + 1
        
        if next_iter > state["max_iterations"]:
            status = "max_iterations_reached"
        else:
            status = "debugging_complete"
            
        return {
            "messages": [response],
            "iteration": next_iter,
            "status": status
        }
    except Exception as e:
        return {
            "status": "error",
            "errors": [f"Debugger failed: {str(e)}"]
        }
