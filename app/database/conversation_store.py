import os
import json
import time
import uuid
from typing import List, Dict, Any, Optional
from app.core.logging import logger

class ConversationStore:
    """
    Classe para gerenciar o armazenamento de conversas.
    """
    
    def __init__(self, db_path: str = "data/conversations"):
        """
        Inicializa o armazenamento de conversas.
        
        Args:
            db_path: Caminho para o diretório de armazenamento das conversas.
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """
        Garante que o diretório de armazenamento exista.
        """
        try:
            if not os.path.exists(self.db_path):
                os.makedirs(self.db_path, exist_ok=True)
                logger.info(f"Diretório de conversas criado: {self.db_path}")
        except Exception as e:
            logger.error(f"Erro ao criar diretório de conversas: {str(e)}")
            raise
    
    def _get_conversation_path(self, conversation_id: str) -> str:
        """
        Retorna o caminho para o arquivo de uma conversa.
        
        Args:
            conversation_id: ID da conversa.
            
        Returns:
            Caminho para o arquivo da conversa.
        """
        return os.path.join(self.db_path, f"{conversation_id}.json")
    
    def create_conversation(self) -> str:
        """
        Cria uma nova conversa.
        
        Returns:
            ID da conversa criada.
        """
        try:
            conversation_id = str(uuid.uuid4())
            conversation_data = {
                "id": conversation_id,
                "created_at": time.time(),
                "updated_at": time.time(),
                "messages": []
            }
            
            with open(self._get_conversation_path(conversation_id), "w", encoding="utf-8") as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Conversa criada: {conversation_id}")
            return conversation_id
        except Exception as e:
            logger.error(f"Erro ao criar conversa: {str(e)}")
            raise
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém os dados de uma conversa.
        
        Args:
            conversation_id: ID da conversa.
            
        Returns:
            Dados da conversa ou None se não existir.
        """
        try:
            conversation_path = self._get_conversation_path(conversation_id)
            
            if not os.path.exists(conversation_path):
                logger.warning(f"Conversa não encontrada: {conversation_id}")
                return None
            
            with open(conversation_path, "r", encoding="utf-8") as f:
                conversation_data = json.load(f)
            
            return conversation_data
        except Exception as e:
            logger.error(f"Erro ao obter conversa {conversation_id}: {str(e)}")
            return None
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        Lista todas as conversas.
        
        Returns:
            Lista de conversas.
        """
        try:
            conversations = []
            
            if not os.path.exists(self.db_path):
                return conversations
            
            for filename in os.listdir(self.db_path):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.db_path, filename), "r", encoding="utf-8") as f:
                            conversation_data = json.load(f)
                            conversations.append({
                                "id": conversation_data.get("id"),
                                "created_at": conversation_data.get("created_at"),
                                "updated_at": conversation_data.get("updated_at"),
                                "message_count": len(conversation_data.get("messages", []))
                            })
                    except Exception as e:
                        logger.error(f"Erro ao ler conversa {filename}: {str(e)}")
            
            # Ordena por data de atualização (mais recente primeiro)
            conversations.sort(key=lambda x: x.get("updated_at", 0), reverse=True)
            
            return conversations
        except Exception as e:
            logger.error(f"Erro ao listar conversas: {str(e)}")
            return []
    
    def add_message(self, conversation_id: str, message: Dict[str, Any]) -> bool:
        """
        Adiciona uma mensagem a uma conversa.
        
        Args:
            conversation_id: ID da conversa.
            message: Dados da mensagem.
            
        Returns:
            True se a mensagem foi adicionada com sucesso, False caso contrário.
        """
        try:
            conversation_data = self.get_conversation(conversation_id)
            
            if not conversation_data:
                logger.warning(f"Tentativa de adicionar mensagem a conversa inexistente: {conversation_id}")
                return False
            
            conversation_data["messages"].append(message)
            conversation_data["updated_at"] = time.time()
            
            with open(self._get_conversation_path(conversation_id), "w", encoding="utf-8") as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Mensagem adicionada à conversa {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem à conversa {conversation_id}: {str(e)}")
            return False
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Obtém todas as mensagens de uma conversa.
        
        Args:
            conversation_id: ID da conversa.
            
        Returns:
            Lista de mensagens.
        """
        try:
            conversation_data = self.get_conversation(conversation_id)
            
            if not conversation_data:
                logger.warning(f"Tentativa de obter mensagens de conversa inexistente: {conversation_id}")
                return []
            
            return conversation_data.get("messages", [])
        except Exception as e:
            logger.error(f"Erro ao obter mensagens da conversa {conversation_id}: {str(e)}")
            return []
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Limpa todas as mensagens de uma conversa.
        
        Args:
            conversation_id: ID da conversa.
            
        Returns:
            True se a conversa foi limpa com sucesso, False caso contrário.
        """
        try:
            conversation_data = self.get_conversation(conversation_id)
            
            if not conversation_data:
                logger.warning(f"Tentativa de limpar conversa inexistente: {conversation_id}")
                return False
            
            conversation_data["messages"] = []
            conversation_data["updated_at"] = time.time()
            
            with open(self._get_conversation_path(conversation_id), "w", encoding="utf-8") as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Conversa limpa: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar conversa {conversation_id}: {str(e)}")
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Exclui uma conversa.
        
        Args:
            conversation_id: ID da conversa.
            
        Returns:
            True se a conversa foi excluída com sucesso, False caso contrário.
        """
        try:
            conversation_path = self._get_conversation_path(conversation_id)
            
            if not os.path.exists(conversation_path):
                logger.warning(f"Tentativa de excluir conversa inexistente: {conversation_id}")
                return False
            
            os.remove(conversation_path)
            logger.info(f"Conversa excluída: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir conversa {conversation_id}: {str(e)}")
            return False 