# RAG Agent Frontend

Interface web para o Agente RAG, construída com React, Material-UI e TypeScript.

## Requisitos

- Node.js 18.x ou superior
- npm 9.x ou superior

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositório>
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

## Configuração

1. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```bash
REACT_APP_API_URL=http://localhost:8000
```

## Desenvolvimento

Para iniciar o servidor de desenvolvimento:

```bash
npm start
```

O aplicativo estará disponível em [http://localhost:3000](http://localhost:3000).

## Build

Para criar uma build de produção:

```bash
npm run build
```

Os arquivos serão gerados na pasta `build`.

## Estrutura do Projeto

```
src/
  ├── components/     # Componentes React reutilizáveis
  ├── hooks/         # Custom hooks
  ├── services/      # Serviços de API e utilitários
  ├── theme/         # Configuração do tema Material-UI
  ├── types/         # Definições de tipos TypeScript
  ├── App.tsx        # Componente principal
  └── index.tsx      # Ponto de entrada
```

## Funcionalidades

- Chat em tempo real com o agente RAG
- Upload e gerenciamento de documentos
- Visualização de estatísticas e análises
- Interface responsiva e moderna
- Tema personalizável
- Integração com FastAPI backend

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes. 