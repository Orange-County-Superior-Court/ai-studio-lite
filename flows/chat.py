from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate
)

from components.retrievers.retrievers import Retrievers
from components.models.models import Models
from components.chatbots.settings import Settings
from components.templates.templates import Templates

class Chat:
    """
 metadata = {
    'chat_model': 
        {
            'model_provider':'azure_openai',
            'model_deployment': 'gpt4o-standard'
        },
    'embedding_model':
        {
            'model_provider': 'ollama',
            'model_deployment': 'nomic-embed-text'
        }
    }
    """
    def __init__(self,metadata):
        self.metadata = metadata

        self.chat_settings = Settings().get_settings()
        self.chat_config = self.chat_settings.get('chat_settings')
        self.models = Models(self.chat_config).get_models()

        self.llm = self.models['chat_model']
        self.embedder = self.models['embedding_model']
        
        self.template_type = self.chat_config.get('template_type','generic')
        self.template_subtype = self.chat_config.get('template_subtype','safe')
        
        self.chain_type = self.chat_config.get('chain_type','basic')
        self.metadata['template_type'] = self.template_type
        self.metadata['template_subtype'] = self.template_subtype
        
        self.user_prompt_template = Templates().get_prompt_template(self.template_type,self.template_subtype)
        
        #message history and system messages
        self.past_messages = metadata.get('past_messages',2)
        
        self.message_history = self.chat_settings['message_history']
        self.system_messages = self.chat_settings['system_messages']
        

        self.user_message = metadata.get('user_message',"sorry something went wrong....error sending message to chatbot...please try again...")
        
    
    def chain_basic(self):
        prompt_template = self.user_prompt_template                                                         
        human_message_template = HumanMessagePromptTemplate.from_template(prompt_template)
        system_messages = self.system_messages
        chat_history = self.message_history
        messages = system_messages + chat_history + [human_message_template]

        chat_prompt = ChatPromptTemplate.from_messages(messages)

        llm_chain = chat_prompt | self.llm | StrOutputParser()
        return llm_chain
    
    def format_docs(self,docs):
        return "\n\n".join(f"Document Name:{doc.metadata['label_04']}\n Page Number: {doc.metadata['page']}\n, Document Path: {doc.metadata['document_source']}\n Content:\n{doc.page_content}\n\n" for doc in docs)

    def chain_qa(self):
        user_message = self.user_message

        prompt_template = self.user_prompt_template                                                         
        human_message_template = HumanMessagePromptTemplate.from_template(prompt_template)
        system_messages = self.system_messages
        chat_history = self.message_history
        messages = system_messages + chat_history + [human_message_template]

        chat_prompt = ChatPromptTemplate.from_messages(messages)

        llm_chain = (
        chat_prompt
        | self.llm
        | StrOutputParser()
        )

        return llm_chain

    def security_chain(self, security_message):
        user_message = self.user_message
  
        prompt_template = "Please recite the following message back to me word for word: " + security_message                                                   
        human_message_template = HumanMessagePromptTemplate.from_template(prompt_template)
        message = "Please recite the following message back to me word for word: " + security_message
        system_messages = Settings().map_messages([{"Role":"system","Content":message}])
        #sys_meesage = 'You are a security chatbot who will received a message when a user asks an inappropriate question. Please warn the user that they are not allowed to ask these types of questions.'
        messages = system_messages + [human_message_template]

        chat_prompt = ChatPromptTemplate.from_messages(messages)

        llm_chain = (
        chat_prompt
        | self.llm
        | StrOutputParser()
        )

        return llm_chain
    
    def chains(self, security_message=None):
        chain_type = self.chain_type
        if chain_type == 'basic': 
            llm_chain = self.chain_basic()
        elif chain_type == 'qa':
            llm_chain = self.chain_qa()
        elif chain_type == 'security':
            llm_chain = self.security_chain(security_message)
        
        self.llm_chain = llm_chain

        return llm_chain

    def chat_stream(self,user_message = 'please tell the user something went wrong....'):
        chain_type = self.chain_type
        user_input = {"user_message":user_message}
        llm_chain = self.chains()
        if chain_type == 'qa':
            retriever = Retrievers({}).get_retriever()
            docs = retriever.invoke(user_message)
            formatted_context = self.format_docs(docs)
            user_input['context'] = formatted_context

            stream = llm_chain.stream(user_input)
        else:
            stream = llm_chain.stream(user_input)

        return stream

    def chat_stream_security(self,user_message):
        self.chain_type = 'security'
        user_input = {"user_message":user_message}
        user_input['context'] = ""
        llm_chain = self.chains(user_message)
        stream = llm_chain.stream(user_input)

        return stream
    
    def chat_complete(self,user_message = 'please tell the user something went wrong....'):
        chain_type = self.chain_type
        user_input = {"user_message":user_message}
        llm_chain = self.chains()
        if chain_type == 'qa':
            retriever = Retrievers({}).get_retriever()
            docs = retriever.invoke(user_message)
            formatted_context = self.format_docs(docs)
            user_input['context'] = formatted_context

            response = llm_chain.invoke(user_input)
        else:
            response = llm_chain.invoke(user_input)
            
        return response
    
    def string_to_stream(self, s):
        for character in s:
            yield character