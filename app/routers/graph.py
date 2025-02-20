from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

import vertexai
from services.graph_storage import GraphStorageService
from services.vertex import VertexAIService
from services.cloud_storage import CloudStorageService  # Used to retrieve file content

router = APIRouter(prefix="/graph")

class GraphQuery(BaseModel):
    query: str
    top_k: Optional[int] = 3

# Initialize services
graph_storage = GraphStorageService()
vertex_service = VertexAIService(project_id="ragproject-447813")
cloud_storage = CloudStorageService()

generation_model = vertexai.generative_models.GenerativeModel("gemini-1.5-flash")

@router.post("/query")
async def graph_query(query: GraphQuery):
    """
    Accepts a text query, converts it to an embedding, performs a graph-based search,
    retrieves the related file contents, and uses the Gemini model to return a coherent answer.
    """
    try:
        # Step 1: Convert query text to embedding.
        query_embedding = vertex_service.get_text_embedding(query.query)
        
        # Step 2: Query the graph database using the embedding.
        results = graph_storage.query_documents(query_embedding, query.top_k)
        
        # Step 3: Retrieve and combine context text from the documents.
        contexts = []
        for record in results:
            # Each record contains the node under key 'd'
            document_node = record.get("d", {})
            file_id = document_node.get("document_id")
            if file_id:
                try:
                    content = cloud_storage.get_file(file_id)
                    if content:
                        contexts.append(content.decode("utf-8"))
                except Exception as ex:
                    print(f"Error retrieving document {file_id}: {ex}")
                    continue
        
        if not contexts:
            return {"answer": "No relevant information found.", "sources": results}
        
        combined_context = "\n".join(contexts)
        
        # Step 4: Build the prompt for Gemini.
        prompt = f"""
Based on the following context, please answer the question.

Context:
{combined_context}

Question: {query.query}

Please provide a concise answer focusing only on information present in the context.
If the information is not in the context, say "I cannot find this information in the documents."
"""
        # Step 5: Generate a coherent response using Gemini.
        response = generation_model.generate_content(prompt)
        
        return {"answer": response.text, "sources": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 