#chat models
from langchain_community.chat_models import ChatOllama,AzureChatOpenAI
from langchain_openai import AzureChatOpenAI

#embeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import AzureOpenAIEmbeddings

#custom configs
from components.config.settings import Settings

class Models:
    """
    metadata = {
        'ChatModel': 
            {
                'model_provider':'azure_openai',
                'model_deployment': 'gpt4o-standard'
            },
        'EmbeddingModel':
            {
                'model_provider': 'ollama',
                'model_deployment': 'nomic-embed-text'
            }
    }
    """
    def __init__(self,metadata):
        self.settings = Settings().list_settings()
        self.temperature = metadata.get('Temperature',0.1)
        self.chat_model_provider = metadata.get('chat_model_provider')
        self.chat_model_deployment = metadata.get('chat_model_deployment')
        self.embedding_model_provider = metadata.get('embedding_model_provider')
        self.embedding_model_deployment = metadata.get('embedding_model_deployment')
        
    def chatmodel_ollama(self):
        settings = self.settings
        endpoint = settings.get('ollama').get('endpoint')
        
        chat_model = ChatOllama(
            model= self.chat_model_deployment,
            temperature= self.temperature,
            base_url = endpoint
            )

        return chat_model
    
    def chatmodel_azureopenai(self):
        settings = self.settings
        api_version = settings.get('azure_open_ai').get('api_version')
        api_key = settings.get('azure_open_ai').get('api_key')
        endpoint = settings.get('azure_open_ai').get('endpoint')

        chat_model = AzureChatOpenAI(
            api_version=api_version,
            api_key = api_key,
            azure_endpoint=endpoint,
            azure_deployment=self.chat_model_deployment,
            temperature=self.temperature
        )
        return chat_model

    def get_chat_model(self):
        if self.chat_model_provider == 'ollama':
            chat_model = self.chatmodel_ollama()

        elif(self.chat_model_provider == 'azure_openai'):
            chat_model = self.chatmodel_azureopenai()

        return chat_model
    
    def embeddingmodel_ollama(self):
        model_deployment = self.embedding_model_deployment

        settings = self.settings
        endpoint = settings.get('ollama').get('endpoint')

        embedding_model =  OllamaEmbeddings(base_url = endpoint ,model=model_deployment)
        
        return embedding_model        

    def embeddingmodel_azureopenai(self):
        model_deployment = self.embedding_model_deployment
        
        settings = self.settings
        api_version = settings.get('azure_open_ai').get('api_version')
        api_key = settings.get('azure_open_ai').get('api_key')
        api_type = endpoint = settings.get('azure_open_ai').get('api_type')
        endpoint = settings.get('azure_open_ai').get('endpoint')
        
        embedder = AzureOpenAIEmbeddings(
            azure_deployment = model_deployment,
            azure_endpoint = endpoint,
            openai_api_type= api_type,
            openai_api_key= api_key
        )

        return embedder

    def get_embedding_model(self):
        model_deployment = self.embedding_model_deployment
        model_provider = self.embedding_model_provider

        if model_provider == 'ollama':
           embedding_model =  self.embeddingmodel_ollama()
        elif(model_provider == 'azure_openai'):
            embedding_model = self.embeddingmodel_azureopenai()

        return embedding_model
    
    def get_models(self):
        models = {}
        models['chat_model'] = self.get_chat_model()
        models['embedding_model'] = self.get_embedding_model()
        return models
