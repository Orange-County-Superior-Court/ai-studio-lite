from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, Float, VARCHAR, inspect, select
from sqlalchemy.orm import Session, relationship, backref, DeclarativeBase
from sqlalchemy import create_engine

from database.models import Base, Chatbot, Document, SystemMessage, ChatHistory

class LocalStorage:
    def __init__(self):
        # Database setup
        self.establish_engine()
        self.setup_base_tables()
        self.prepropulate_tables()

    def establish_engine(self):
        self.engine = create_engine('sqlite:///database/storage.db')

    # Setup the database table layouts
    def setup_base_tables(self):
        Base.metadata.create_all(self.engine)

    
    def display_tables_and_columns(self):
        inspector = inspect(self.engine)
        session = Session(self.engine)

        for table_name in inspector.get_table_names():
            print("Table: ", table_name)
            for column in inspector.get_columns(table_name):
                print("Column: ", column['name'])

            # Query the table and print the data
            table = Base.metadata.tables.get(table_name)
            if table is not None:
                for row in session.query(table).all():
                    print(row)

        session.close()
        

    """
    Interacting with the database
    """
    def create_chatbot(self, chatbot_data):
        with Session(self.engine) as session:
            new_chatbot = Chatbot(
                chatbot_name = chatbot_data['chatbot_name'],
                temperature = chatbot_data['temperature'],
                top_p = chatbot_data['top_p'],
                search_top_k = chatbot_data['search_top_k'],
                embedding_model_provider = chatbot_data['embedding_model_provider'],
                embedding_model_deployment = chatbot_data['embedding_model_deployment'],
                chat_model_provider = chatbot_data['chat_model_provider'],
                chat_model_deployment = chatbot_data['chat_model_deployment'],
                past_messages = chatbot_data['past_messages'],
                prompt_template = chatbot_data['prompt_template'],
                security = chatbot_data['security'],
                chain_type = chatbot_data['chain_type']
            )

            session.add(new_chatbot)
            session.commit()

    def read_chatbot(self, chatbot_id):
        with Session(self.engine) as session:
            chatbot = session.query(Chatbot).filter(Chatbot.chatbot_id == chatbot_id).first()
            if chatbot:
                chatbot_dict = {key: value for key, value in chatbot.__dict__.items() if not key.startswith('_sa_')}
                chatbot_dict['chatbot_id'] = chatbot.chatbot_id
        return chatbot_dict
    
    def update_chatbot(self, chatbot_data):
        stmt = select(Chatbot).where(Chatbot.chatbot_id == chatbot_data['chatbot_id'])
        with Session(self.engine) as session:
            chatbot = session.scalars(stmt).first()
            if chatbot:
                chatbot.chatbot_name = chatbot_data['chatbot_name']
                chatbot.temperature = chatbot_data['temperature']
                chatbot.top_p = chatbot_data['top_p']
                chatbot.search_top_k = chatbot_data['search_top_k']
                chatbot.embedding_model_provider = chatbot_data['embedding_model_provider']
                chatbot.embedding_model_deployment = chatbot_data['embedding_model_deployment']
                chatbot.chat_model_provider = chatbot_data['chat_model_provider']
                chatbot.chat_model_deployment = chatbot_data['chat_model_deployment']
                chatbot.past_messages = chatbot_data['past_messages']
                chatbot.prompt_template = chatbot_data['prompt_template']
                chatbot.security = chatbot_data['security']
                chatbot.chain_type = chatbot_data['chain_type']
                session.commit()

    def delete_chatbot(self, chatbot_id):
        with Session(self.engine) as session:
            chatbot = session.get(Chatbot, chatbot_id)
            session.delete(chatbot)
            session.commit()
            
    def create_chat_history(self, chat_history_data):
        with Session(self.engine) as session:
            new_chat_history = ChatHistory(
                role = chat_history_data['role'],
                content = chat_history_data['content'],
            )
            session.add(new_chat_history)
            session.commit()
    def read_chat_history(self, chatbot_id):
        with Session(self.engine) as session:
            chatbot_histories = session.query(ChatHistory).filter(ChatHistory.chatbot_id == chatbot_id).all()
            chat_histories_list = []
            for chatbot_history in chatbot_histories:
                chat_history_dict = {key: value for key, value in chatbot_history.__dict__.items() if not key.startswith('_sa_')}
                chat_history_dict['chatbot_id'] = chatbot_id
                chat_histories_list.append(chat_history_dict)
        return chat_histories_list
    
    def delete_chat_history(self):
        with Session(self.engine) as session:
            session.query(ChatHistory).delete()
            session.commit()

 
