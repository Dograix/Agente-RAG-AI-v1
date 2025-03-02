import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import hashlib
from ..core.logging import logger

class FileTracker:
    def __init__(self):
        self.documents_dir = Path("documents")
        self.metadata_file = self.documents_dir / "metadata.json"
        self._ensure_directories()
        self._load_metadata()

    def _ensure_directories(self):
        """Garante que os diretórios necessários existam"""
        self.documents_dir.mkdir(exist_ok=True)
        if not self.metadata_file.exists():
            self._save_metadata({})

    def _load_metadata(self) -> Dict:
        """Carrega os metadados dos documentos"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar metadados: {str(e)}")
            return {}

    def _save_metadata(self, metadata: Dict):
        """Salva os metadados dos documentos"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Erro ao salvar metadados: {str(e)}")

    def _generate_file_id(self, filename: str, content: bytes) -> str:
        """Gera um ID único para o arquivo"""
        hash_object = hashlib.sha256(content)
        hash_object.update(filename.encode())
        return hash_object.hexdigest()[:12]

    def track_document(self, filename: str, file_path: Path, size_bytes: int) -> str:
        """Registra um novo documento no sistema"""
        metadata = self._load_metadata()
        
        with open(file_path, 'rb') as f:
            content = f.read()
            file_id = self._generate_file_id(filename, content)

        metadata[file_id] = {
            "filename": filename,
            "file_type": file_path.suffix[1:],
            "upload_date": datetime.now().isoformat(),
            "status": "uploaded",
            "size_bytes": size_bytes,
            "processed": False,
            "embedding_count": None,
            "error_message": None
        }

        self._save_metadata(metadata)
        return file_id

    def update_document_status(
        self,
        file_id: str,
        status: str,
        processed: bool = False,
        embedding_count: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """Atualiza o status de processamento de um documento"""
        metadata = self._load_metadata()
        
        if file_id not in metadata:
            raise ValueError(f"Documento não encontrado: {file_id}")

        metadata[file_id].update({
            "status": status,
            "processed": processed,
            "embedding_count": embedding_count,
            "error_message": error_message
        })

        self._save_metadata(metadata)

    def get_document(self, file_id: str) -> Dict:
        """Obtém informações de um documento específico"""
        metadata = self._load_metadata()
        return metadata.get(file_id)

    def get_all_documents(self) -> List[Dict]:
        """Lista todos os documentos registrados"""
        metadata = self._load_metadata()
        return [
            {"id": file_id, **doc_data}
            for file_id, doc_data in metadata.items()
        ]

    def remove_document(self, file_id: str) -> bool:
        """Remove um documento do sistema"""
        metadata = self._load_metadata()
        
        if file_id not in metadata:
            return False

        # Remove o arquivo físico se existir
        filename = metadata[file_id]["filename"]
        file_path = self.documents_dir / filename
        if file_path.exists():
            file_path.unlink()

        # Remove dos metadados
        del metadata[file_id]
        self._save_metadata(metadata)
        return True

    def get_processing_status(self, file_id: str) -> str:
        """Obtém o status de processamento de um documento"""
        metadata = self._load_metadata()
        if file_id in metadata:
            return metadata[file_id]["status"]
        return "not_found" 