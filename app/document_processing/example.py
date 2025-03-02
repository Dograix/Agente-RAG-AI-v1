from pathlib import Path
from .extractors import DocumentProcessor
from .chunking import TextChunker
from .file_watcher import FileWatcher
from ..core.logging import logger

def on_chunks_ready(file_path: str, chunks: list[str]):
    """Callback chamado quando os chunks estão prontos"""
    logger.info(
        f"Chunks prontos para o arquivo: {file_path}",
        extra={
            "num_chunks": len(chunks),
            "first_chunk_preview": chunks[0][:100] if chunks else ""
        }
    )

def main():
    # Cria diretório de documentos se não existir
    docs_dir = Path("documents")
    docs_dir.mkdir(exist_ok=True)
    
    # Inicializa os componentes
    processor = DocumentProcessor()
    chunker = TextChunker()
    
    # Inicializa o watcher
    watcher = FileWatcher(
        watch_path=str(docs_dir),
        processor=processor,
        chunker=chunker,
        on_chunks_ready=on_chunks_ready
    )
    
    try:
        logger.info("Iniciando sistema de processamento de documentos")
        watcher.start()
        
        # Mantém o programa rodando
        while True:
            input("Pressione Enter para sair...")
            break
            
    except KeyboardInterrupt:
        logger.info("Interrupção do usuário detectada")
    finally:
        watcher.stop()
        logger.info("Sistema de processamento finalizado")

if __name__ == "__main__":
    main() 