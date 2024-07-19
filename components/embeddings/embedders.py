from langchain_community.embeddings import OllamaEmbeddings
from components.models.models import Models

class Embeddings:
    def __init__(self, metadata):
        self.embedding_model = metadata
        self.embedder = Models(metadata).get_embedding_model()
    
    def embed_documents(self, documents):
        embedder = self.embedder
        embedded_docs = self.embedder.embed_documents(documents)
        return embedded_docs
    
    def embed_query(self, query):
        embedder = self.embedder
    
        embedded_query = embedder.embed_query(query)

        return embedded_query
