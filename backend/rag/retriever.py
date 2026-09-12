# backend/rag/retriever.py
from typing import List, Dict, Any
from backend.rag.vector_store import VectorStore

class Retriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        
    def retrieve_relevant_evidence(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve relevant evidence chunks based on a query.
        Returns a list of chunk metadata dictionaries including the text and similarity score.
        """
        results = self.vector_store.similarity_search(query, k=k)
        
        evidence = []
        for chunk_meta, distance in results:
            # Copy to avoid mutating the original store
            evidence_item = dict(chunk_meta)
            evidence_item["similarity_score"] = distance
            evidence.append(evidence_item)
            
        return evidence
