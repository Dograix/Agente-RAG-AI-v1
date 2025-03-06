# RAG App

Aplicação de Recuperação Aumentada por Geração (RAG) que permite carregar documentos e fazer perguntas sobre eles usando IA.

## Funcionalidades

- Gerenciamento de conversas
- Upload e processamento de documentos
- Análise de dados e métricas
- Interface moderna e responsiva

## Tecnologias

- React 19
- TypeScript
- Vite
- React Query
- Axios
- Vitest
- React Testing Library

## Pré-requisitos

- Node.js 18+
- npm 9+

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/rag-app.git
cd rag-app
```

2. Instale as dependências:
```bash
npm install
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```
Edite o arquivo `.env` com suas configurações.

## Desenvolvimento

Para iniciar o servidor de desenvolvimento:

```bash
npm run dev
```

## Testes

Para rodar os testes:

```bash
npm test
```

Para ver a cobertura de testes:

```bash
npm run test:coverage
```

## Build

Para gerar o build de produção:

```bash
npm run build
```

## Estrutura do Projeto

```
src/
  ├── components/    # Componentes React
  ├── hooks/         # Custom hooks
  ├── services/      # Serviços e APIs
  ├── config/        # Configurações
  ├── types/         # Tipos TypeScript
  └── utils/         # Utilitários
tests/
  ├── components/    # Testes de componentes
  ├── hooks/         # Testes de hooks
  └── setup.ts       # Configuração dos testes
```

## Contribuindo

1. Faça o fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes. 