# Sistema Gestor de Documentos RAG

Um sistema completo para gerenciamento de documentos com Retrieval Augmented Generation (RAG), permitindo processamento inteligente de documentos, busca contextual e chat com IA.

## Funcionalidades

- **Processamento de Documentos**: Upload, processamento e gerenciamento de documentos.
- **Chat RAG Inteligente**: Interação com documentos através de chat com IA usando GPT-4o-mini.
- **Avaliação de Relevância**: Sistema inteligente que avalia a relevância do contexto para cada pergunta.
- **Interface Web**: Interface amigável para todas as funcionalidades do sistema.
- **Analytics**: Visualização de estatísticas e métricas de uso do sistema.

## Componentes do Sistema

- **Vector Store**: Armazenamento de embeddings usando Pinecone.
- **Processamento de Documentos**: Extração de texto, chunking e geração de embeddings.
- **Chat Manager**: Gerenciamento de conversas e interação com o modelo de linguagem.
- **Interface Web**: Interface Streamlit para interação com o sistema.

## Requisitos

- Python 3.8+
- OpenAI API Key
- Pinecone API Key
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/sistema-rag.git
cd sistema-rag
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```
OPENAI_API_KEY=sua_chave_api_openai
PINECONE_API_KEY=sua_chave_api_pinecone
PINECONE_ENVIRONMENT=seu_ambiente_pinecone
```

## Uso

### Interface Web

Para iniciar a interface web:

```
python run_web.py
```

Acesse a interface em: http://localhost:8501

### Processamento de Documentos

Para processar documentos existentes:

```
python process_existing.py
```

### Chat via Terminal

Para iniciar o chat via terminal:

```
python chat.py
```

## Estrutura do Projeto

```
.
├── app/
│   ├── api/              # API REST
│   ├── chat/             # Lógica de chat e interação com LLM
│   ├── core/             # Configurações e utilitários
│   ├── database/         # Armazenamento de conversas
│   ├── document_processing/ # Processamento de documentos
│   ├── vector_store/     # Gerenciamento de embeddings
│   └── web/              # Interface web
├── data/
│   ├── conversations/    # Armazenamento de conversas
│   └── db/               # Banco de dados SQLite
├── documents/            # Documentos para processamento
├── logs/                 # Logs do sistema
├── chat.py               # Script para chat via terminal
├── process_existing.py   # Script para processar documentos existentes
├── run_web.py            # Script para iniciar a interface web
└── README.md             # Este arquivo
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes. 