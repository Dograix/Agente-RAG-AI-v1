import asyncio
from datetime import datetime
from pathlib import Path
from ..document_processing import DocumentProcessor, TextChunker
from .embeddings import EmbeddingGenerator
from .pinecone_store import PineconeManager
from ..core.logging import logger

async def process_and_store_document(
    file_path: str,
    embedding_generator: EmbeddingGenerator,
    pinecone_manager: PineconeManager
):
    """Processa um documento e armazena no Pinecone"""
    try:
        # Processa o documento
        processor = DocumentProcessor()
        text = processor.process_document(file_path)
        
        # Divide em chunks
        chunker = TextChunker()
        chunks = chunker.create_chunks(text)
        
        # Prepara metadados
        metadata = [{
            "source": file_path,
            "chunk_index": i,
            "timestamp": datetime.now().isoformat(),
            "total_chunks": len(chunks)
        } for i in range(len(chunks))]
        
        # Armazena no Pinecone
        await pinecone_manager.upsert_documents(
            embedding_generator=embedding_generator,
            texts=chunks,
            metadata=metadata
        )
        
        logger.info(f"Documento processado e armazenado com sucesso: {file_path}")
        
    except Exception as e:
        logger.error(f"Erro ao processar e armazenar documento: {str(e)}")
        raise

async def search_documents(
    query: str,
    embedding_generator: EmbeddingGenerator,
    pinecone_manager: PineconeManager
):
    """Realiza busca nos documentos"""
    try:
        results = await pinecone_manager.search(
            embedding_generator=embedding_generator,
            query=query,
            top_k=5
        )
        
        logger.info(f"Busca realizada com sucesso: '{query}'")
        return results
        
    except Exception as e:
        logger.error(f"Erro ao realizar busca: {str(e)}")
        raise

async def main():
    # Inicializa componentes
    embedding_generator = EmbeddingGenerator()
    pinecone_manager = PineconeManager(index_name="rag-documents")
    
    # Exemplo: processa um documento
    docs_dir = Path("documents")
    if docs_dir.exists():
        for file_path in docs_dir.glob("*.*"):
            if file_path.suffix.lower() in {".pdf", ".docx"}:
                await process_and_store_document(
                    str(file_path),
                    embedding_generator,
                    pinecone_manager
                )
    
    # Exemplo: realiza uma busca
    query = "Qual é o principal tema dos documentos?"
    results = await search_documents(
        query,
        embedding_generator,
        pinecone_manager
    )
    
    # Exibe resultados
    print("\nResultados da busca:")
    for result in results:
        print(f"\nScore: {result['score']:.4f}")
        print(f"Fonte: {result['metadata']['source']}")
        print(f"Chunk: {result['metadata']['chunk_index'] + 1} de {result['metadata']['total_chunks']}")

if __name__ == "__main__":
    asyncio.run(main()) 