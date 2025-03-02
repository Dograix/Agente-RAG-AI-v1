import asyncio
from app.vector_store.pinecone_store import PineconeManager
from app.core.logging import logger

async def test_pinecone_connection():
    """Testa a conexão com o Pinecone"""
    try:
        # Inicializa o gerenciador do Pinecone
        pinecone_manager = PineconeManager(index_name="rag-documents")
        
        # Se chegou até aqui, a conexão foi estabelecida
        logger.info(
            "Conexão com Pinecone testada com sucesso!",
            extra={
                "index_name": pinecone_manager.index_name,
                "environment": pinecone_manager.environment
            }
        )
        return True
            
    except Exception as e:
        logger.error(f"Erro ao testar conexão com Pinecone: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_pinecone_connection()) 