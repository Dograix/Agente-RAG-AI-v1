import asyncio
from ..vector_store import EmbeddingGenerator, PineconeManager
from .chat_manager import ChatManager
from .database import get_db
from ..core.logging import logger

async def chat_example():
    try:
        # Inicializa componentes
        db = next(get_db())
        embedding_generator = EmbeddingGenerator()
        pinecone_manager = PineconeManager(index_name="rag-documents")
        
        # Inicializa chat manager
        chat_manager = ChatManager(
            db=db,
            pinecone_manager=pinecone_manager,
            embedding_generator=embedding_generator
        )
        
        # Cria uma nova conversa
        conversation = chat_manager.create_conversation("Exemplo de Conversa")
        logger.info(f"Conversa criada com ID: {conversation.id}")
        
        # Lista de perguntas para exemplo
        questions = [
            "Qual é o tema principal dos documentos?",
            "Pode me dar mais detalhes sobre isso?",
            "Há alguma conclusão importante?"
        ]
        
        # Processa cada pergunta
        for question in questions:
            print(f"\nUsuário: {question}")
            
            # Envia mensagem e obtém resposta
            response = await chat_manager.send_message(
                conversation_id=conversation.id,
                content=question
            )
            
            print(f"\nAssistente: {response.content}")
            
            if response.context_source:
                print(f"\nFonte: {response.context_source}")
                print(f"Relevância: {response.similarity_score:.2f}")
        
    except Exception as e:
        logger.error(f"Erro no exemplo de chat: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(chat_example()) 