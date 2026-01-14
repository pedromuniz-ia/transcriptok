# PRD - TranscripTok (Open Source)

## 1. Visão Geral

**Nome:** TranscripTok
**Descrição:** Plataforma open-source para transcrição automática, download e análise de vídeos curtos (TikTok, Instagram Reels, YouTube Shorts) com ferramentas de IA.

**Objetivo:** Criar uma base sólida, escalável, pronta para evolução futura para SaaS com mínimo refatoramento.

---

## 2. Stack Tecnológico

### Backend (Python)
| Tecnologia | Propósito | Justificativa |
|------------|-----------|---------------|
| **FastAPI** | Framework web | Async nativo, tipagem, docs automática, alta performance |
| **yt-dlp** | Download de vídeos | Suporte a TikTok, Instagram, YouTube. Mantido ativamente |
| **Whisper** | Transcrição | Híbrido: local (dev) / API OpenAI (prod) |
| **Agno** | Framework agêntico | Multi-modal, memory, tools. Mais moderno que LangChain |
| **PostgreSQL** | Banco de dados | Robusto, JSON support, pronto para SaaS |
| **FFmpeg** | Processamento de mídia | Extração de áudio, conversão de formatos |
| **Celery + Redis** | Filas de tarefas | Jobs assíncronos para transcrição/download |
| **Pydantic** | Validação | Schemas robustos, integrado com FastAPI |

### Frontend (Next.js)
| Tecnologia | Propósito | Justificativa |
|------------|-----------|---------------|
| **Next.js 16+** | Framework React | App Router, Server Actions, deploy fácil Vercel |
| **TypeScript** | Tipagem | Segurança, DX, manutenibilidade |
| **Tailwind CSS** | Estilização | Rápido, consistente, baixo bundle |
| **shadcn/ui** | Componentes | Acessíveis, customizáveis, sem lock-in |
| **TanStack Query** | State/Cache | Gerenciamento de estado servidor |
| **Zustand** | Estado local | Simples, leve, sem boilerplate |

### Infra & DevOps
| Tecnologia | Propósito |
|------------|-----------|
| **Vercel** | Deploy frontend |
| **Railway/Render** | Deploy backend + PostgreSQL + Redis |
| **GitHub Actions** | CI/CD |
| **Docker** | Containerização (prod) |

---

## 3. Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Vercel)                       │
│                         Next.js + React                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │  Home    │  │ Download │  │Transcript│  │  AI Tools    │    │
│  │  Page    │  │  Page    │  │  Page    │  │    Page      │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘    │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS/REST
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Railway/Render)                    │
│                           FastAPI                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     API Gateway                          │    │
│  │  • Rate Limiting (por IP)                               │    │
│  │  • Request Validation                                    │    │
│  │  • CORS                                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────┐   │
│  │  Video    │  │Transcript │  │    AI     │  │   Export   │   │
│  │  Service  │  │  Service  │  │  Service  │  │   Service  │   │
│  │  (yt-dlp) │  │ (Whisper) │  │  (Agno)   │  │  (formats) │   │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬──────┘   │
│        │              │              │              │            │
│        └──────────────┴──────────────┴──────────────┘            │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │   Celery Worker   │                        │
│                    │  (Background Jobs)│                        │
│                    └─────────┬─────────┘                        │
└──────────────────────────────┼──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    ┌─────▼─────┐       ┌──────▼─────┐      ┌──────▼──────┐
    │ PostgreSQL│       │   Redis    │      │ File Storage│
    │ (metadata)│       │  (queue)   │      │  (S3/local) │
    └───────────┘       └────────────┘      └─────────────┘
```

---

## 4. Features do MVP

### 4.1 Download de Vídeos
**Endpoint:** `POST /api/v1/videos/download`

```python
# Request
{
  "url": "https://tiktok.com/@user/video/123",
  "quality": "best",  # best | 720p | 480p
  "remove_watermark": true
}

