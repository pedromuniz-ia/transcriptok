# TranscripTok

Plataforma open-source para transcricao automatica, download e analise com IA de videos curtos (TikTok, Instagram Reels, YouTube Shorts).

## Funcionalidades

- **Transcricao automatica** - Transcreve audio de videos usando Whisper (local ou API)
- **Download de videos** - Baixa videos de TikTok, Instagram Reels e YouTube Shorts via yt-dlp
- **Ferramentas de IA** - Gera ganchos, reescreve roteiros e analisa conteudo com LLMs
- **Export de transcricoes** - Exporta em TXT, SRT, VTT e JSON
- **Historico completo** - Listagem paginada com busca e filtros por plataforma/status
- **Interface moderna** - UI responsiva com tema escuro

## Tech Stack

| Camada | Tecnologias |
|--------|-------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Celery + Redis, yt-dlp, Whisper, Agno |
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS, TanStack Query, Zustand |
| **Banco de dados** | PostgreSQL 15 |
| **Fila** | Redis 7 |

## Quick Start (Docker)

```bash
# Clonar o repositorio
git clone https://github.com/pedromuniz-ia/transcriptok.git
cd transcriptok

# Subir todos os servicos
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:3000 (rodar separadamente, veja abaixo)
```

## Desenvolvimento Local

### Backend

```bash
cd backend
cp .env.example .env              # Configurar variaveis de ambiente
pip install -e ".[dev]"           # Instalar dependencias
alembic upgrade head              # Rodar migracoes
uvicorn app.main:app --reload     # Servidor dev (porta 8000)
```

Em outro terminal, iniciar o worker Celery:

```bash
cd backend
celery -A app.core.celery worker --loglevel=info
```

### Frontend

```bash
cd frontend
cp .env.example .env.local        # Configurar variaveis de ambiente
npm install                       # Instalar dependencias
npm run dev                       # Servidor dev (porta 3000)
```

## Estrutura do Projeto

```
transcriptok/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # Endpoints (videos, transcripts, ai_tools)
│   │   ├── core/                # Config, database, celery
│   │   ├── models/              # SQLAlchemy models (Job, Video, Transcript)
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Logica de negocio (downloader, transcriber, AI)
│   │   └── workers/             # Celery tasks
│   ├── alembic/                 # Migracoes de banco
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   ├── components/          # Componentes React
│   │   ├── hooks/               # Custom hooks
│   │   └── lib/                 # API client, utils
│   └── Dockerfile
├── docker-compose.yml           # Dev (inclui PostgreSQL e Redis)
└── docker-compose.prod.yml      # Producao (usa infra existente)
```

## Variaveis de Ambiente

### Backend (`backend/.env`)

| Variavel | Descricao | Default |
|----------|-----------|---------|
| `DATABASE_URL` | URL de conexao PostgreSQL | `postgresql+asyncpg://postgres:postgres@localhost:5432/transcriptok` |
| `REDIS_URL` | URL de conexao Redis | `redis://localhost:6379/0` |
| `WHISPER_MODE` | Modo do Whisper (`local` ou `api`) | `local` |
| `OPENAI_API_KEY` | Chave da API OpenAI | - |
| `ANTHROPIC_API_KEY` | Chave da API Anthropic (opcional) | - |
| `GROQ_API_KEY` | Chave da API Groq (opcional) | - |
| `STORAGE_PATH` | Diretorio de armazenamento | `./storage` |
| `CORS_ORIGINS` | Origens CORS permitidas | `["http://localhost:3000"]` |

### Frontend (`frontend/.env.local`)

| Variavel | Descricao | Default |
|----------|-----------|---------|
| `NEXT_PUBLIC_API_URL` | URL do backend | `http://localhost:8000` |

## Deploy

### Docker Compose (Producao)

```bash
# Configurar variaveis de ambiente
export DATABASE_PASSWORD=sua-senha-segura
export OPENAI_API_KEY=sk-...

# Subir com config de producao
docker-compose -f docker-compose.prod.yml up -d
```

### Frontend (Vercel)

O frontend pode ser deployado na Vercel apontando `NEXT_PUBLIC_API_URL` para o backend.

## Licenca

MIT
