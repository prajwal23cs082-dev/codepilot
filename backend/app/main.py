from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CodePilot API",
    description="API for CodePilot Autonomous AI Software Engineer",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import projects, tasks, repositories, agent

app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(repositories.router)
app.include_router(agent.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
