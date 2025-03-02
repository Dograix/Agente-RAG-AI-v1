import os
import json
from datetime import datetime
from app.document_processing.file_tracker import FileTracker
from app.core.logging import logger

def main():
    """Lista todos os arquivos já processados"""
    try:
        # Inicializa o rastreador de arquivos
        file_tracker = FileTracker()
        
        # Verifica se há arquivos processados
        if not file_tracker.processed_files:
            print("\nNenhum arquivo foi processado ainda.")
            return
        
        # Exibe os arquivos processados
        print("\n📋 Arquivos Processados:")
        print("-" * 120)
        print(f"{'ID':<36} {'Arquivo':<40} {'Data de Processamento':<25} {'Chunks':<10}")
        print("-" * 120)
        
        for file_path, info in file_tracker.processed_files.items():
            # Obtém o ID do documento
            doc_id = info.get("doc_id", "N/A")
            
            # Formata a data
            processed_at = info.get("processed_at", "N/A")
            try:
                dt = datetime.fromisoformat(processed_at)
                processed_at = dt.strftime("%d/%m/%Y %H:%M:%S")
            except:
                pass
                
            # Obtém o número de chunks
            chunks = info.get("metadata", {}).get("chunks", "N/A")
            
            # Exibe as informações
            print(f"{doc_id:<36} {os.path.basename(file_path):<40} {processed_at:<25} {chunks:<10}")
        
        print("-" * 120)
        print(f"Total: {len(file_tracker.processed_files)} arquivos processados")
        print("\nPara remover um documento específico, use o comando:")
        print("python remove_document.py ID_DO_DOCUMENTO")
        print("\nPara remover um documento sem apagar o arquivo físico:")
        print("python remove_document.py ID_DO_DOCUMENTO --keep-file")
        
    except Exception as e:
        logger.error(f"Erro ao listar arquivos processados: {str(e)}")
        print(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main() 