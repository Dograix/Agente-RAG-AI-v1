import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import Callable
from ..core.logging import logger
from .extractors import DocumentProcessor
from .chunking import TextChunker

class DocumentHandler(FileSystemEventHandler):
    def __init__(
        self,
        processor: DocumentProcessor,
        chunker: TextChunker,
        on_chunks_ready: Callable[[str, list[str]], None]
    ):
        self.processor = processor
        self.chunker = chunker
        self.on_chunks_ready = on_chunks_ready
        self.supported_extensions = {'.pdf', '.docx'}
    
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix.lower() not in self.supported_extensions:
            return
            
        logger.info(f"Novo arquivo detectado: {file_path}")
        
        try:
            # Processa o documento
            text = self.processor.process_document(str(file_path))
            
            # Cria chunks do texto
            chunks = self.chunker.create_chunks(text)
            
            # Notifica que os chunks estão prontos
            self.on_chunks_ready(str(file_path), chunks)
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")

class FileWatcher:
    def __init__(
        self,
        watch_path: str,
        processor: DocumentProcessor,
        chunker: TextChunker,
        on_chunks_ready: Callable[[str, list[str]], None]
    ):
        self.watch_path = watch_path
        self.event_handler = DocumentHandler(processor, chunker, on_chunks_ready)
        self.observer = Observer()
    
    def start(self):
        """Inicia o monitoramento do diretório"""
        logger.info(f"Iniciando monitoramento do diretório: {self.watch_path}")
        self.observer.schedule(self.event_handler, self.watch_path, recursive=False)
        self.observer.start()
        
    def stop(self):
        """Para o monitoramento"""
        logger.info("Parando monitoramento de arquivos")
        self.observer.stop()
        self.observer.join() 