import os,uuid
from components.documents.router import DocumentTypeRouter
from components.documents.loaders import DocumentLoader
from components.embeddings.embedders import Embeddings

from database.local_storage import LocalStorage

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

def embed_docs(file_path):
    """
    file_path = r'./local_storage/documents/Appointment of Elisor.pdf'
    """
    
    splits = file_path.split('/')
    file_name = splits[-1]
    file_extension = '.' + file_name.split('.')[-1]

    doc_router = DocumentTypeRouter({'file_extension':file_extension})
    document_ext_metadata = doc_router.get_content_type()
    
    local_storage = LocalStorage()
    chat_config = local_storage.read_chatbot(1)

    embedder = Embeddings(chat_config).embedder

    bytes = open(file_path, 'rb').read()
    document_id = int(str(uuid.uuid4().int)[:10])
    metadata = {**chat_config,**document_ext_metadata}
    metadata['court_id'] = 1
    metadata['data_exchange_id'] = 1
    metadata['document_id'] = document_id
    metadata['document_tag'] = file_name
    metadata['document_url'] = file_path

    loader = DocumentLoader(metadata,bytes)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100)

    split_documents = text_splitter.split_documents(documents)  

    index_temp = FAISS.from_documents(split_documents, embedder)

    local_storage = './local_storage'

    local_storage_final = os.path.join(local_storage,f'indexes/final/knowledge_base/')
    local_storage_final_document = os.path.join(local_storage,f'indexes/final/documents/{document_id}')

    if not os.path.exists(local_storage_final):
        os.makedirs(local_storage_final)

    #merging final index with new index
    if os.listdir(local_storage_final):
        index_stage = FAISS.load_local(local_storage_final, embedder,allow_dangerous_deserialization=True)
        index_stage.merge_from(index_temp)

    else:
        index_stage = index_temp

    index_stage.save_local(local_storage_final)

    if not os.path.exists(local_storage_final_document):
        os.makedirs(local_storage_final_document)

    index_temp.save_local(local_storage_final_document)