#!=System Messages=============================================================================================================
    def create_system_message(self, system_message_data):
        with Session(self.engine) as session:
            new_system_message = SystemMessage(
                system_message = system_message_data['message'],
                chatbot_id = system_message_data['chatbot_id']
            )
            session.add(new_system_message)
            session.commit()
    def read_system_message(self, chatbot_id):
        with Session(self.engine) as session:
            system_message = session.query(SystemMessage).filter(SystemMessage.chatbot_id == chatbot_id).first()
            if system_message:
                system_message_dict = {key: value for key, value in system_message.__dict__.items() if not key.startswith('_sa_')}
                system_message_dict['chatbot_id'] = chatbot_id
        return system_message_dict
    
    def delete_system_message(self):
        with Session(self.engine) as session:
            session.query(SystemMessage).delete()
            session.commit()
    
    def update_system_messages(self, system_message_data):
        stmt = select(SystemMessage).where(SystemMessage.chatbot_id == system_message_data['chatbot_id'])
        with Session(self.engine) as session:
            system_message = session.scalars(stmt).first()
            if system_message:
                system_message.system_message = system_message_data['system_message']
                system_message.chatbot_id = system_message_data['chatbot_id']
                session.commit()

    def prepop_chatbot(self):
        # check if there is already a chatbot with id 1, in which case there is no need to prepopulate the tabels
        stmt = select(Chatbot).where(Chatbot.chatbot_id == 1)
        with Session(self.engine) as session:
            chatbot = session.scalars(stmt).first()
            if chatbot:
                return

        self.create_chatbot({'chatbot_name': 'NACM-Demo', 
                             'temperature': 0.1, 
                             'max_tokens': 750,
                             'top_p': 1.0, 
                             'search_top_k': 5, 
                             'embedding_model_provider': 'azure_openai', 
                             'embedding_model_deployment': 'text-embedding-3-small', 
                             'chat_model_provider': 'azure_openai', 
                             'chat_model_deployment': 'gpt-4o', 
                             'past_messages': 3, 
                             'prompt_template': 'Below is the user message: {user_message} END OF USER MESSAGE /n Document Context: {context} End of Document Context',
                             'security': 'Off',
                             'chain_type': 'qa'
                             })
        
    def prepop_sys(self):
        # check if there is already a chatbot with id 1, in which case there is no need to prepopulate the tabels
        stmt = select(SystemMessage).where(SystemMessage.chatbot_id == 1)
        with Session(self.engine) as session:
            sys_messages = session.scalars(stmt).first()
            if sys_messages:
                return

        self.create_system_message({'message': '', 'chatbot_id': 1})
    
    def prepop_chathist(self):
        # check if there is already a chatbot with id 1, in which case there is no need to prepopulate the tabels
        stmt = select(ChatHistory).where(ChatHistory.chatbot_id == 1)
        with Session(self.engine) as session:
            history = session.scalars(stmt).first()
            if history:
                return

        self.create_chat_history({'role': 'user', 'content': 'hello'})
        self.create_chat_history({'role': 'assistant', 'content': 'hello, how are you doing today? Are you ready to build a chatbot for the NACM demo?'})

    def prepropulate_tables(self):
        self.prepop_sys()
        self.prepop_chatbot()
        self.prepop_chathist()
# #!==============================================================================================================
# Testing


# local_storage = LocalStorage()
# local_storage.display_tables_and_columns()

# local_storage.update_system_messages({'chatbot_id':1,'system_message':'your name is courtly and you are to assist users with their questions.'})
# local_storage.read_system_message(1)
# # inserting test data
# local_storage.create_chatbot({'chatbot_name': 'Steven', 
#                              'temperature': 0.1, 
#                              'max_tokens': 2000,
#                              'top_p': 1.0, 
#                              'search_top_k': 100, 
#                              'embedding_model_provider': 'ollama', 
#                              'embedding_model_deployment': 'nomic-embed-text', 
#                              'chat_model_provider': 'ollama', 
#                              'chat_model_deployment': 'phi3:mini', 
#                              'past_messages': 0, 
#                              'prompt_template': '{user_message}'})
# local_storage.read_chatbot(1)
# # local_storage.delete_chatbot(2)
# local_storage.update_chatbot(
#                                 {
#                                     'chatbot_id':1,
#                                     'chatbot_name': 'Steven', 
#                                     'temperature': 0.1, 
#                                     'max_tokens': 2000,
#                                     'top_p': 1.0, 
#                                     'search_top_k': 100, 
#                                     'embedding_model_provider': 'ollama', 
#                                     'embedding_model_deployment': 'nomic-embed-text', 
#                                     'chat_model_provider': 'ollama', 
#                                     'chat_model_deployment': 'phi3:mini', 
#                                     'past_messages': 0, 
#                                     'prompt_template': '{user_message}',
#                                     'security': 'Off'
#                                 }
#                              )

# # testing read chat history
# local_storage.create_chat_history({'role': 'user', 'content': 'yes', 'chatbot_id': 1})
# local_storage.read_chat_history(1)
# local_storage.delete_chat_history()

# #testing system messages
# local_storage.create_system_message({'message': 'do not answer inappropriate questionss', 'chatbot_id': 1})
# local_storage.read_system_message(1)
# local_storage.delete_system_message()

# #! ==============================================================================================================




