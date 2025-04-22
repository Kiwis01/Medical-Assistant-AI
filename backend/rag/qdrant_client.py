import qdrant_client
from qdrant_client.http import models
from langchain.embeddings import VertexAIEmbeddings
from langchain.schema import Document

class QdrantRetriever:
    def __init__(self, config, collection_name="medical_documents"):
        self.config = config
        self.collection_name = collection_name
        self.qdrant_key = config.get_qdrant_key()
        
        # Initialize Qdrant client
        self.client = qdrant_client.QdrantClient(
            url="[https://4bd4ec0c-0fb8-40cd-a5f8-03d9b8b4720f.us-east4-0.gcp.cloud.qdrant.io](https://4bd4ec0c-0fb8-40cd-a5f8-03d9b8b4720f.us-east4-0.gcp.cloud.qdrant.io)",
            api_key=self.qdrant_key
        )
        
        # Initialize embeddings model
        self.embeddings = VertexAIEmbeddings()
    
    def retrieve(self, query, top_k=3):
        """
        Retrieve relevant documents for a query
        
        Args:
            query (str): The user query
            top_k (int): Number of documents to retrieve
            
        Returns:
            list: List of Document objects
        """
        # Generate embedding for the query
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in Qdrant
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        
        # Convert to Document objects
        documents = []
        for result in search_result:
            doc = Document(
                page_content=result.payload.get("content", ""),
                metadata={
                    "source": result.payload.get("source", "Unknown"),
                    "title": result.payload.get("title", ""),
                    "score": result.score
                }
            )
            documents.append(doc)
            
        return documents