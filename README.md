
# CodePilot — Autonomous AI Software Engineer

## Problem
Modern AI coding assistants (like Copilot) are essentially advanced autocomplete tools. They require constant developer supervision, line-by-line prompting, and manual verification. They cannot autonomously plan a complex task, explore an unfamiliar codebase, execute tests, and self-correct when things fail.

## Solution
**CodePilot** is an autonomous AI software engineer. You give it a high-level task (e.g., "Add JWT authentication to this project"), and it takes over. It analyzes your repository using semantic search (RAG), formulates a structured execution plan, uses tools to navigate and modify your code, runs your tests inside a secure sandbox, and automatically debugs and fixes any failures before presenting you with a final, verified Git diff.

## Features
- **Semantic Codebase Understanding**: Ingests and indexes entire repositories using ChromaDB and LangChain.
- **Autonomous Planning**: Breaks down complex tasks into structured, actionable steps.
- **Agentic Tool Usage**: Navigates files, reads code, edits files, and interacts with Git autonomously.
- **Self-Correction Loop**: Executes tests, analyzes stack traces on failure, and iteratively fixes the code until all tests pass.
- **Agent Observability**: Real-time streaming of the agent's "thought process", tool calls, and state transitions.
- **Evaluation Framework**: Built-in metrics dashboard to track success rates, iterations, latency, and tool accuracy.

## Architecture
CodePilot uses a modern decoupled architecture:
1. **Frontend**: React + Vite + TypeScript, styled with Tailwind CSS for a dark-mode IDE experience.
2. **Backend**: FastAPI orchestrates the LangGraph state machine, database connections, and API endpoints.
3. **Agent Brain**: LangGraph manages the cyclical workflow of Planning -> Coding -> Testing -> Debugging.
4. **Memory & RAG**: ChromaDB handles semantic search across the codebase.
5. **Database**: PostgreSQL (or SQLite for local dev) stores agent runs, tool traces, and project metadata.
6. **Execution**: A subprocess-based sandbox (designed to wrap Docker) safely executes arbitrary code and tests.

## Agent Workflow
`Planner -> Coder -> Tool Executor -> Tester -> Debugger (loop back to Coder)`

1. **Task Analyzer**: Understands the user intent.
2. **Planner**: Creates a step-by-step JSON plan and identifies likely affected files.
3. **Coder**: Uses tools (`read_file`, `search_code`, `edit_file`) to implement the changes.
4. **Tester**: Runs `pytest` inside the sandbox.
5. **Debugger**: If tests fail, it analyzes the stderr/stdout, updates the context, and instructs the Coder to try again (up to a configurable max iterations).

## Tech Stack
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS v4, React Router, Recharts, Lucide-React.
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Pydantic, LangChain, LangGraph, ChromaDB, GitPython.
- **Infrastructure**: Docker, Docker Compose, PostgreSQL.

## Installation
1. Clone the repository.
2. Ensure you have Node.js 20+ and Python 3.11+ installed.
3. Create a `.env` file (see below).

## Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
DATABASE_URL=sqlite:///./codepilot.db
EMBEDDING_MODEL=text-embedding-3-small
MAX_AGENT_ITERATIONS=5
SANDBOX_TIMEOUT=60
MAX_FILE_SIZE_MB=50
```

## Running Locally
**Backend:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Example Task
1. Go to the Dashboard and create a new project.
2. Upload the `evaluation/sample_projects/demo_fastapi.zip` repository.
3. Click "Build Code Index".
4. Enter the task: `"Add JWT authentication to the user API and fix the failing test."`
5. Watch the agent plan, code, test, fail, self-correct, and eventually succeed!

## Tool Architecture
Tools are implemented using LangChain's `@tool` decorator. The agent is bound to tools like `read_file`, `edit_file`, `search_code`, and `run_tests`. The `Tool Executor` node in LangGraph intercepts these calls, executes them securely, and passes the results back to the LLM.

## RAG Architecture
When a repository is attached, the `indexer.py` service walks the directory tree, chunks text files using `RecursiveCharacterTextSplitter`, generates embeddings via OpenAI, and stores them in a persistent ChromaDB collection. The agent uses the `search_code` tool to perform similarity searches against this database.

## Self-Correction
CodePilot doesn't just write code and hope it works. It runs `run_tests()`. If the exit code is non-zero, the `Debugger` node takes the test output, analyzes the stack trace, and feeds a detailed correction strategy back into the `Coder` node.

## Evaluation
The Evaluation Dashboard tracks key metrics:
- Task Success Rate
- Average Iterations (Self-correction loops)
- Average Latency
- Tool Usage Accuracy

## Security
- **Sandbox**: Test execution is wrapped in a sandbox (subprocess with strict timeouts locally, designed for Docker in prod).
- **No Path Traversal**: Workspace paths are strictly isolated per project.
- **Secrets Management**: API keys are handled via environment variables and never logged or sent to the frontend.

## Limitations
- Advanced CPU/Memory cgroups require a Linux host running Docker.
- Semantic search is limited by the context window of the embedding model.
- Very large repositories may take a while to index.

## Future Improvements
- Multi-agent collaboration (e.g., a dedicated Frontend Agent and Backend Agent).
- Direct GitHub PR integration (open PRs instead of just showing diffs).
- More robust static analysis before running tests.
- Support for Claude 3.5 Sonnet and local models via Ollama.
