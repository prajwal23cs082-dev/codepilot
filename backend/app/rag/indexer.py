import os
from pathlib import Path
from typing import List, Dict, Any
import uuid

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.core.config import settings

# Initialize Chroma client globally
# It will store data in a persistent directory
chroma_client = chromadb.PersistentClient(path="./chroma_db")

def get_embedding_function():
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY
    )

def is_text_file(file_path: Path) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except UnicodeDecodeError:
        return False
    except Exception:
        return False

def index_repository(project_id: str, workspace_path: str) -> Dict[str, Any]:
    workspace = Path(workspace_path)
    if not workspace.exists():
        raise FileNotFoundError(f"Workspace {workspace_path} does not exist")
        
    documents = []
    
    # Collect files
    for root, dirs, files in os.walk(workspace):
        # exclude hidden directories and standard ignores
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', '__pycache__', 'venv', '.venv')]
        
        for file in files:
            if file.startswith('.') or file.endswith(('.pyc', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.tar', '.gz')):
                continue
                
            file_path = Path(root) / file
            
            if not is_text_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                rel_path = str(file_path.relative_to(workspace))
                
                doc = Document(
                    page_content=content,
                    metadata={"source": rel_path, "project_id": project_id}
                )
                documents.append(doc)
            except Exception as e:
                print(f"Skipping {file_path}: {e}")

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=150,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    if not chunks:
        return {"status": "success", "chunks_indexed": 0}
        
    # Create or get collection
    # Note: we use direct LangChain Chroma or just raw Chroma. 
    # Let's use raw Chroma for better control
    collection = chroma_client.get_or_create_collection(
        name=f"project_{project_id}"
    )
    
    # We could use OpenAIEmbeddings from langchain but it's simpler to use it directly 
    # to embed texts, or let Chroma's built-in embedding function do it if we configure it.
    # Since we need to use a specific model and API key:
    embedding_func = get_embedding_function()
    
    # Generate embeddings and add to Chroma
    texts = [c.page_content for c in chunks]
    metadatas = [c.metadata for c in chunks]
    ids = [str(uuid.uuid4()) for _ in chunks]
    
    embeddings = embedding_func.embed_documents(texts)
    
    # Add in batches
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        collection.add(
            embeddings=embeddings[i:i+batch_size],
            documents=texts[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )
        
    return {"status": "success", "chunks_indexed": len(chunks)}

def retrieve_context(project_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    try:
        collection = chroma_client.get_collection(name=f"project_{project_id}")
    except ValueError:
        return [] # Collection does not exist
        
    embedding_func = get_embedding_function()
    query_embedding = embedding_func.embed_query(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    retrieved = []
    if results['documents']:
        for i in range(len(results['documents'][0])):
            retrieved.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
            
    return retrieved
