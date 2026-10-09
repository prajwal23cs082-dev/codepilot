from typing import Annotated, TypedDict, List, Optional, Any
from operator import add

class AgentState(TypedDict):
    task: str
    project_id: str
    workspace_path: str
    plan: Optional[dict]
    current_step: Optional[str]
    retrieved_context: List[str]
    proposed_changes: Optional[str]
    test_results: Optional[dict]
    errors: List[str]
    iteration: int
    max_iterations: int
    messages: Annotated[List[Any], add]
    status: str
    final_report: Optional[str]
