import os
import json
import asyncio
import shutil
from app.vector_store.pinecone_store import PineconeManager
from app.core.config import settings
from app.core.logging import logger
from app.document_processing.file_tracker import FileTracker

async def main():
    """Limpa o índice do Pinecone e o registro de arquivos processados"""
    try:
        # Confirma com o usuário
        print("\n⚠️ ATENÇÃO: Esta operação irá apagar todos os dados do Pinecone e o registro de arquivos processados.")
        delete_files = input("Deseja também apagar os arquivos físicos da pasta documents? (s/n): ").lower() == 's'
        
        if delete_files:
            print("\n⚠️ ATENÇÃO EXTRA: Todos os arquivos na pasta 'documents' serão PERMANENTEMENTE EXCLUÍDOS!")
        
        print("\nIsso significa que todos os documentos terão que ser processados novamente.")
        confirmation = input("\nDigite 'CONFIRMAR' para prosseguir: ")
        
        if confirmation != "CONFIRMAR":
            print("Operação cancelada pelo usuário.")
            return
        
        # Limpa o índice do Pinecone
        logger.info("Iniciando limpeza do índice Pinecone")
        pinecone_manager = PineconeManager(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT,
            index_name=settings.PINECONE_INDEX_NAME
        )
        
        # Deleta todos os vetores
        pinecone_manager.delete_all()
        logger.info(f"Índice Pinecone '{settings.PINECONE_INDEX_NAME}' limpo com sucesso")
        
        # Obtém a lista de arquivos processados antes de limpar
        file_tracker = FileTracker()
        processed_files = file_tracker.get_all_documents()
        
        # Limpa o registro de arquivos processados
        tracker_file = "data/processed_files.json"
        if os.path.exists(tracker_file):
            with open(tracker_file, 'w') as f:
                json.dump({}, f)
            logger.info("Registro de arquivos processados limpo com sucesso")
        
        # Opcionalmente apaga os arquivos físicos
        if delete_files:
            documents_dir = "documents"
            if os.path.exists(documents_dir):
                # Apaga todos os arquivos na pasta
                for filename in os.listdir(documents_dir):
                    file_path = os.path.join(documents_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            logger.info(f"Arquivo removido: {file_path}")
                    except Exception as e:
                        logger.error(f"Erro ao remover arquivo {file_path}: {str(e)}")
                
                logger.info("Todos os arquivos físicos foram removidos")
                print("\n🗑️ Arquivos físicos removidos com sucesso!")
        
        print("\n✅ Operação concluída com sucesso!")
        print("Você pode agora processar novamente seus documentos.")
        
    except Exception as e:
        logger.error(f"Erro ao limpar dados: {str(e)}")
        print(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 