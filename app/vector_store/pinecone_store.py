from typing import List, Dict, Any, Optional
import uuid

# Tentativa de importar Pinecone com tratamento de erro
try:
    from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion, VectorType
except ImportError:
    raise ImportError("Não foi possível importar Pinecone. Instale o pacote com: pip install pinecone")

from ..core.config import settings
from ..core.logging import logger
from .embeddings import EmbeddingGenerator

class PineconeManager:
    """Gerenciador de operações com Pinecone"""
    def __init__(
        self,
        api_key: str = None,
        environment: str = None,
        index_name: str = None
    ):
        self.api_key = api_key or settings.PINECONE_API_KEY
        self.environment = environment or settings.PINECONE_ENVIRONMENT
        self.index_name = index_name or settings.PINECONE_INDEX
        
        if not self.api_key:
            raise ValueError("Pinecone API Key não configurada")
        
        if not self.index_name:
            raise ValueError("Nome do índice Pinecone não configurado")
        
        # Inicializa o cliente Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        
        # Verifica se o índice existe, se não, cria
        self._ensure_index_exists()
        
        # Obtém o índice
        self.index = self.pc.Index(self.index_name)
        
        logger.info(f"PineconeManager inicializado com índice: {self.index_name}")
    
    def _ensure_index_exists(self):
        """Garante que o índice existe, criando-o se necessário"""
        # Lista os índices existentes
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        # Se o índice não existir, cria
        if self.index_name not in existing_indexes:
            logger.info(f"Criando índice Pinecone: {self.index_name}")
            
            # Cria o índice com as configurações padrão
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # Dimensão para embeddings OpenAI
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=CloudProvider.AWS,
                    region=AwsRegion.US_WEST_2
                ),
                vector_type=VectorType.DENSE
            )
            
            logger.info(f"Índice criado com sucesso: {self.index_name}")
    
    def upsert_documents(
        self,
        embedding_generator: EmbeddingGenerator,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Insere documentos no índice Pinecone
        
        Args:
            embedding_generator: Gerador de embeddings
            texts: Lista de textos para inserir
            metadatas: Lista de metadados para cada texto
            ids: Lista de IDs para cada texto (opcional)
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            if not texts:
                logger.warning("Nenhum texto fornecido para inserção")
                return False
            
            # Gera IDs aleatórios se não fornecidos
            if not ids:
                ids = [str(uuid.uuid4()) for _ in range(len(texts))]
            
            # Garante que metadatas é uma lista
            if not metadatas:
                metadatas = [{} for _ in range(len(texts))]
            
            # Verifica se os tamanhos são consistentes
            if len(texts) != len(ids) or len(texts) != len(metadatas):
                raise ValueError(
                    f"Tamanhos inconsistentes: texts={len(texts)}, "
                    f"ids={len(ids)}, metadatas={len(metadatas)}"
                )
            
            logger.info(f"Gerando embeddings para {len(texts)} textos")
            
            # Gera embeddings para os textos
            embeddings = embedding_generator.generate_embeddings(texts)
            
            # Prepara os vetores para inserção
            vectors = []
            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
                # Adiciona o texto ao metadata para recuperação posterior
                metadata["text"] = text
                
                # Formato atualizado para a nova API do Pinecone
                vectors.append((ids[i], embedding, metadata))
            
            # Insere os vetores no índice
            logger.info(f"Inserindo {len(vectors)} vetores no índice Pinecone")
            self.index.upsert(vectors=vectors)
            
            logger.info(f"Vetores inseridos com sucesso no índice: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inserir documentos no Pinecone: {str(e)}")
            return False
    
    async def search(
        self,
        embedding_generator: EmbeddingGenerator,
        query: str,
        top_k: int = 3,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos similares à query
        
        Args:
            embedding_generator: Gerador de embeddings
            query: Texto da consulta
            top_k: Número de resultados a retornar
            filter: Filtro para a busca (opcional)
            
        Returns:
            List[Dict]: Lista de resultados da busca
        """
        try:
            # Gera embedding para a query
            query_embedding = embedding_generator.generate_embeddings([query])[0]
            
            # Realiza a busca
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            # Formata os resultados
            formatted_results = []
            for match in results["matches"]:
                formatted_results.append({
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match["metadata"]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro ao buscar documentos no Pinecone: {str(e)}")
            return []
    
    def delete_documents(self, ids: List[str]) -> bool:
        """
        Exclui documentos do índice pelo ID
        
        Args:
            ids: Lista de IDs dos documentos a excluir
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            if not ids:
                logger.warning("Nenhum ID fornecido para exclusão")
                return False
            
            logger.info(f"Excluindo {len(ids)} documentos do índice Pinecone")
            self.index.delete(ids=ids)
            
            logger.info(f"Documentos excluídos com sucesso do índice: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao excluir documentos do Pinecone: {str(e)}")
            return False
    
    def delete_all(self) -> bool:
        """
        Exclui todos os documentos do índice
        
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            logger.info(f"Excluindo todos os documentos do índice: {self.index_name}")
            self.index.delete(delete_all=True)
            
            logger.info("Todos os documentos excluídos com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao excluir todos os documentos do Pinecone: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do índice
        
        Returns:
            Dict: Estatísticas do índice
        """
        try:
            stats = self.index.describe_index_stats()
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do Pinecone: {str(e)}")
            return {} 