# Response
{
  "job_id": "uuid",
  "status": "processing",
  "estimated_time": 15
}
```

**Funcionalidades:**
- Suporte: TikTok, Instagram Reels, YouTube Shorts
- Download HD sem marca d'água (quando possível)
- Extração de metadados (título, autor, likes, etc.)
- Extração de thumbnail


### 4.2 Transcrição Automática
**Endpoint:** `POST /api/v1/transcripts/create`

```python
# Request
{
  "video_url": "https://tiktok.com/...",
  # OU
  "job_id": "uuid-do-download"
}

# Response
{
  "job_id": "uuid",
  "status": "processing"
}

# GET /api/v1/transcripts/{job_id}
{
  "status": "completed",
  "transcript": {
    "text": "Full transcript here...",
    "segments": [
      {"start": 0.0, "end": 2.5, "text": "Hey guys..."},
      {"start": 2.5, "end": 5.0, "text": "Today we're going to..."}
    ],
    "language": "pt",
    "confidence": 0.94
  }
}
```

**Funcionalidades:**
- Transcrição com timestamps (word-level opcional)
- Detecção automática de idioma
- Suporte a 99+ idiomas
- Exportação: TXT, JSON, SRT, VTT
- Híbrido: Whisper local (dev) / API OpenAI (prod)

### 4.3 Ferramentas de IA
**Endpoint:** `POST /api/v1/ai/tools`

```python
# Request - Hook Generator
{
  "tool": "hook_generator",
  "input": {
    "transcript": "Full transcript or topic",
    "style": "curiosity",  # curiosity | shock | question | story
    "count": 5
  }
}

# Response
{
  "hooks": [
    "Você não vai acreditar no que aconteceu quando...",
    "3 segundos mudaram tudo para...",
    ...
  ]
}

