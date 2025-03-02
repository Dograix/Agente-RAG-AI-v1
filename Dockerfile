FROM python:3.13.2-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código
COPY . .

# Porta para a API
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.api.endpoints:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 