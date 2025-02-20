import os
from dotenv import load_dotenv

load_dotenv()

# Google Cloud settings
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_STORAGE_BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

# Pinecone settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_REGION = "us-east-1"  # Your Pinecone region

# Vector dimensions
TEXT_VECTOR_DIMENSION = 768  # For text embeddings
IMAGE_VECTOR_DIMENSION = 1024  # For image embeddings