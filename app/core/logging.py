import sys
import json
from loguru import logger
from .config import settings
import os
from datetime import datetime
from typing import Dict, Any, Optional

class JsonFormatter:
    def __call__(self, record):
        # Formata a data/hora como string ISO
        time_str = record["time"].isoformat()
        
        # Cria o dicionário base
        log_data = {
            "time": time_str,
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"]
        }
        
        # Adiciona dados extras se existirem
        if record["extra"]:
            # Trata objetos não serializáveis
            safe_extra = {}
            for key, value in record["extra"].items():
                try:
                    # Tenta converter para string se não for serializável
                    json.dumps({key: value})
                    safe_extra[key] = value
                except (TypeError, OverflowError):
                    safe_extra[key] = str(value)
            
            log_data["extra"] = safe_extra
            
        # Adiciona exceção se existir
        if record["exception"] is not None:
            log_data["exception"] = str(record["exception"])
            
        return json.dumps(log_data)

def setup_logging():
    # Remove o handler padrão
    logger.remove()
    
    # Cria a estrutura de diretórios para logs
    log_base_dir = settings.LOG_DIR
    log_app_dir = os.path.join(log_base_dir, "app")
    log_error_dir = os.path.join(log_base_dir, "errors")
    log_debug_dir = os.path.join(log_base_dir, "debug")
    
    os.makedirs(log_base_dir, exist_ok=True)
    os.makedirs(log_app_dir, exist_ok=True)
    os.makedirs(log_error_dir, exist_ok=True)
    os.makedirs(log_debug_dir, exist_ok=True)
    
    # Data atual para os nomes dos arquivos
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Adiciona o handler para console com formato simples (apenas para desenvolvimento)
    if settings.LOG_TO_CONSOLE:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.LOG_LEVEL,
            filter=lambda record: record["level"].name not in ["ERROR", "CRITICAL"] or settings.DEBUG_MODE
        )
    
    # Log de aplicação (INFO e acima) - formato JSON para análise
    logger.add(
        os.path.join(log_app_dir, f"app_{current_date}.log"),
        format="{message}",
        rotation="10 MB",
        retention="30 days",
        level="INFO",
        serialize=False,
        filter=lambda record: record["level"].name in ["INFO", "SUCCESS", "WARNING"],
        enqueue=True
    )
    
    # Log de erros (ERROR e CRITICAL) - formato detalhado com traceback
    logger.add(
        os.path.join(log_error_dir, f"error_{current_date}.log"),
        format="<red>{time:YYYY-MM-DD HH:mm:ss.SSS}</red> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>\n{exception}",
        rotation="10 MB",
        retention="60 days",
        level="ERROR",
        backtrace=True,
        diagnose=True,
        enqueue=True
    )
    
    # Log de debug (todos os níveis) - apenas se DEBUG_MODE estiver ativado
    if settings.DEBUG_MODE:
        logger.add(
            os.path.join(log_debug_dir, f"debug_{current_date}.log"),
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            rotation="20 MB",
            retention="7 days",
            level="TRACE",
            enqueue=True
        )
    
    # Log completo em JSON para análise de dados
    logger.add(
        os.path.join(log_base_dir, f"rag_app_{current_date}.json"),
        format="{message}",
        rotation="50 MB",
        retention="30 days",
        level=settings.LOG_LEVEL,
        serialize=False,
        filter=lambda record: record["message"] == JsonFormatter()(record),
        enqueue=True
    )
    
    return logger

# Funções auxiliares para logging contextual
def log_with_context(level: str, message: str, context: Dict[str, Any] = None, exception: Optional[Exception] = None):
    """
    Registra uma mensagem com contexto adicional.
    
    Args:
        level: Nível do log (debug, info, warning, error, critical)
        message: Mensagem a ser registrada
        context: Dicionário com informações de contexto
        exception: Exceção a ser registrada (para níveis error e critical)
    """
    log_func = getattr(logger, level.lower())
    
    if context:
        with logger.contextualize(**context):
            if exception and level.lower() in ["error", "critical"]:
                log_func(message, exc_info=exception)
            else:
                log_func(message)
    else:
        if exception and level.lower() in ["error", "critical"]:
            log_func(message, exc_info=exception)
        else:
            log_func(message)

# Configuração inicial do logger
logger = setup_logging()