from sqlalchemy import ForeignKey,Column, Integer, String, Float, VARCHAR, inspect
from sqlalchemy.orm import sessionmaker, relationship, backref, DeclarativeBase

# Create a base class for our classes definitions

class Base(DeclarativeBase):
    pass

class Chatbot(Base):
    __tablename__ = 'chatbots'
    chatbot_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    chatbot_name = Column(String(50), nullable=False)
    temperature = Column(Float, default=0.5, nullable=False)
    max_tokens = Column(Integer, default=1000, nullable=False)
    top_p = Column(Float, default=1.0, nullable=False) 
    search_top_k = Column(Integer, default=3, nullable=False)
    embedding_model_provider = Column(String(50), default='ollama', nullable=False)
    embedding_model_deployment = Column(String(50), default='nomic-embed-text', nullable=False)
    chat_model_provider = Column(String(50), default='ollama', nullable=False)
    chat_model_deployment = Column(String(50), default='llama3-chatqa:8b', nullable=False)
    past_messages = Column(Integer, default=0, nullable=False)
    prompt_template = Column(String(4000), default='user message: {user_message}', nullable=False)
    security = Column(String(50), default='Off', nullable=False)
    chain_type = Column(String(50), default='basic', nullable=False)
    

    # relationships
    # documents = relationship('Document', backref=backref('chatbot', uselist=False))
    # system_messages = relationship('SystemMessage', backref=backref('chatbot', uselist=False))

class Document(Base):
    __tablename__ = 'documents'
    document_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    document_name = Column(String(250), nullable=False)
    document_type = Column(String(50), nullable=False)
    document_path = Column(String(250), nullable=False)
    chatbot_id = Column(Integer)

class SystemMessage(Base):
    __tablename__ = 'system_messages'
    system_message_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    chatbot_id = Column(Integer, default=1,nullable=False)
    system_message = Column(String(2000), nullable=False)

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    chat_history_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    role = Column(String(50), nullable=False)
    content = Column(String(4000), nullable=False)
    chatbot_id = Column(Integer, default=1, nullable=True)