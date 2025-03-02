from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from ..chat import Conversation, Message
from ..core.logging import logger

class ConversationAnalyzer:
    def __init__(self, db: Session):
        self.db = db
    
    def get_conversation_stats(self, conversation_id: int) -> Dict[str, Any]:
        """Obtém estatísticas de uma conversa específica"""
        try:
            # Busca mensagens da conversa
            messages = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).all()
            
            # Calcula estatísticas
            stats = {
                "total_messages": len(messages),
                "user_messages": sum(1 for m in messages if m.role == "user"),
                "assistant_messages": sum(1 for m in messages if m.role == "assistant"),
                "avg_response_time": self._calculate_avg_response_time(messages),
                "sources_used": self._get_sources_used(messages),
                "avg_similarity_score": self._calculate_avg_similarity(messages),
                "conversation_duration": self._get_conversation_duration(messages)
            }
            
            return stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas da conversa {conversation_id}: {str(e)}")
            raise
    
    def get_period_stats(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Obtém estatísticas de todas as conversas em um período"""
        try:
            # Busca conversas no período
            conversations = self.db.query(Conversation).filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at <= end_date
                )
            ).all()
            
            # Estatísticas gerais
            stats = {
                "total_conversations": len(conversations),
                "total_messages": 0,
                "avg_messages_per_conversation": 0,
                "most_active_sources": self._get_most_active_sources(start_date, end_date),
                "hourly_distribution": self._get_hourly_distribution(start_date, end_date),
                "avg_conversation_duration": timedelta(0)
            }
            
            # Calcula totais
            if conversations:
                all_messages = []
                total_duration = timedelta(0)
                
                for conv in conversations:
                    messages = conv.messages
                    all_messages.extend(messages)
                    
                    if messages:
                        duration = messages[-1].created_at - messages[0].created_at
                        total_duration += duration
                
                stats["total_messages"] = len(all_messages)
                stats["avg_messages_per_conversation"] = len(all_messages) / len(conversations)
                stats["avg_conversation_duration"] = total_duration / len(conversations)
            
            return stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do período: {str(e)}")
            raise
    
    def _calculate_avg_response_time(self, messages: List[Message]) -> timedelta:
        """Calcula tempo médio de resposta do assistente"""
        response_times = []
        
        for i in range(len(messages) - 1):
            if messages[i].role == "user" and messages[i+1].role == "assistant":
                response_time = messages[i+1].created_at - messages[i].created_at
                response_times.append(response_time)
        
        if response_times:
            return sum(response_times, timedelta(0)) / len(response_times)
        return timedelta(0)
    
    def _get_sources_used(self, messages: List[Message]) -> Dict[str, int]:
        """Conta frequência de uso de cada fonte"""
        sources = {}
        for message in messages:
            if message.context_source:
                sources[message.context_source] = sources.get(message.context_source, 0) + 1
        return sources
    
    def _calculate_avg_similarity(self, messages: List[Message]) -> float:
        """Calcula score médio de similaridade"""
        scores = [m.similarity_score for m in messages if m.similarity_score is not None]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _get_conversation_duration(self, messages: List[Message]) -> timedelta:
        """Calcula duração total da conversa"""
        if not messages:
            return timedelta(0)
        return messages[-1].created_at - messages[0].created_at
    
    def _get_most_active_sources(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Identifica as fontes mais utilizadas no período"""
        sources = self.db.query(
            Message.context_source,
            func.count(Message.id).label('count')
        ).filter(
            and_(
                Message.created_at >= start_date,
                Message.created_at <= end_date,
                Message.context_source.isnot(None)
            )
        ).group_by(Message.context_source).all()
        
        return {source: count for source, count in sources}
    
    def _get_hourly_distribution(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[int, int]:
        """Analisa distribuição de mensagens por hora do dia"""
        messages = self.db.query(
            func.extract('hour', Message.created_at).label('hour'),
            func.count(Message.id).label('count')
        ).filter(
            and_(
                Message.created_at >= start_date,
                Message.created_at <= end_date
            )
        ).group_by('hour').all()
        
        return {int(hour): count for hour, count in messages} 