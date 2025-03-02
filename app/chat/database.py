from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from ..core.config import settings
from ..core.logging import logger

# Cria URL de conexão
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

# Cria engine do SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria base para os modelos
Base = declarative_base()

class Conversation(Base):
    """Modelo para conversas"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    """Modelo para mensagens"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(50))  # user, assistant, ou system
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Campos para rastreamento de contexto
    context_source = Column(String(255), nullable=True)  # Fonte do documento
    context_chunk = Column(Integer, nullable=True)       # Índice do chunk
    similarity_score = Column(Float, nullable=True)      # Score de similaridade
    
    conversation = relationship("Conversation", back_populates="messages")

def init_db():
    """Inicializa o banco de dados"""
    try:
        logger.info("Inicializando banco de dados")
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        raise

def get_db():
    """Retorna uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializa o banco de dados na importação
init_db() 