from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class QueryType(str, Enum):
    TEXT = "text"
    IMAGE = "image"

class DocumentUploadResponse(BaseModel):
    document_id: str
    status: str
    message: str

class Query(BaseModel):
    query: str
    query_type: QueryType
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]