import asyncio
from app.vector_store.embeddings import EmbeddingGenerator
from app.core.logging import logger

async def test_openai_connection():
    """Testa a conexão com a OpenAI"""
    try:
        # Inicializa o gerador de embeddings
        embedding_generator = EmbeddingGenerator()
        
        # Testa geração de embeddings
        test_texts = ["Isso é um teste de conexão com a OpenAI"]
        embeddings = await embedding_generator.generate_embeddings(test_texts)
        
        # Verifica se recebemos os embeddings
        if embeddings and len(embeddings) > 0:
            logger.info(
                "Conexão com OpenAI testada com sucesso!",
                extra={
                    "embedding_dim": len(embeddings[0])
                }
            )
            return True
        else:
            logger.error("Não foi possível gerar embeddings")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao testar conexão com OpenAI: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openai_connection()) 