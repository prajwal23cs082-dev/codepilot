from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

from app.agents.state import AgentState
from app.agents.planner import plan_node
from app.agents.coder import coder_node
from app.agents.tools_executor import tool_node
from app.agents.debugger import run_tests_node, debugger_node

def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", plan_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("tester", run_tests_node)
    workflow.add_node("debugger", debugger_node)
    
    # Edges from Planner
    workflow.add_edge("planner", "coder")
    
    # Edges from Coder
    def coder_router(state: AgentState):
        if state["status"] == "tool_calls_pending":
            return "tools"
        return "tester" # Go to tester when coding is complete
        
    workflow.add_conditional_edges(
        "coder",
        coder_router,
        {
            "tools": "tools",
            "tester": "tester"
        }
    )
    
    # Edges from Tools
    workflow.add_edge("tools", "coder")
    
    # Edges from Tester
    def tester_router(state: AgentState):
        if state["status"] == "tests_passed":
            return END
        return "debugger"
        
    workflow.add_conditional_edges(
        "tester",
        tester_router,
        {
            END: END,
            "debugger": "debugger"
        }
    )
    
    # Edges from Debugger
    def debugger_router(state: AgentState):
        if state["status"] == "max_iterations_reached":
            return END
        return "coder"
        
    workflow.add_conditional_edges(
        "debugger",
        debugger_router,
        {
            "coder": "coder",
            END: END
        }
    )
    
    workflow.set_entry_point("planner")
    return workflow.compile()

# Global graph instance
agent_graph = create_agent_graph()
