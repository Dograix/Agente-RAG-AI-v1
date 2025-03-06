from typing import Generator
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..chat import ChatManager
from ..chat.database import get_db
from ..vector_store import EmbeddingGenerator, PineconeManager
from ..core.config import settings
from ..core.logging import logger

def get_pinecone() -> PineconeManager:
    """Retorna uma instância do PineconeManager"""
    try:
        return PineconeManager(index_name=settings.PINECONE_INDEX_NAME)
    except Exception as e:
        logger.error(f"Erro ao inicializar Pinecone: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao conectar com Pinecone"
        )

def get_embedding_generator() -> EmbeddingGenerator:
    """Retorna uma instância do EmbeddingGenerator"""
    try:
        return EmbeddingGenerator()
    except Exception as e:
        logger.error(f"Erro ao inicializar EmbeddingGenerator: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao inicializar sistema de embeddings"
        )

def get_chat_manager(
    pinecone: PineconeManager = Depends(get_pinecone),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator)
) -> ChatManager:
    """Retorna uma instância do ChatManager"""
    try:
        return ChatManager(
            pinecone_manager=pinecone,
            embedding_generator=embedding_generator,
            conversation_store=None  # Usa o store padrão
        )
    except Exception as e:
        logger.error(f"Erro ao inicializar ChatManager: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao inicializar gerenciador de chat"
        ) 