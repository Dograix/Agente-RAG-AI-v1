from typing import List
import PyPDF2
from docx import Document
from pathlib import Path
from ..core.logging import logger

class DocumentExtractor:
    """Classe base para extração de documentos"""
    def extract_text(self, file_path: str) -> str:
        raise NotImplementedError

class PDFExtractor(DocumentExtractor):
    """Extrator para arquivos PDF"""
    def extract_text(self, file_path: str) -> str:
        logger.info(f"Extraindo texto do PDF: {file_path}")
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if not page_text.strip():
                        logger.warning(f"Página {i+1} do PDF está vazia ou ilegível")
                        continue
                    text += page_text + "\n"
                    logger.info(f"Página {i+1} extraída com {len(page_text)} caracteres")
                
                final_text = text.strip()
                if not final_text:
                    raise ValueError("Nenhum texto legível foi extraído do PDF")
                    
                logger.info(f"PDF processado com {len(final_text)} caracteres totais")
                return final_text
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF {file_path}: {str(e)}")
            raise

class DOCXExtractor(DocumentExtractor):
    """Extrator para arquivos DOCX"""
    def extract_text(self, file_path: str) -> str:
        logger.info(f"Extraindo texto do DOCX: {file_path}")
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Erro ao extrair texto do DOCX {file_path}: {str(e)}")
            raise

class TXTExtractor(DocumentExtractor):
    """Extrator para arquivos TXT"""
    def extract_text(self, file_path: str) -> str:
        logger.info(f"Extraindo texto do TXT: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Erro ao extrair texto do TXT {file_path}: {str(e)}")
            raise

class DocumentProcessor:
    """Classe principal para processamento de documentos"""
    def __init__(self):
        self.extractors = {
            '.pdf': PDFExtractor(),
            '.docx': DOCXExtractor(),
            '.txt': TXTExtractor()
        }
    
    def process_document(self, file_path: str) -> str:
        """Processa um documento e retorna seu texto"""
        path = Path(file_path)
        extractor = self.extractors.get(path.suffix.lower())
        
        if not extractor:
            supported = ", ".join(self.extractors.keys())
            raise ValueError(
                f"Formato de arquivo não suportado: {path.suffix}. "
                f"Formatos suportados: {supported}"
            )
        
        logger.info(f"Iniciando processamento do documento: {file_path}")
        try:
            text = extractor.extract_text(file_path)
            logger.info(
                f"Documento processado com sucesso: {file_path}",
                extra={"chars_extracted": len(text)}
            )
            return text
        except Exception as e:
            logger.error(f"Erro no processamento do documento {file_path}: {str(e)}")
            raise 