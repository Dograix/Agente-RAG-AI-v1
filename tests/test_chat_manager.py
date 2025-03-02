import os
import asyncio
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Carrega as variáveis de ambiente
load_dotenv()

# Importações necessárias
from app.chat.chat_manager import ChatManager
from app.vector_store.pinecone_store import PineconeManager
from app.vector_store.embeddings import EmbeddingGenerator
from app.chat.conversation_store import ConversationStore

# Classe MockPineconeManager para substituir o PineconeManager real
class MockPineconeManager:
    def __init__(self, *args, **kwargs):
        print("✅ MockPineconeManager inicializado")
    
    async def search(self, embedding_generator, query, top_k=3):
        print(f"🔍 Simulando busca para: {query}")
        # Retorna um resultado simulado
        return [{
            "id": "mock-doc-1",
            "score": 0.85,
            "metadata": {
                "source": "documentos/manual.pdf",
                "doc_id": "doc-123",
                "chunk_index": 1,
                "text": "Este é um texto simulado para o sistema de documentos RAG."
            }
        }]

async def test_chat_manager_response():
    """Testa a funcionalidade básica do ChatManager"""
    # Obtém a chave da API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        return False

    print(f"✅ OPENAI_API_KEY encontrada: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        # Inicializa os componentes
        embedding_generator = EmbeddingGenerator(api_key=api_key)
        pinecone_manager = MockPineconeManager()
        conversation_store = ConversationStore()
        
        chat_manager = ChatManager(
            pinecone_manager=pinecone_manager,
            embedding_generator=embedding_generator,
            conversation_store=conversation_store,
            api_key=api_key,
            model="gpt-4o-mini"
        )
        
        # Cria uma nova conversa
        conversation = chat_manager.create_conversation("Teste ChatManager")
        conversation_id = conversation.conversation_id
        
        # Testa o envio de mensagem
        response = await chat_manager.get_response(
            conversation_id=conversation_id,
            message="Como funciona o sistema de documentos?"
        )
        
        # Verifica se a resposta foi recebida
        if not response or 'content' not in response:
            print("❌ Não recebeu resposta válida do ChatManager")
            return False
            
        # Verifica duplicação de mensagens
        conversation = chat_manager.get_conversation(conversation_id)
        user_messages = [msg for msg in conversation.messages if msg["role"] == "user"]
        
        if len(user_messages) > 1:
            print("❌ A mensagem do usuário foi duplicada!")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do ChatManager: {e}")
        return False

async def run_all_tests():
    """Executa todos os testes do ChatManager"""
    print("\n🔄 Iniciando testes do ChatManager...")
    
    # Teste principal
    result = await test_chat_manager_response()
    
    if result:
        print("✅ Todos os testes passaram com sucesso!")
    else:
        print("❌ Alguns testes falharam!")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 