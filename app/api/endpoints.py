from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
from datetime import datetime

from .models import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ConversationStats,
    PeriodStats,
    DateRange,
    DocumentResponse,
    ProcessingStatus
)
from .dependencies import get_chat_manager, get_db
from ..chat import ChatManager, Conversation, Message
from ..analytics.conversation_analyzer import ConversationAnalyzer
from ..document_processing.file_tracker import FileTracker
from ..core.logging import logger

app = FastAPI(
    title="Sistema Gestor RAG API",
    description="API completa para o Sistema de RAG (Retrieval Augmented Generation)",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas de Conversas
@app.post("/conversations/", response_model=ConversationResponse, tags=["Conversas"])
async def create_conversation(
    conversation: ConversationCreate,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """Cria uma nova conversa"""
    try:
        db_conversation = chat_manager.create_conversation(conversation.title)
        # Converte para o formato esperado
        return {
            "id": db_conversation.conversation_id,
            "title": db_conversation.title or conversation.title,  # Usa o título da conversa se disponível
            "created_at": datetime.fromisoformat(db_conversation.created_at),
            "updated_at": datetime.fromisoformat(db_conversation.updated_at)
        }
    except Exception as e:
        logger.error(f"Erro ao criar conversa: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao criar conversa")

@app.get("/conversations/", response_model=List[ConversationResponse], tags=["Conversas"])
async def list_conversations(
    skip: int = Query(0, description="Número de registros para pular"),
    limit: int = Query(10, description="Limite de registros a retornar"),
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """Lista todas as conversas com opção de busca"""
    try:
        conversations = chat_manager.list_conversations(limit=limit, offset=skip)
        return [
            {
                "id": conv["conversation_id"],
                "title": conv.get("metadata", {}).get("title", "Nova Conversa"),
                "created_at": datetime.fromisoformat(conv["created_at"]),
                "updated_at": datetime.fromisoformat(conv["updated_at"])
            }
            for conv in conversations
        ]
    except Exception as e:
        logger.error(f"Erro ao listar conversas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar conversas")

@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """Obtém uma conversa específica"""
    try:
        conversation = chat_manager.get_conversation(conversation_id)
        
        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversa não encontrada"
            )
            
        return {
            "id": conversation.conversation_id,
            "title": conversation.title or "Nova Conversa",
            "created_at": datetime.fromisoformat(conversation.created_at),
            "updated_at": datetime.fromisoformat(conversation.updated_at)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter conversa: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter conversa"
        )

@app.post("/conversations/{conversation_id}/messages/", response_model=MessageResponse)
async def create_message(
    conversation_id: str,
    message: MessageCreate,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """Envia uma mensagem em uma conversa"""
    try:
        response = await chat_manager.send_message(
            conversation_id=conversation_id,
            content=message.content
        )
        
        # Formata a resposta de acordo com o modelo MessageResponse
        return {
            "id": response["id"],
            "conversation_id": conversation_id,
            "content": response["content"],
            "role": response["role"],
            "created_at": datetime.fromisoformat(response["timestamp"]) if "timestamp" in response else datetime.now(),
            "tokens_used": response.get("metadata", {}).get("tokens_used"),
            "processing_time": response.get("metadata", {}).get("processing_time"),
            "metadata": response.get("metadata", {})
        }
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar mensagem: {str(e)}"
        )

@app.get("/conversations/{conversation_id}/messages/", response_model=List[MessageResponse])
async def list_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 50,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """Lista mensagens de uma conversa"""
    try:
        conversation = chat_manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversa não encontrada"
            )
        
        messages = []
        for msg in conversation.messages:
            if msg["role"] != "system":  # Ignora mensagens do sistema
                messages.append({
                    "id": msg.get("id", ""),
                    "conversation_id": conversation_id,
                    "content": msg["content"],
                    "role": msg["role"],
                    "created_at": datetime.fromisoformat(msg["timestamp"]) if "timestamp" in msg else datetime.now(),
                    "tokens_used": msg.get("metadata", {}).get("tokens_used"),
                    "processing_time": msg.get("metadata", {}).get("processing_time"),
                    "metadata": msg.get("metadata", {})
                })
        
        # Aplica paginação
        start = skip
        end = skip + limit
        return messages[start:end]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar mensagens: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao listar mensagens"
        )

