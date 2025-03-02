from app.chat.database import init_db, get_db
from app.core.logging import logger

def test_db_connection():
    """Testa a conexão com o PostgreSQL"""
    try:
        # Inicializa o banco de dados (cria tabelas)
        init_db()
        
        # Tenta obter uma conexão usando o generator
        db = None
        for session in get_db():
            db = session
            break
        
        if db is None:
            raise Exception("Não foi possível obter uma sessão do banco de dados")
            
        logger.info(
            "Conexão com PostgreSQL testada com sucesso!",
            extra={"database": db.get_bind().url.database}
        )
        
        db.close()
        return True
            
    except Exception as e:
        logger.error(f"Erro ao testar conexão com PostgreSQL: {str(e)}")
        return False

if __name__ == "__main__":
    test_db_connection() 