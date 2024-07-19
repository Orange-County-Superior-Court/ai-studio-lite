import os

class Settings:

    def __init__(self):
        pass

    def azure_open_ai(self):
        settings = {
            'api_version': os.getenv('AzureOpenAI_APIVersion'),
            'api_key': os.getenv('AzureOpenAI_APIKey'),
            'endpoint': os.getenv('AzureOpenAI_Endpoint'),
            'api_type': os.getenv('AzureOpenAI_APIType')
        }

        return settings
    def ollama(self):
        settings = {
            'endpoint': os.getenv('Ollama_Endpoint')
        }

        return settings
    def list_settings(self):
        settings = {
            'azure_open_ai': self.azure_open_ai(),
            'ollama': self.ollama()
        }
        return settings