# Request - Script Rewriter
{
  "tool": "script_rewriter",
  "input": {
    "original_script": "...",
    "goal": "more_viral",  # more_viral | shorter | clearer
    "tone": "casual"
  }
}
```

**Ferramentas IA (MVP):**
1. **Hook Generator** - Gera ganchos virais para vídeos
2. **Script Rewriter** - Reescreve scripts para maior engajamento
3. **Content Analyzer** - Analisa padrões de viralidade

**Providers LLM (via Agno):**
- OpenAI GPT-4o-mini (default, barato)
- Claude 3.5 Sonnet (opcional)
- Llama 3 via Groq (fallback gratuito)

---

## 5. Referência de UI/UX (TokScript)

Baseado no produto de referência TokScript, a interface deve seguir estes padrões:

### 5.1 Layout Geral
- **Tema:** Dark mode com tons de azul escuro/ciano
- **Header fixo:** Logo, navegação (Home, Support, Install Chrome Extension), botão "Upgrade My Plan", avatar do usuário
- **Gradiente:** Background com gradiente sutil roxo/azul na área do hero

### 5.2 Área Principal (Hero)
- **Título:** "Paste your video link here"
- **Subtítulo:** "Paste your TikTok, YouTube Shorts, or Instagram Reels link to get started."
- **Input:** Campo de texto grande com placeholder, botão "Download" com ícone de loading

### 5.3 Resultado do Processamento
Layout em duas colunas após processar:

**Coluna Esquerda - Vídeo:**
- Thumbnail do vídeo (imagem de capa)
- Botões: "Save cover image", "Download video"

**Coluna Direita - Transcrição:**
- Header "TokScript AI" com botões de ação:
  - "Write hooks" (gerar ganchos)
  - "Rewrite scripts" (reescrever roteiro)
  - "Get framework" (obter estrutura)
- Toggle "Show timestamp" para mostrar/ocultar timestamps
- Ícones: Copiar e Download
- Área de texto com a transcrição completa

### 5.4 Histórico de Transcrições
Seção abaixo do resultado principal:

**Header:**
- Título: "Transcript History"
- Subtítulo: "Global archive of all processed videos and collections"
- Botão "Export All"

**Cards de Estatísticas:**
| Métrica | Descrição |
|---------|-----------|
| Total Transcripts | Número total de transcrições |
| Successfully Processed | Tempo total processado (ex: "0.02h") |
| Currently Processing | Jobs em andamento |
| Failed/Errors | Transcrições com erro |

**Filtros e Busca:**
- Campo de busca "Search transcripts..."
- Dropdowns: All Folders, Status: All, Source: All, Platform: All
- Toggle: "Bookmarked Only"

**Tabela de Resultados:**
| Coluna | Conteúdo |
|--------|----------|
| Content | Thumbnail + título + @autor + views |
| Source | "Web" ou "Extension" |
| Folder | Pasta de organização |
| Platform | Ícone da plataforma (TikTok, YouTube, etc.) |
| Date | Data e hora do processamento |
| Duration | Duração do vídeo (ex: "61s") |
| Status | Badge "Complete" / "Processing" / "Failed" |
| Actions | Ícones: Preview, Mover para pasta, Menu (...) |

### 5.5 Footer
- Logo + descrição do produto
- Links sociais: Twitter, Facebook, LinkedIn, Instagram
- **Product:** Features, Pricing, API, Integrations
- **Company:** About, Contact, Privacy, Terms, Help center
- Copyright

### 5.6 Componentes UI Específicos
- **Badges de status:** Verde para "Complete", amarelo para "Processing", vermelho para "Failed"
- **Botões primários:** Fundo sólido cyan/teal com texto escuro
- **Botões secundários:** Borda com fundo transparente
- **Cards:** Borda sutil, fundo semi-transparente
- **Ícones de plataforma:** TikTok, YouTube, Instagram com cores próprias

---

## 6. Estrutura de Diretórios

### Backend
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # Settings (pydantic-settings)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencies (rate limit, etc)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Main router
│   │       ├── videos.py       # Download endpoints
│   │       ├── transcripts.py  # Transcription endpoints
│   │       └── ai_tools.py     # AI tools endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── video_downloader.py # yt-dlp wrapper
│   │   ├── transcriber.py      # Whisper wrapper (local + API)
│   │   ├── ai_agent.py         # Agno agent setup
│   │   └── exporter.py         # Export formats
│   ├── models/
│   │   ├── __init__.py
│   │   ├── video.py            # SQLAlchemy models
│   │   ├── transcript.py
│   │   └── job.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── video.py            # Pydantic schemas
│   │   ├── transcript.py
│   │   └── ai_tools.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py         # DB connection
│   │   ├── redis.py            # Redis connection
│   │   └── celery.py           # Celery config
│   └── workers/
│       ├── __init__.py
│       ├── download_task.py    # Celery task
│       └── transcribe_task.py
├── tests/
│   ├── conftest.py
│   ├── test_videos.py
│   └── test_transcripts.py
├── alembic/                    # DB migrations
├── Dockerfile
├── pyproject.toml              # Poetry/UV
├── .env.example
└── README.md
```

### Frontend
```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx            # Home
│   │   ├── download/
│   │   │   └── page.tsx
│   │   ├── transcript/
│   │   │   └── page.tsx
│   │   └── ai-tools/
│   │       └── page.tsx
│   ├── components/
│   │   ├── ui/                 # shadcn components
│   │   ├── video-input.tsx
│   │   ├── transcript-viewer.tsx
│   │   ├── download-card.tsx
│   │   └── ai-tool-form.tsx
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   ├── utils.ts
│   │   └── constants.ts
│   ├── hooks/
│   │   ├── use-download.ts
│   │   └── use-transcript.ts
│   └── types/
│       └── index.ts
├── public/
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.example
```

---

## 6. Database Schema

```sql
-- Jobs (genérico para download/transcription)
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,  -- 'download' | 'transcription' | 'ai_tool'
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending | processing | completed | failed
    input_data JSONB NOT NULL,
    output_data JSONB,
    error_message TEXT,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Videos (metadata cache)
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(20) NOT NULL,  -- tiktok | instagram | youtube
    original_url TEXT NOT NULL UNIQUE,
    video_id VARCHAR(100),
    title TEXT,
    author VARCHAR(255),
    duration INTEGER,  -- seconds
    thumbnail_url TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Transcripts
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id),
    job_id UUID REFERENCES jobs(id),
    full_text TEXT NOT NULL,
    segments JSONB,  -- [{start, end, text}]
    language VARCHAR(10),
    confidence FLOAT,
    word_timestamps JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Rate limiting (simples)
CREATE TABLE rate_limits (
    ip_address INET PRIMARY KEY,
    download_count INTEGER DEFAULT 0,
    transcript_count INTEGER DEFAULT 0,
    ai_tool_count INTEGER DEFAULT 0,
    window_start TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_ip ON jobs(ip_address);
CREATE INDEX idx_videos_platform ON videos(platform);
CREATE INDEX idx_transcripts_video ON transcripts(video_id);
```

