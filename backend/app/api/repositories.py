import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.database import models
from app.schemas.projects import ProjectResponse
from app.services import repository as repo_service

router = APIRouter(prefix="/projects/{project_id}/repository", tags=["repositories"])

@router.post("")
def attach_repository(
    project_id: str,
    repository_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not repository_url and not file:
        raise HTTPException(status_code=400, detail="Must provide repository_url or zip file")

    try:
        workspace_path = ""
        if repository_url:
            workspace_path = repo_service.setup_github_repository(project_id, repository_url)
            project.repository_url = repository_url
        elif file:
            if not file.filename.endswith('.zip'):
                raise HTTPException(status_code=400, detail="Only ZIP files are supported")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                content = file.file.read()
                tmp.write(content)
                tmp_path = tmp.name
                
            workspace_path = repo_service.extract_zip_repository(project_id, tmp_path)
            os.remove(tmp_path)
            project.repository_url = f"local://{file.filename}"

        project.status = "ready"
        db.commit()
        db.refresh(project)
        return {"status": "success", "workspace": workspace_path}

    except Exception as e:
        project.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to setup repository: {str(e)}")

@router.get("/tree")
def get_repository_tree(project_id: str, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    tree = repo_service.get_file_tree(project_id)
    return {"tree": tree}

from app.rag.indexer import index_repository

@router.post("/index")
def trigger_index(project_id: str, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if not project.repository_url:
        raise HTTPException(status_code=400, detail="Repository not attached yet")
        
    workspace = repo_service.get_project_workspace(project_id)
    try:
        project.status = "indexing"
        db.commit()
        
        result = index_repository(project_id, str(workspace))
        
        project.status = "ready"
        db.commit()
        return result
    except Exception as e:
        project.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
