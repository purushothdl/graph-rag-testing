import requests
import streamlit as st

# Set the BASE_URL for your FastAPI backend. If running in docker-compose,
# you might use the service name (e.g., "http://app:8000") instead of localhost.
BASE_URL = "http://app:8000"

def upload_document_api(file):
    """
    Calls the FastAPI upload endpoint to upload the document.
    """
    url = f"{BASE_URL}/api/v1/upload"
    files = {"file": (file.name, file.getvalue(), file.type)}
    try:
        response = requests.post(url, files=files)
        return response.json()
    except Exception as e:
        st.error(f"Upload error: {e}")
        return {}

def query_rag_api(query_text: str):
    """
    Calls the FastAPI RAG endpoint to retrieve a coherent answer.
    """
    url = f"{BASE_URL}/api/v1/query"
    payload = {"query": query_text, "top_k": 3, "query_type": "text"}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        st.error(f"RAG query error: {e}")
        return {}

def query_graphrag_api(query_text: str):
    """
    Calls the FastAPI GraphRAG endpoint to retrieve a coherent answer.
    """
    url = f"{BASE_URL}/graph/query"
    payload = {"query": query_text, "top_k": 3}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        st.error(f"GraphRAG query error: {e}")
        return {} 