---

## 7. CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # Backend Tests
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install
      - name: Run tests
        run: |
          cd backend
          poetry run pytest --cov

  # Frontend Tests
  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install & Test
        run: |
          cd frontend
          npm ci
          npm run lint
          npm run build

  # Deploy (on main)
  deploy-frontend:
    needs: [backend-test, frontend-test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
```

---

## 8. Configuração de Ambiente

### Backend (.env)
```env
# App
APP_ENV=development  # development | production
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/transcriptok

# Redis
REDIS_URL=redis://localhost:6379/0

# Whisper
WHISPER_MODE=local  # local | api
OPENAI_API_KEY=sk-...  # para modo api

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...

# Rate Limits
RATE_LIMIT_DOWNLOADS=5  # per hour
RATE_LIMIT_TRANSCRIPTS=10
RATE_LIMIT_AI_TOOLS=20

# Storage
STORAGE_TYPE=local  # local | s3
STORAGE_PATH=./storage
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=TranscripTok
```

---

## 9. Roadmap de Implementação

### Fase 1 - Setup (Dia 1-2)
- [ ] Criar repositório monorepo
- [ ] Setup backend FastAPI + estrutura
- [ ] Setup frontend Next.js + shadcn
- [ ] Configurar CI/CD básico
- [ ] Deploy inicial (health check)

### Fase 2 - Download (Dia 3-4)
- [ ] Integrar yt-dlp
- [ ] Endpoint de download
- [ ] Background jobs com Celery
- [ ] UI de input de URL
- [ ] Testes básicos

### Fase 3 - Transcrição (Dia 5-6)
- [ ] Integrar Whisper (local + API)
- [ ] Endpoint de transcrição
- [ ] Viewer de transcrição com timestamps
- [ ] Export formats (TXT, SRT, JSON)

### Fase 4 - AI Tools (Dia 7-8)
- [ ] Setup Agno com multi-provider
- [ ] Hook Generator
- [ ] Script Rewriter
- [ ] UI para ferramentas IA

### Fase 5 - Polish (Dia 9-10)
- [ ] Rate limiting robusto
- [ ] Error handling completo
- [ ] Loading states / UX
- [ ] Documentação API
- [ ] README completo

---

## 10. Considerações para Futuro SaaS

A arquitetura foi pensada para facilitar evolução:

| Aspecto | MVP Atual | Futuro SaaS |
|---------|-----------|-------------|
| Auth | Rate limit por IP | JWT + tiers de usuário |
| Storage | Local/S3 | S3 com presigned URLs |
| DB | Single PostgreSQL | Read replicas + connection pooling |
| Queue | Redis/Celery | AWS SQS ou Redis Cluster |
| Payments | N/A | Stripe integration |
| Analytics | N/A | PostHog/Mixpanel |

**Pontos de extensão já preparados:**
- Schemas Pydantic separados (fácil adicionar campos user_id)
- Rate limiting por IP (trocar para por user_id)
- Jobs table com ip_address (adicionar user_id)
- Service layer desacoplado (injeção de dependências)

---

## 11. Verificação / Testes

Para validar que tudo funciona:

### Backend
```bash
# Rodar testes
cd backend && poetry run pytest

# Testar manualmente
curl -X POST http://localhost:8000/api/v1/videos/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@user/video/123"}'
```

### Frontend
```bash
# Build de produção
cd frontend && npm run build

# Rodar localmente
npm run dev
```

### E2E
1. Colar URL de TikTok no input
2. Verificar download inicia
3. Verificar transcrição gerada
4. Testar gerador de hooks
5. Exportar em diferentes formatos
