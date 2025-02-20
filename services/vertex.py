from google.cloud import aiplatform
import vertexai
from vertexai.language_models import TextEmbeddingModel
from vertexai.vision_models import Image
from vertexai.preview.generative_models import GenerativeModel

class VertexAIService:
    def __init__(self, project_id, location="us-central1"):
        vertexai.init(project=project_id, location=location)
        self.text_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        self.multimodal_model = GenerativeModel("gemini-pro-vision")
    
    def get_text_embedding(self, text):
        embeddings = self.text_model.get_embeddings([text])
        return embeddings[0].values if embeddings else None

    def get_image_embedding(self, image_bytes):
        # Convert bytes to Image
        image = Image.from_bytes(image_bytes)
        
        # Use multimodal model to get image understanding
        response = self.multimodal_model.generate_content(
            ["Describe this image in detail", image],
            generation_config={
                "max_output_tokens": 2048,
                "temperature": 0.4
            }
        )
        
        # Convert the image description to embeddings
        description = response.text
        return self.get_text_embedding(description)

    def generate_response(self, query, context):
        model = GenerativeModel("gemini-pro")
        prompt = f"""
        Question: {query}
        Context: {context}
        
        Please provide a concise and accurate answer based on the context provided.
        """
        response = model.generate_content(prompt)
        return response.text