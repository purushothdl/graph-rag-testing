import os
import json
from neo4j import GraphDatabase, basic_auth

# Read Neo4j connection details from the environment:
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j_password")

class GraphStorageService:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def insert_document(self, document_id: str, embedding: list, metadata: dict):
        """
        Inserts (or merges) a document node with its embedding and metadata.
        The metadata is converted to a JSON string.
        """
        cypher_query = """
        MERGE (d:Document {document_id: $document_id})
        SET d.embedding = $embedding, d.metadata = $metadata_json
        RETURN d
        """
        metadata_json = self._jsonify_metadata(metadata)
        with self.driver.session() as session:
            result = session.run(cypher_query, document_id=document_id, embedding=embedding, metadata_json=metadata_json)
            return result.single()

    def query_documents(self, query_embedding: list, top_k: int = 3):
        """
        Uses a manually computed cosine similarity between the stored document embeddings and the query embedding.
        The cosine similarity is calculated as:
        
        cosine = (dot(d.embedding, query_embedding)) / (norm(d.embedding) * norm(query_embedding))
        """
        cypher_query = """
        MATCH (d:Document)
        WITH d,
             reduce(s=0.0, i in range(0, size(d.embedding)-1) | s + d.embedding[i]*$query_embedding[i]) AS dot,
             reduce(s=0.0, i in range(0, size(d.embedding)-1) | s + d.embedding[i]*d.embedding[i]) AS norm_d,
             reduce(s=0.0, i in range(0, size($query_embedding)-1) | s + $query_embedding[i]*$query_embedding[i]) AS norm_q
        WITH d, dot / (sqrt(norm_d)*sqrt(norm_q)) AS similarity
        ORDER BY similarity DESC
        LIMIT $top_k
        RETURN d, similarity
        """
        with self.driver.session() as session:
            result = session.run(cypher_query, query_embedding=query_embedding, top_k=top_k)
            return [record.data() for record in result]

    def _jsonify_metadata(self, metadata: dict) -> str:
        """
        Convert the metadata dictionary to a JSON string.
        """
        return json.dumps({k: str(v) for k, v in metadata.items()}) 