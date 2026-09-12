# backend/rag/chunker.py
from typing import Dict, Any, List
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text: str, paper_metadata: Dict[str, Any], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict[str, Any]]:
    """Split text into smaller chunks and attach metadata."""
    if not text.strip():
        return []
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks_text = splitter.split_text(text)
    
    chunks = []
    for i, chunk_text in enumerate(chunks_text):
        chunk_meta = {
            "text": chunk_text,
            "paper_id": paper_metadata.get("paper_id"),
            "title": paper_metadata.get("title"),
            "source": paper_metadata.get("source"),
            "url": paper_metadata.get("url"),
            "chunk_index": i
        }
        chunks.append(chunk_meta)
        
    return chunks
