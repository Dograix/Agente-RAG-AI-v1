import os
import time
import asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.document_processing.extractors import DocumentProcessor
from app.document_processing.chunking import TextChunker
from app.vector_store.embeddings import EmbeddingGenerator
from app.vector_store.pinecone_store import PineconeManager
from app.core.config import settings
from app.core.logging import logger
from app.document_processing.file_tracker import FileTracker

class DocumentHandler(FileSystemEventHandler):
    def __init__(self):
        self.processor = DocumentProcessor()
        self.chunker = TextChunker()
        self.embedding_generator = EmbeddingGenerator()
        self.pinecone_manager = PineconeManager(settings.PINECONE_INDEX_NAME)
        self.file_tracker = FileTracker()
        self.processing_queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop()
        self.task = self.loop.create_task(self.process_queue())
    
    async def process_queue(self):
        """Processa arquivos na fila"""
        while True:
            file_path = await self.processing_queue.get()
            try:
                await self.process_file(file_path)
            except Exception as e:
                logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
            finally:
                self.processing_queue.task_done()
    
    async def process_file(self, file_path):
        """Processa um único arquivo"""
        try:
            # Verifica se o arquivo já foi processado
            if self.file_tracker.is_file_processed(file_path):
                logger.info(f"Arquivo já processado anteriormente: {file_path}")
                return
                
            # Aguarda um pouco para garantir que o arquivo foi completamente escrito
            await asyncio.sleep(1)
                
            # Extrai o texto do documento
            text = self.processor.process_document(file_path)
            
            # Divide o texto em chunks
            chunks = self.chunker.create_chunks(text)
            
            if not chunks:
                logger.warning(f"Nenhum chunk gerado para o arquivo: {file_path}")
                return
            
            # Marca o arquivo como processado e obtém o ID
            doc_id = self.file_tracker.mark_as_processed(file_path, {
                "chunks": len(chunks),
                "index": settings.PINECONE_INDEX_NAME
            })
            
            # Prepara os metadados
            metadata = []
            for i in range(len(chunks)):
                metadata.append({
                    "source": str(file_path),
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
            
            # Armazena os chunks no Pinecone
            await self.pinecone_manager.upsert_documents(
                embedding_generator=self.embedding_generator,
                texts=chunks,
                metadata=metadata
            )
            
            logger.info(f"Arquivo processado com sucesso: {file_path} (ID: {doc_id})")
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
    
    def on_created(self, event):
        """Manipula evento de criação de arquivo"""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Verifica se a extensão é suportada
        if file_path.suffix.lower() in settings.SUPPORTED_EXTENSIONS:
            logger.info(f"Novo arquivo detectado: {file_path}")
            self.loop.call_soon_threadsafe(
                self.processing_queue.put_nowait, 
                str(file_path)
            )
        else:
            logger.warning(
                f"Arquivo ignorado (formato não suportado): {file_path}",
                extra={"extension": file_path.suffix}
            )

async def main():
    """Função principal"""
    # Diretório a ser monitorado
    documents_dir = Path("documents")
    
    # Cria o diretório se não existir
    if not documents_dir.exists():
        os.makedirs(documents_dir)
        logger.info(f"Diretório criado: {documents_dir}")
    
    # Configura o observador
    event_handler = DocumentHandler()
    observer = Observer()
    observer.schedule(event_handler, str(documents_dir), recursive=False)
    
    # Inicia o observador
    observer.start()
    logger.info(f"Monitoramento iniciado no diretório: {documents_dir}")
    logger.info(f"Formatos suportados: {', '.join(settings.SUPPORTED_EXTENSIONS)}")
    
    try:
        # Mantém o programa em execução
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Para o observador ao receber Ctrl+C
        observer.stop()
        logger.info("Monitoramento interrompido pelo usuário")
    
    # Aguarda o observador finalizar
    observer.join()
    logger.info("Monitoramento finalizado")

if __name__ == "__main__":
    asyncio.run(main()) 