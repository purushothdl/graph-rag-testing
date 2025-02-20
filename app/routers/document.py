from fastapi import APIRouter, File, UploadFile, HTTPException
import vertexai.generative_models
from services.cloud_storage import CloudStorageService
from services.vision import VisionService
from services.vertex import VertexAIService
from services.vector_store import VectorStore
from models.schemas import DocumentUploadResponse, Query, QueryResponse
import vertexai
from vertexai.language_models import TextGenerationModel
import PyPDF2
import io
from services.graph_storage import GraphStorageService

router = APIRouter(prefix="/api/v1")

cloud_storage = CloudStorageService()
vision_service = VisionService()
vertex_service = VertexAIService(project_id="ragproject-447813")
vector_store = VectorStore()

# Initialize Gemini model
vertexai.init(project="ragproject-447813", location="us-central1")
generation_model = vertexai.generative_models.GenerativeModel("gemini-1.5-flash")

# Initialize the Graph Storage Service
graph_storage = GraphStorageService()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        # Extract text content based on file type
        if file.content_type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text()
        else:
            # Assume it's an image
            text_content = vision_service.extract_text_from_image(content)
            image_labels = vision_service.analyze_image(content)
            text_content += "\n" + image_labels
        
        # Store the extracted text content
        file_id = cloud_storage.upload_file(text_content.encode('utf-8'), 'text/plain')
        
        # Generate embeddings
        text_embedding = vertex_service.get_text_embedding(text_content)
        
        # Store in vector database
        metadata = {
            "file_id": file_id,
            "content_type": file.content_type,
            "filename": file.filename
        }
        
        vector_store.store_vectors([(file_id, text_embedding)], metadata)
        
        # Store the document in the graph database (Neo4j)
        graph_storage.insert_document(document_id=file_id, embedding=text_embedding, metadata=metadata)
        
        return DocumentUploadResponse(
            document_id=file_id,
            status="success",
            message="Document processed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_documents(query: Query):
    try:
        query_embedding = vertex_service.get_text_embedding(query.query)
        results = vector_store.search(query_embedding, query.top_k)
        
        # Retrieve and combine contexts
        contexts = []
        for match in results.matches:
            try:
                content = cloud_storage.get_file(match.id)
                if content:
                    contexts.append(content.decode('utf-8'))
            except Exception as e:
                print(f"Error retrieving content for {match.id}: {str(e)}")
                continue
        
        if not contexts:
            return QueryResponse(
                answer="No relevant information found.",
                sources=[{"id": match.id, "score": match.score} for match in results.matches]
            )
        
        combined_context = "\n".join(contexts)
        
        # Generate response using Gemini Pro
        prompt = f"""
        Based on the following context, please answer the question.
        
        Context:
        {combined_context}
        
        Question: {query.query}
        
        Please provide a concise answer focusing only on information present in the context.
        If the information is not in the context, say "I cannot find this information in the document."
        """
        
        response = generation_model.generate_content(prompt)  # Changed this line
        
        return QueryResponse(
            answer=response.text,
            sources=[{"id": match.id, "score": match.score} for match in results.matches]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))