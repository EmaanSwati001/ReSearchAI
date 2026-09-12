# backend/rag/vector_store.py
import faiss
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the local FAISS vector store and embedding model."""
        self.model = SentenceTransformer(model_name)
        # all-MiniLM-L6-v2 has an embedding dimension of 384
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks_metadata: List[Dict[str, Any]] = []

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Embed and add chunks to the FAISS index."""
        if not chunks:
            return
            
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # Ensure it's float32 for FAISS
        embeddings = np.array(embeddings).astype('float32')
        
        self.index.add(embeddings)
        self.chunks_metadata.extend(chunks)

    def similarity_search(self, query: str, k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        """Search for the most similar chunks to the query."""
        if self.index.ntotal == 0:
            return []
            
        query_embedding = self.model.encode([query], convert_to_numpy=True).astype('float32')
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                results.append((self.chunks_metadata[idx], float(distances[0][i])))
                
        return results
