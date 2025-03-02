import os
import asyncio
import argparse
from app.vector_store.pinecone_store import PineconeManager
from app.core.config import settings
from app.core.logging import logger
from app.document_processing.file_tracker import FileTracker

async def remove_document(doc_id, delete_physical=False):
    """Remove um documento específico do sistema"""
    try:
        # Inicializa o rastreador de arquivos
        file_tracker = FileTracker()
        
        # Verifica se o documento existe
        file_path = file_tracker.get_file_by_id(doc_id)
        if not file_path:
            print(f"\n❌ Documento com ID {doc_id} não encontrado.")
            return False
        
        # Obtém informações do documento
        file_info = file_tracker.get_file_info(file_path)
        if not file_info:
            print(f"\n❌ Informações do documento com ID {doc_id} não encontradas.")
            return False
        
        # Inicializa o gerenciador do Pinecone
        pinecone_manager = PineconeManager(settings.PINECONE_INDEX_NAME)
        
        # Prepara o filtro para remover os vetores do documento
        filter_dict = {"source": str(file_path)}
        
        # Remove os vetores do Pinecone
        try:
            # Usa o método de deleção com filtro
            pinecone_manager.index.delete(filter=filter_dict)
            logger.info(f"Vetores do documento {doc_id} removidos do Pinecone")
        except Exception as e:
            logger.error(f"Erro ao remover vetores do Pinecone: {str(e)}")
            print(f"\n⚠️ Erro ao remover vetores do Pinecone: {str(e)}")
        
        # Remove o documento do registro
        success = file_tracker.remove_file(doc_id, delete_physical)
        
        if success:
            print(f"\n✅ Documento removido com sucesso!")
            if delete_physical:
                print(f"O arquivo físico também foi removido: {os.path.basename(file_path)}")
            return True
        else:
            print(f"\n⚠️ Documento removido do registro, mas houve problemas ao remover o arquivo físico.")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao remover documento {doc_id}: {str(e)}")
        print(f"\n❌ Erro: {str(e)}")
        return False

async def main():
    """Função principal"""
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(description="Remove um documento específico do sistema")
    parser.add_argument("doc_id", help="ID do documento a ser removido")
    parser.add_argument("--keep-file", action="store_true", help="Mantém o arquivo físico (apenas remove do índice)")
    args = parser.parse_args()
    
    # Verifica se o ID foi fornecido
    if not args.doc_id:
        print("\n❌ É necessário fornecer o ID do documento.")
        return
    
    # Confirma com o usuário
    delete_physical = not args.keep_file
    
    if delete_physical:
        print(f"\n⚠️ ATENÇÃO: O documento com ID {args.doc_id} será removido do índice e o arquivo físico será EXCLUÍDO.")
    else:
        print(f"\n⚠️ ATENÇÃO: O documento com ID {args.doc_id} será removido apenas do índice. O arquivo físico será mantido.")
    
    confirmation = input("\nDigite 'CONFIRMAR' para prosseguir: ")
    
    if confirmation != "CONFIRMAR":
        print("Operação cancelada pelo usuário.")
        return
    
    # Remove o documento
    await remove_document(args.doc_id, delete_physical)

if __name__ == "__main__":
    asyncio.run(main()) 