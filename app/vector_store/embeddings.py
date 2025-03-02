from typing import List
import openai
from ..core.logging import logger
from ..core.config import settings

class EmbeddingGenerator:
    def __init__(
        self,
        api_key: str = None,
        model: str = None
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_EMBEDDING_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API Key não configurada")
        
        # Configura a API key
        openai.api_key = self.api_key
        
        logger.info(f"EmbeddingGenerator inicializado com modelo: {self.model}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos
        
        Args:
            texts: Lista de textos para gerar embeddings
            
        Returns:
            List[List[float]]: Lista de embeddings
        """
        try:
            if not texts:
                logger.warning("Nenhum texto fornecido para gerar embeddings")
                return []
            
            # Filtra textos vazios
            filtered_texts = [text for text in texts if text and text.strip()]
            
            if not filtered_texts:
                logger.warning("Todos os textos estão vazios")
                return []
            
            logger.info(f"Gerando embeddings para {len(filtered_texts)} textos")
            
            # Gera embeddings usando a API da OpenAI
            response = openai.embeddings.create(
                model=self.model,
                input=filtered_texts
            )
            
            # Extrai os embeddings da resposta
            embeddings = [item.embedding for item in response.data]
            
            logger.info(f"Embeddings gerados com sucesso: {len(embeddings)}")
            
            # Se alguns textos foram filtrados, precisamos preencher com embeddings vazios
            if len(filtered_texts) < len(texts):
                # Cria um embedding vazio com a mesma dimensão dos outros
                empty_embedding = [0.0] * len(embeddings[0])
                
                # Reconstrói a lista de embeddings com os vazios nas posições corretas
                result = []
                filtered_idx = 0
                
                for text in texts:
                    if text and text.strip():
                        result.append(embeddings[filtered_idx])
                        filtered_idx += 1
                    else:
                        result.append(empty_embedding)
                
                return result
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {str(e)}")
            raise

    async def generate_query_embedding(self, query: str) -> List[float]:
        """Gera embedding para uma query de busca"""
        try:
            logger.info("Gerando embedding para query de busca")
            
            embedding = await self.embeddings.aembed_query(query)
            
            logger.info(
                "Embedding de query gerado com sucesso",
                extra={"embedding_dim": len(embedding)}
            )
            
            return embedding
            
        except Exception as e:
            logger.error(f"Erro ao gerar embedding de query: {str(e)}")
            raise 