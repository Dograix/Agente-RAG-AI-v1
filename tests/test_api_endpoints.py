import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import MagicMock, patch
from app.api import app
from app.chat import ChatManager
from app.vector_store.pinecone_store import PineconeManager
from app.vector_store.embeddings import EmbeddingGenerator
from app.chat.conversation_store import ConversationStore
from app.analytics.conversation_analyzer import ConversationAnalyzer

# Cliente de teste
client = TestClient(app)

# Mock do PineconeManager
class MockPineconeManager:
    async def search(self, embedding_generator, query, top_k=3):
        return [{
            "id": "mock-doc-1",
            "score": 0.85,
            "metadata": {
                "source": "documentos/teste.pdf",
                "text": "Texto de teste para o sistema RAG"
            }
        }]

# Mock do ConversationAnalyzer
class MockConversationAnalyzer:
    def get_recent_activity(self):
        return [
            {"type": "message", "count": 10, "date": "2024-03-01"},
            {"type": "conversation", "count": 2, "date": "2024-03-01"}
        ]
    
    def get_popular_topics(self, days):
        return [
            {"topic": "documentos", "count": 5, "relevance_score": 0.8},
            {"topic": "sistema", "count": 3, "relevance_score": 0.7}
        ]

# Fixtures do pytest
@pytest.fixture
def mock_chat_manager():
    embedding_generator = EmbeddingGenerator()
    pinecone_manager = MockPineconeManager()
    conversation_store = ConversationStore()
    
    return ChatManager(
        pinecone_manager=pinecone_manager,
        embedding_generator=embedding_generator,
        conversation_store=conversation_store
    )

@pytest.fixture
def mock_analytics():
    return MockConversationAnalyzer()

# Testes dos endpoints de Conversas
def test_create_conversation():
    """Testa a criação de uma nova conversa"""
    response = client.post(
        "/conversations/",
        json={"title": "Conversa de Teste"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Conversa de Teste"
    assert "created_at" in data
    assert "updated_at" in data

def test_list_conversations():
    """Testa a listagem de conversas"""
    response = client.get("/conversations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "title" in data[0]

def test_get_conversation():
    """Testa a obtenção de uma conversa específica"""
    # Primeiro cria uma conversa
    create_response = client.post(
        "/conversations/",
        json={"title": "Conversa para Teste"}
    )
    conversation_id = create_response.json()["id"]
    
    # Tenta obter a conversa criada
    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conversation_id

# Testes dos endpoints de Mensagens
def test_create_message():
    """Testa o envio de uma mensagem em uma conversa"""
    # Cria uma conversa primeiro
    conv_response = client.post(
        "/conversations/",
        json={"title": "Conversa para Mensagens"}
    )
    conversation_id = conv_response.json()["id"]
    
    # Envia uma mensagem
    response = client.post(
        f"/conversations/{conversation_id}/messages/",
        json={
            "content": "Olá, como funciona o sistema?",
            "role": "user"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "content" in data
    assert "role" in data
    assert "created_at" in data
    assert isinstance(data["content"], str)
    assert len(data["content"]) > 0

def test_list_messages():
    """Testa a listagem de mensagens de uma conversa"""
    # Cria uma conversa primeiro
    conv_response = client.post(
        "/conversations/",
        json={"title": "Conversa para Listar Mensagens"}
    )
    conversation_id = conv_response.json()["id"]
    
    # Envia algumas mensagens
    client.post(
        f"/conversations/{conversation_id}/messages/",
        json={
            "content": "Primeira mensagem",
            "role": "user"
        }
    )
    client.post(
        f"/conversations/{conversation_id}/messages/",
        json={
            "content": "Segunda mensagem",
            "role": "user"
        }
    )
    
    # Lista as mensagens
    response = client.get(f"/conversations/{conversation_id}/messages/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

# Testes dos endpoints de Documentos
def test_list_documents():
    """Testa a listagem de documentos"""
    response = client.get("/documents/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@patch("app.api.endpoints.ConversationAnalyzer", return_value=MockConversationAnalyzer())
def test_get_system_overview(mock_analyzer):
    """Testa a obtenção da visão geral do sistema"""
    response = client.get("/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_conversations" in data
    assert "total_messages" in data
    assert "total_documents" in data
    assert "recent_activity" in data
    assert isinstance(data["recent_activity"], list)
    assert len(data["recent_activity"]) > 0

@patch("app.api.endpoints.ConversationAnalyzer", return_value=MockConversationAnalyzer())
def test_get_popular_topics(mock_analyzer):
    """Testa a obtenção dos tópicos populares"""
    response = client.get("/analytics/popular-topics?days=7")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "topic" in data[0]
    assert "count" in data[0]
    assert "relevance_score" in data[0] 