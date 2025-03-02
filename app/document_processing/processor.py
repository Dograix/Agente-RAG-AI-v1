import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
import docx
from ..core.logging import logger
from .file_tracker import FileTracker
from ..vector_store.embeddings import EmbeddingGenerator
from ..vector_store.store import VectorStore

class DocumentProcessor:
    def __init__(self):
        self.file_tracker = FileTracker()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()

    async def process_document(self, file_path: Path) -> bool:
        """Processa um documento e gera embeddings"""
        try:
            # Extrai texto do documento
            text_chunks = self._extract_text(file_path)
            if not text_chunks:
                raise ValueError("Não foi possível extrair texto do documento")

            # Gera embeddings
            embeddings = await self._generate_embeddings(text_chunks)
            if not embeddings:
                raise ValueError("Falha ao gerar embeddings")

            # Salva no vector store
            doc_id = file_path.stem
            self.vector_store.add_embeddings(doc_id, text_chunks, embeddings)

            # Atualiza status do documento
            self.file_tracker.update_document_status(
                doc_id,
                status="processed",
                processed=True,
                embedding_count=len(embeddings)
            )

            return True

        except Exception as e:
            logger.error(f"Erro ao processar documento {file_path}: {str(e)}")
            self.file_tracker.update_document_status(
                file_path.stem,
                status="error",
                processed=False,
                error_message=str(e)
            )
            return False

    def _extract_text(self, file_path: Path) -> List[str]:
        """Extrai texto do documento em chunks"""
        file_type = file_path.suffix.lower()
        
        if file_type == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_type in ['.doc', '.docx']:
            return self._extract_from_word(file_path)
        elif file_type in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            return self._extract_from_text(file_path)
        else:
            raise ValueError(f"Tipo de arquivo não suportado: {file_type}")

    def _extract_from_pdf(self, file_path: Path) -> List[str]:
        """Extrai texto de arquivos PDF"""
        chunks = []
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        # Divide o texto em chunks menores se necessário
                        chunks.extend(self._split_into_chunks(text))
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF {file_path}: {str(e)}")
        return chunks

    def _extract_from_word(self, file_path: Path) -> List[str]:
        """Extrai texto de arquivos Word"""
        chunks = []
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    chunks.extend(self._split_into_chunks(text))
        except Exception as e:
            logger.error(f"Erro ao extrair texto do Word {file_path}: {str(e)}")
        return chunks

    def _extract_from_text(self, file_path: Path) -> List[str]:
        """Extrai texto de arquivos de texto"""
        chunks = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                chunks.extend(self._split_into_chunks(text))
        except Exception as e:
            logger.error(f"Erro ao extrair texto do arquivo {file_path}: {str(e)}")
        return chunks

    def _split_into_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Divide texto em chunks menores"""
        chunks = []
        words = text.split()
        current_chunk = []
        current_size = 0

        for word in words:
            word_size = len(word) + 1  # +1 para o espaço
            if current_size + word_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    async def _generate_embeddings(self, text_chunks: List[str]) -> List[List[float]]:
        """Gera embeddings para chunks de texto"""
        try:
            embeddings = []
            for chunk in text_chunks:
                embedding = await self.embedding_generator.generate(chunk)
                if embedding:
                    embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {str(e)}")
            return []

    async def process_directory(self, directory: Path):
        """Processa todos os documentos em um diretório"""
        try:
            tasks = []
            for file_path in directory.glob('*'):
                if file_path.is_file() and not self.file_tracker.get_document(file_path.stem):
                    tasks.append(self.process_document(file_path))
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return all(isinstance(r, bool) and r for r in results)
            return True
        except Exception as e:
            logger.error(f"Erro ao processar diretório {directory}: {str(e)}")
            return False 