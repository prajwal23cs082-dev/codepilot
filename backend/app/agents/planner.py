from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import json

from app.core.config import settings
from app.agents.state import AgentState

class PlanStep(BaseModel):
    id: int = Field(description="Step ID")
    description: str = Field(description="Description of what needs to be done")
    status: str = Field(default="pending", description="Status of the step")

class Plan(BaseModel):
    goal: str = Field(description="The main goal of the task")
    steps: List[PlanStep] = Field(description="List of steps to achieve the goal")
    files_likely_affected: List[str] = Field(description="List of files that are likely to be affected")
    risk: str = Field(description="Risk level of the changes: low, medium, high")

def plan_node(state: AgentState):
    llm = ChatOpenAI(model=settings.LLM_MODEL, openai_api_key=settings.OPENAI_API_KEY)
    
    parser = PydanticOutputParser(pydantic_object=Plan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI software architect. Create a structured implementation plan for the user's task.\n{format_instructions}"),
        ("user", "Task: {task}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        plan = chain.invoke({
            "task": state["task"],
            "format_instructions": parser.get_format_instructions()
        })
        
        return {
            "plan": plan.dict(),
            "status": "planning_complete",
            "messages": [("ai", f"Created plan: {json.dumps(plan.dict())}")]
        }
    except Exception as e:
        return {
            "status": "error",
            "errors": [f"Planner failed: {str(e)}"]
        }
