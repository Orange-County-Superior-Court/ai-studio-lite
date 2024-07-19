    
from components.embeddings.embedders import Embeddings
from database.local_storage import LocalStorage
from langchain_community.vectorstores import FAISS
import shutil,os

def reset_index():
    local_storage = LocalStorage()
    chat_config = local_storage.read_chatbot(1)

    embedder = Embeddings(chat_config).embedder

    index_folder = './local_storage/indexes/final/knowledge_base'
    document_folder_index = './local_storage/indexes/final/documents'
    document_folder = './local_storage/documents'

    try:
        shutil.rmtree(index_folder)
        shutil.rmtree(document_folder_index)
        shutil.rmtree(document_folder)

        # After removing the folders, recreate them
        os.makedirs(index_folder, exist_ok=True)
        os.makedirs(document_folder_index, exist_ok=True)
        os.makedirs(document_folder, exist_ok=True)
    
    except Exception as e:
        pass

    return 'Index reset successfully'