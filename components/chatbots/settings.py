import json
from datetime import datetime

from components.file_storage.files import FileStorage
from database.local_storage import LocalStorage

from langchain_core.messages import SystemMessage, HumanMessage,AIMessage

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
class Settings:
    def __init__(self,metadata={}):
        local_storage = LocalStorage()
        self.chatbot_config = local_storage.read_chatbot(1)
        self.past_messages = self.chatbot_config.get('past_messages',0)
            
    def map_messages(self,messages):
        mapped_messages = []

        for message in messages:
            if message['Role'] == 'user':
                message = HumanMessage(content=message['Content'])
            elif message['Role'] == 'assistant':
                message = AIMessage(content=message['Content'])
            elif message['Role'] == 'system':
                message = SystemMessage(content=message['Content'])

            mapped_messages.append(message)

        return mapped_messages

    def global_system_messages(self):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        day_of_week = datetime.now().strftime("%A")
        global_sys_messages = [{"Role":"system","Content":f"Assume the current date and time is: {current_datetime} /n the day of the week is:{day_of_week}."}]
        global_sys_messages= []
        return global_sys_messages

    def chatbot_settings(self):
        chatbot_data = self.chatbot_config

        chat_settings = {
                "temperature": chatbot_data['temperature'],
                "max_tokens": chatbot_data['max_tokens'],
                "top_p": chatbot_data['top_p'],
                "search_top_k": chatbot_data['search_top_k'],
                "chat_model_provider": chatbot_data['chat_model_provider'],
                "chat_model_deployment": chatbot_data['chat_model_deployment'],
                "embedding_model_provider": chatbot_data['embedding_model_provider'],
                "embedding_model_deployment": chatbot_data['embedding_model_deployment'],
                "past_messages": chatbot_data['past_messages'],
                "chain_type": chatbot_data['chain_type']
        }
        return chat_settings
    
    def user_system_messages(self):
        """
        EXAMPLE:
        user_system_messages = [{"Role":"system","Content":"dont be mean"}]
        """
        local_storage = LocalStorage()
        system_messages_data = local_storage.read_system_message(1)
        system_message = [{"Role":"system","Content":system_messages_data['system_message']}]
        
        return system_message

    def get_system_messages(self):
        user_defined_messages = self.user_system_messages()
        global_messages = self.global_system_messages()
        
        system_messages = global_messages + user_defined_messages  
        mapped_system_messages = self.map_messages(system_messages)
        
        return mapped_system_messages

    def get_message_history(self):
        """
        EXAMPLE:
        message_history_array = [{"Role":"user","Content":"what is todays date?"},{"Role":"assistant","Content":"todays date is July 5th, 2024"}]
        """


        past_messages = self.past_messages*2

        local_storage = LocalStorage()
        chat_history_data = local_storage.read_chat_history(1)
        if chat_history_data:
            message_history_array = [{'Role': item['role'], 'Content': item['content']} for item in chat_history_data] 
       
        past_messages_final = min(past_messages,len(message_history_array))
        message_history_array = message_history_array[-past_messages_final:] if past_messages_final > 0 else []
        
        mapped_message_history= self.map_messages(message_history_array)

        return mapped_message_history
    
    def get_settings(self):
        
        settings = {
            "system_messages": self.get_system_messages(),
            "message_history": self.get_message_history(),
            "chat_settings": self.chatbot_settings()
        }
        
        return settings