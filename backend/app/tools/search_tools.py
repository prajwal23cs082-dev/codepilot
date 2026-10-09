from langchain_core.tools import tool
from app.rag.indexer import retrieve_context

@tool
def search_code(project_id: str, query: str) -> str:
    """Semantic search the codebase for a query."""
    results = retrieve_context(project_id, query)
    
    if not results:
        return "No relevant code found."
        
    formatted = []
    for i, res in enumerate(results):
        formatted.append(f"--- Result {i+1} (Source: {res['metadata'].get('source', 'Unknown')}) ---")
        formatted.append(res['content'])
        
    return "\n\n".join(formatted)
