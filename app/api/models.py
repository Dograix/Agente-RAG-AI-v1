from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

class MessageBase(BaseModel):
    content: str = Field(..., description="Conteúdo da mensagem")
    role: str = Field(..., description="Papel do remetente (user/assistant)")

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    created_at: datetime
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str = Field(..., description="Título da conversa")

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: str = Field(..., description="ID único da conversa")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationStats(BaseModel):
    total_messages: int
    average_response_time: float
    user_message_count: int
    assistant_message_count: int
    total_tokens_used: int

class PeriodStats(BaseModel):
    period: str
    conversation_count: int
    message_count: int
    average_response_time: float

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_date: datetime
    status: str
    size_bytes: int
    processed: bool
    embedding_count: Optional[int] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class ProcessingStatus(BaseModel):
    status: str
    message: str

class SystemOverview(BaseModel):
    total_conversations: int
    total_messages: int
    total_documents: int
    recent_activity: List[Dict]

class PopularTopic(BaseModel):
    topic: str
    count: int
    relevance_score: float

class ErrorResponse(BaseModel):
    detail: str 