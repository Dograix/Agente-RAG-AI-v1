@echo off
echo Iniciando setup do projeto...
echo.

:: Cria ambiente virtual
echo Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo Erro ao criar ambiente virtual
    pause
    exit /b 1
)

:: Ativa ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Erro ao ativar ambiente virtual
    pause
    exit /b 1
)

:: Atualiza pip
echo Atualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Erro ao atualizar pip
    pause
    exit /b 1
)

:: Instala dependências uma por uma
echo Instalando dependências principais...

echo Instalando Pydantic primeiro...
pip install "pydantic>=2.0.0"

echo Instalando OpenAI e seus componentes...
pip install "openai>=1.0.0" "langchain-openai>=0.0.5"

echo Instalando FastAPI...
pip install "fastapi>=0.68.0"

echo Instalando Uvicorn...
pip install "uvicorn>=0.15.0"

echo Instalando Loguru...
pip install "loguru>=0.5.3"

echo Instalando LangChain e seus componentes...
pip install "langchain>=0.1.0" "langchain-core>=0.1.0" "langchain-community>=0.0.10"

echo Instalando PyPDF2...
pip install "pypdf2>=2.0.0"

echo Instalando python-docx...
pip install "python-docx>=0.8.11"

echo Instalando Watchdog...
pip install "watchdog>=2.1.0"

echo Instalando Pinecone...
pip install "pinecone>=0.1.0"

echo Instalando SQLAlchemy...
pip install "sqlalchemy>=2.0.0"

echo Instalando psycopg2-binary...
pip install "psycopg2-binary>=2.9.1"

echo Instalando python-multipart...
pip install "python-multipart>=0.0.5"

echo Instalando python-dotenv...
pip install "python-dotenv>=0.19.0"

echo.
echo Instalação concluída!
echo Para ativar o ambiente virtual novamente, use: venv\Scripts\activate.bat
pause 