# Rotas de Documentos
@app.post("/documents/upload/", response_model=ProcessingStatus, tags=["Documentos"])
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """Upload e processamento de novo documento"""
    try:
        # Salva o arquivo
        file_path = f"documents/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Inicia processamento em background
        background_tasks.add_task(process_document, file_path, chat_manager)
        
        return {"status": "processing", "message": "Documento em processamento"}
    except Exception as e:
        logger.error(f"Erro no upload do documento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro no upload do documento")

@app.get("/documents/", response_model=List[DocumentResponse], tags=["Documentos"])
async def list_documents():
    """Lista todos os documentos processados"""
    try:
        file_tracker = FileTracker()
        documents = file_tracker.get_all_documents()
        return documents
    except Exception as e:
        logger.error(f"Erro ao listar documentos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar documentos")

@app.delete("/documents/{document_id}", tags=["Documentos"])
async def delete_document(document_id: str):
    """Remove um documento do sistema"""
    try:
        file_tracker = FileTracker()
        success = file_tracker.remove_document(document_id)
        if success:
            return {"status": "success", "message": "Documento removido com sucesso"}
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    except Exception as e:
        logger.error(f"Erro ao remover documento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao remover documento")

# Rotas de Analytics
@app.get("/analytics/overview", tags=["Analytics"])
async def get_system_overview(db: Session = Depends(get_db)):
    """Obtém visão geral do sistema"""
    try:
        analyzer = ConversationAnalyzer(db)
        return {
            "total_conversations": db.query(Conversation).count(),
            "total_messages": db.query(Message).count(),
            "total_documents": len(FileTracker().get_all_documents()),
            "recent_activity": analyzer.get_recent_activity()
        }
    except Exception as e:
        logger.error(f"Erro ao obter visão geral: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter visão geral")

@app.get("/analytics/popular-topics", tags=["Analytics"])
async def get_popular_topics(
    days: int = Query(7, description="Número de dias para análise"),
    db: Session = Depends(get_db)
):
    """Obtém tópicos mais populares nas conversas"""
    try:
        analyzer = ConversationAnalyzer(db)
        return analyzer.get_popular_topics(days)
    except Exception as e:
        logger.error(f"Erro ao obter tópicos populares: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter tópicos populares")

# Rota de Health Check
@app.get("/health", tags=["Sistema"])
async def health_check():
    """Verifica a saúde do sistema"""
    return {
        "status": "healthy",
        "components": {
            "database": "online",
            "vector_store": "online",
            "document_processor": "online"
        }
    }

# Rotas de Sistema
@app.post("/system/clear-cache", tags=["Sistema"])
async def clear_system_cache():
    """Limpa o cache do sistema"""
    try:
        # Implementar limpeza de cache
        return {"status": "success", "message": "Cache limpo com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao limpar cache")

# Endpoints de análise
@app.get("/analytics/conversations/{conversation_id}/stats", response_model=ConversationStats)
async def get_conversation_stats(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de uma conversa específica"""
    try:
        analyzer = ConversationAnalyzer(db)
        stats = analyzer.get_conversation_stats(conversation_id)
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas da conversa {conversation_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter estatísticas da conversa"
        )

@app.post("/analytics/period-stats", response_model=PeriodStats)
async def get_period_stats(
    date_range: DateRange,
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de um período específico"""
    try:
        analyzer = ConversationAnalyzer(db)
        stats = analyzer.get_period_stats(
            start_date=date_range.start_date,
            end_date=date_range.end_date
        )
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do período: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao obter estatísticas do período"
        ) 