from pinecone import Pinecone, ServerlessSpec
from config.settings import PINECONE_API_KEY, PINECONE_REGION

class VectorStore:
    def __init__(self):
        # Initialize Pinecone
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index_name = "document-store"
        
        # Create index if it doesn't exist
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=768,  
                metric="cosine",
                spec=ServerlessSpec(
                    cloud='aws',
                    region=PINECONE_REGION
                )
            )
        
        self.index = self.pc.Index(self.index_name)

    def store_vectors(self, vectors, metadata):
        # Format vectors for upsert
        records = []
        for id, vector in vectors:
            records.append({
                "id": id,
                "values": vector,
                "metadata": metadata
            })
        
        return self.index.upsert(vectors=records)

    def search(self, query_vector, top_k=3):
        return self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )