# Alleato Elements Workers

This repository contains the Cloudflare Workers that power the Alleato AI Elements backend infrastructure.

## Workers Overview

### 1. AI Agent Worker (`ai-agent-worker/`)
- **Purpose**: AI chatbot with RAG (Retrieval-Augmented Generation) capabilities
- **Features**: Streaming responses, OpenAI and Cloudflare AI integration
- **Endpoints**: `/api/v1/chat`

### 2. Fireflies Ingest Worker (`fireflies-ingest-worker/`)
- **Purpose**: Scheduled ingestion of meeting transcripts from Fireflies.ai
- **Schedule**: Runs every 30 minutes via cron trigger
- **Features**: API sync, database storage, queue management

### 3. Vectorize Worker (`vectorize-worker/`)
- **Purpose**: Processes transcripts to generate embeddings and insights
- **Features**: Text chunking, embedding generation, project matching
- **Queue**: Consumes from `transcript-processing` queue

### 4. Insights Worker (`insights-worker/`)
- **Status**: ⚠️ Under development
- **Purpose**: Advanced analytics and insights generation

## Development Setup

### Prerequisites
- Node.js >= 20.0.0
- Wrangler CLI (`npm install -g wrangler`)
- Cloudflare account with Workers enabled

### Local Development
```bash
# Install dependencies for all workers
npm run install:all

# Start development servers
npm run dev:ai-agent      # Port 8788
npm run dev:fireflies     # Port 8789
npm run dev:vectorize     # Port 8790
npm run dev:insights      # Port 8791

# Deploy all workers
npm run deploy:all
```

## Environment Configuration

Each worker requires specific environment variables and Cloudflare resources:

### Shared Resources
- **D1 Database**: `alleato` (ID: `fc7c9a6d-ca65-4768-b3f9-07ec5afb38c5`)
- **Vectorize Index**: `fireflies-transcripts`
- **R2 Bucket**: `alleato-files`

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Fireflies.ai Configuration
FIREFLIES_API_KEY=your_fireflies_api_key

# Worker URLs (for cross-worker communication)
AI_AGENT_WORKER_URL=http://localhost:8788
VECTORIZE_WORKER_URL=http://localhost:8790
```

## Deployment

### Individual Worker Deployment
```bash
cd ai-agent-worker
wrangler deploy

cd ../fireflies-ingest-worker
wrangler deploy

cd ../vectorize-worker
wrangler deploy
```

### Automated Deployment
```bash
npm run deploy:all
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │────│  AI Agent Worker │────│  D1 Database    │
│   (Next.js)     │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                │
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Fireflies Ingest │────│  R2 Storage     │
                       │     Worker       │    │                 │
                       └──────────────────┘    └─────────────────┘
                                │
                                │ Queue
                                ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Vectorize Worker │────│ Vectorize Index │
                       │                  │    │                 │
                       └──────────────────┘    └─────────────────┘
```

## Contributing

1. Create feature branch from `main`
2. Develop and test locally
3. Run `npm run lint` and `npm run typecheck`
4. Create pull request

## License

Private - Alleato Technologies