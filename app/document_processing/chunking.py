from typing import List
from ..core.config import settings
from ..core.logging import logger

class TextChunker:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def _find_sentence_end(self, text: str, position: int) -> int:
        """Encontra o fim da sentença mais próximo após a posição especificada"""
        sentence_endings = ['. ', '! ', '? ', '\n\n']
        min_end = len(text)
        
        for ending in sentence_endings:
            pos = text.find(ending, position)
            if pos != -1 and pos < min_end:
                min_end = pos + len(ending)
        
        # Se não encontrar um fim de sentença, retorna o próprio position
        return min_end if min_end < len(text) else position

    def create_chunks(self, text: str) -> List[str]:
        """Divide o texto em chunks respeitando o fim das sentenças"""
        logger.info("Iniciando processo de chunking do texto")
        
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Define o fim do chunk atual
            end = start + self.chunk_size
            
            if end >= text_length:
                # Se chegamos ao fim do texto
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break
            
            # Encontra o fim da sentença mais próximo
            end = self._find_sentence_end(text, end)
            
            # Extrai o chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Atualiza a posição inicial para o próximo chunk
            start = end - self.chunk_overlap
        
        logger.info(
            f"Chunking concluído",
            extra={
                "total_chunks": len(chunks),
                "avg_chunk_size": sum(len(c) for c in chunks) / len(chunks) if chunks else 0
            }
        )
        
        return chunks 