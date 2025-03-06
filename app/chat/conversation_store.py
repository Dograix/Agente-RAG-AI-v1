import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..core.logging import logger

class Conversation:
    """Representa uma conversa entre o usuário e o sistema"""
    
    def __init__(self, conversation_id: str = None, user_id: str = "default_user"):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.messages = []
        self.metadata = {}
        self.title = None
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Adiciona uma mensagem à conversa"""
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.updated_at = message["timestamp"]
        return message["id"]
    
    def get_messages(self, as_dict: bool = False):
        """Retorna todas as mensagens da conversa"""
        if as_dict:
            return [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in self.messages
            ]
        return self.messages
    
    def to_dict(self):
        """Converte a conversa para um dicionário"""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": self.messages,
            "metadata": self.metadata,
            "title": self.title
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Cria uma conversa a partir de um dicionário"""
        conversation = cls(
            conversation_id=data.get("conversation_id"),
            user_id=data.get("user_id", "default_user")
        )
        conversation.created_at = data.get("created_at", conversation.created_at)
        conversation.updated_at = data.get("updated_at", conversation.updated_at)
        conversation.messages = data.get("messages", [])
        conversation.metadata = data.get("metadata", {})
        conversation.title = data.get("title")
        return conversation


class ConversationStore:
    """Gerencia o armazenamento e recuperação de conversas"""
    
    def __init__(self, storage_dir: str = "data/conversations"):
        self.storage_dir = storage_dir
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Garante que o diretório de armazenamento existe"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def _get_user_dir(self, user_id: str):
        """Obtém o diretório de um usuário específico"""
        user_dir = os.path.join(self.storage_dir, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return user_dir
    
    def _get_conversation_path(self, conversation_id: str, user_id: str):
        """Obtém o caminho do arquivo de uma conversa"""
        user_dir = self._get_user_dir(user_id)
        return os.path.join(user_dir, f"{conversation_id}.json")
    
    def create_conversation(self, user_id: str = "default_user", metadata: Dict[str, Any] = None) -> Conversation:
        """Cria uma nova conversa"""
        conversation = Conversation(user_id=user_id)
        
        if metadata:
            conversation.metadata = metadata
            # Adiciona o título aos atributos principais da conversa
            if "title" in metadata:
                conversation.title = metadata["title"]
        
        # Salva a conversa
        self.save_conversation(conversation)
        
        logger.info(
            f"Nova conversa criada",
            extra={
                "conversation_id": conversation.conversation_id,
                "user_id": user_id
            }
        )
        
        return conversation
    
    def save_conversation(self, conversation: Conversation) -> bool:
        """Salva uma conversa no armazenamento"""
        try:
            file_path = self._get_conversation_path(
                conversation.conversation_id, 
                conversation.user_id
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation.to_dict(), f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar conversa: {str(e)}")
            return False
    
    def get_conversation(self, conversation_id: str, user_id: str = "default_user") -> Optional[Conversation]:
        """Recupera uma conversa pelo ID"""
        try:
            file_path = self._get_conversation_path(conversation_id, user_id)
            
            if not os.path.exists(file_path):
                logger.warning(f"Conversa não encontrada: {conversation_id}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Conversation.from_dict(data)
        except Exception as e:
            logger.error(f"Erro ao recuperar conversa {conversation_id}: {str(e)}")
            return None
    
    def list_conversations(self, user_id: str = "default_user", limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Lista as conversas de um usuário"""
        try:
            user_dir = self._get_user_dir(user_id)
            
            # Lista todos os arquivos JSON no diretório do usuário
            files = [f for f in os.listdir(user_dir) if f.endswith('.json')]
            
            # Ordena por data de modificação (mais recente primeiro)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(user_dir, x)), reverse=True)
            
            # Aplica paginação
            paginated_files = files[offset:offset+limit] if limit > 0 else files
            
            # Carrega os metadados básicos de cada conversa
            conversations = []
            for file_name in paginated_files:
                conversation_id = file_name.replace('.json', '')
                conversation = self.get_conversation(conversation_id, user_id)
                
                if conversation:
                    # Inclui apenas os metadados básicos e a última mensagem
                    conversations.append({
                        "conversation_id": conversation.conversation_id,
                        "created_at": conversation.created_at,
                        "updated_at": conversation.updated_at,
                        "message_count": len(conversation.messages),
                        "last_message": conversation.messages[-1] if conversation.messages else None,
                        "metadata": conversation.metadata
                    })
            
            return conversations
        except Exception as e:
            logger.error(f"Erro ao listar conversas do usuário {user_id}: {str(e)}")
            return []
    
    def delete_conversation(self, conversation_id: str, user_id: str = "default_user") -> bool:
        """Exclui uma conversa"""
        try:
            file_path = self._get_conversation_path(conversation_id, user_id)
            
            if not os.path.exists(file_path):
                logger.warning(f"Conversa não encontrada para exclusão: {conversation_id}")
                return False
            
            os.remove(file_path)
            logger.info(f"Conversa excluída: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir conversa {conversation_id}: {str(e)}")
            return False
    
    def add_message_to_conversation(
        self, 
        conversation_id: str, 
        role: str, 
        content: str, 
        user_id: str = "default_user",
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Adiciona uma mensagem a uma conversa existente"""
        conversation = self.get_conversation(conversation_id, user_id)
        
        if not conversation:
            logger.warning(f"Tentativa de adicionar mensagem a conversa inexistente: {conversation_id}")
            return None
        
        # Adiciona a mensagem
        message_id = conversation.add_message(role, content, metadata)
        
        # Salva a conversa atualizada
        if self.save_conversation(conversation):
            return message_id
        
        return None 