import os,logging
from langchain_community.vectorstores import FAISS
from components.models.models import Models
from components.chatbots.settings import Settings

class Retrievers:
    def __init__(self,metadata):
        self.metadata = metadata
        self.base_storage_path = 'local_storage'
        self.index_folder = 'indexes/final'
        self.index_subfolder = 'knowledge_base'

        self.chat_settings = Settings().get_settings()
        self.chat_config = self.chat_settings.get('chat_settings')
        self.embedder = Models(self.chat_config).get_embedding_model()
        self.top_k = self.chat_config.get('search_top_k',5)

    def get_indexes(self):
        base_storage = self.base_storage_path
        index_folder = self.index_folder
        index_subfolder = self.index_subfolder
        embedder = self.embedder
        index_path = os.path.join(base_storage, index_folder,index_subfolder)
        index_main = FAISS.load_local(index_path, embedder,allow_dangerous_deserialization=True)

        return index_main
    
    def get_retriever(self):
        index_main = self.get_indexes()
        retriever = index_main.as_retriever(
                search_type="mmr",
                search_kwargs={'k': self.top_k, 'fetch_k': 100}
        )
        return retriever