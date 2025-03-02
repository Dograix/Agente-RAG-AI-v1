import os
import sys
from app.document_processing.extractors import DocumentProcessor
from app.document_processing.chunking import TextChunker
from app.vector_store.embeddings import EmbeddingGenerator
from app.vector_store.pinecone_store import PineconeManager
from app.core.logging import logger
from app.core.config import settings

def process_file(file_path, document_processor, chunker, embedding_generator, pinecone_manager):
    """Processa um arquivo e armazena no Pinecone"""
    try:
        # Extrai o nome do arquivo para usar como ID do documento
        file_name = os.path.basename(file_path)
        doc_id = os.path.splitext(file_name)[0]
        
        logger.info(f"Processando arquivo: {file_path}")
        
        # Extrai o texto do arquivo
        text = document_processor.process_document(file_path)
        if not text:
            logger.warning(f"Nenhum texto extraído de {file_path}")
            return False
        
        logger.info(f"Texto extraído com sucesso: {len(text)} caracteres")
        
        # Divide o texto em chunks
        chunks = chunker.create_chunks(text)
        logger.info(f"Texto dividido em {len(chunks)} chunks")
        
        # Prepara metadados para cada chunk
        metadatas = []
        for i in range(len(chunks)):
            metadatas.append({
                "source": file_path,
                "doc_id": doc_id,
                "chunk_index": i
            })
        
        # Armazena os chunks no Pinecone
        pinecone_manager.upsert_documents(
            embedding_generator=embedding_generator,
            texts=chunks,
            metadatas=metadatas
        )
        
        logger.info(f"Documento armazenado com sucesso no Pinecone: {doc_id}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
        return False

def main():
    """Função principal"""
    # Inicializa componentes
    document_processor = DocumentProcessor()
    chunker = TextChunker()
    embedding_generator = EmbeddingGenerator(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_EMBEDDING_MODEL
    )
    pinecone_manager = PineconeManager(
        api_key=settings.PINECONE_API_KEY,
        environment=settings.PINECONE_ENVIRONMENT,
        index_name=settings.PINECONE_INDEX
    )
    
    # Diretório de documentos
    documents_dir = "documents"
    
    # Verifica se o diretório existe
    if not os.path.exists(documents_dir):
        logger.error(f"Diretório de documentos não encontrado: {documents_dir}")
        sys.exit(1)
    
    # Lista de extensões suportadas
    supported_extensions = [".txt", ".pdf", ".docx", ".md"]
    
    # Processa todos os arquivos no diretório
    files_processed = 0
    for file_name in os.listdir(documents_dir):
        file_path = os.path.join(documents_dir, file_name)
        
        # Verifica se é um arquivo e tem extensão suportada
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(file_name)[1].lower()
            if file_ext in supported_extensions:
                success = process_file(
                    file_path, 
                    document_processor, 
                    chunker, 
                    embedding_generator, 
                    pinecone_manager
                )
                if success:
                    files_processed += 1
    
    logger.info(f"Processamento concluído. {files_processed} arquivos processados.")

if __name__ == "__main__":
    main() 