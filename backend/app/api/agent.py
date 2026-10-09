from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import json

from app.database.session import get_db
from app.database import models
from app.agents.graph import agent_graph
from app.services.repository import get_project_workspace

router = APIRouter(prefix="/tasks/{task_id}", tags=["agent"])

def run_agent_task(task_id: str, db: Session):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return
        
    project = task.project
    workspace = get_project_workspace(project.id)
    
    # Create agent run record
    agent_run = models.AgentRun(task_id=task_id)
    db.add(agent_run)
    
    task.status = "running"
    db.commit()
    db.refresh(agent_run)
    
    # Initial state
    initial_state = {
        "task": task.description,
        "project_id": project.id,
        "workspace_path": str(workspace),
        "plan": None,
        "current_step": "init",
        "retrieved_context": [],
        "proposed_changes": None,
        "test_results": None,
        "errors": [],
        "iteration": 1,
        "max_iterations": 5,
        "messages": [],
        "status": "started",
        "final_report": None
    }
    
    try:
        # We can stream the output or run it completely.
        # For background execution, we use invoke or stream.
        # To persist steps to the DB, we can use graph.stream
        for output in agent_graph.stream(initial_state):
            for key, value in output.items():
                # Save step to DB
                step = models.AgentStep(
                    run_id=agent_run.id,
                    step_type=key,
                    content=json.dumps(value.get("status", "unknown")),
                )
                db.add(step)
                db.commit()
                
        # Final state
        agent_run.status = "completed"
        task.status = "completed"
        db.commit()
        
    except Exception as e:
        agent_run.status = "failed"
        task.status = "failed"
        db.commit()

@router.post("/start")
def start_agent(task_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    background_tasks.add_task(run_agent_task, task_id, db)
    return {"status": "started"}

@router.get("/trace")
def get_trace(task_id: str, db: Session = Depends(get_db)):
    # Returns the agent run details
    runs = db.query(models.AgentRun).filter(models.AgentRun.task_id == task_id).all()
    
    traces = []
    for run in runs:
        steps = db.query(models.AgentStep).filter(models.AgentStep.run_id == run.id).all()
        traces.append({
            "run_id": run.id,
            "status": run.status,
            "iterations": run.iterations,
            "steps": [{"type": s.step_type, "content": s.content, "created_at": s.created_at} for s in steps]
        })
        
    return {"traces": traces}
