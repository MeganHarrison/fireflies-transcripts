# Fireflies Transcripts RAG Pipeline

A complete pipeline for syncing Fireflies.ai meeting transcripts to Supabase with vector embeddings for RAG (Retrieval-Augmented Generation).

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config/.env.example .env
# Edit .env with your credentials

# Run the sync
python3 run_sync.py

# Check status
python scripts/utils/sync_report.py
```

## 📁 Project Structure

```
fireflies-transcripts/
├── run_sync.py              # Main entry point
├── scripts/
│   ├── sync/               # Sync and ingestion scripts
│   │   ├── fireflies_client.py
│   │   ├── markdown_converter.py
│   │   ├── supabase_uploader_adapter.py
│   │   ├── sync_all_transcripts.py
│   │   └── sync_all_transcripts_enhanced.py
│   └── utils/              # Utility scripts
│       ├── sync_report.py
│       ├── verify_uploads.py
│       └── update_project_assignments.py
├── sql/                    # Database schemas
│   └── supabase_schema.sql
├── docs/                   # Documentation
│   ├── CLAUDE.md
│   └── supabase_implementation_guide.md
├── transcripts/           # Downloaded markdown files
├── workers/               # Cloudflare worker templates
└── config/               # Configuration files
```

## 🔧 Configuration

Required environment variables in `.env`:

```bash
# Fireflies API
FIREFLIES_API_KEY=your_fireflies_api_key

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
```

## 📊 Database Schema

The pipeline uses these main tables:
- `projects` - Project organization
- `meetings` - Meeting metadata
- `meeting_chunks` - Vectorized content chunks
- `project_insights` - Extracted insights
- `project_tasks` - Action items

## 🛠️ Usage

### Sync New Transcripts (One-Time)
```bash
python3 run_sync.py
```

### Sync ALL Available Transcripts
```bash
python3 run_sync.py --all
```

### Continuous Sync Mode (Every 30 Minutes)
```bash
python3 run_sync.py --continuous
```

### Custom Sync Interval
```bash
python3 run_sync.py --continuous --interval 60  # Sync every 60 minutes
```

### Check Status
```bash
python scripts/utils/sync_report.py
```

### Update Project Assignments
```bash
python scripts/utils/update_project_assignments.py
```

## 📈 Current Status

- ✅ 36 meetings synced
- ✅ 460 chunks with embeddings
- ✅ Vector search enabled
- ✅ Ready for RAG applications

## 🚀 Next Steps

1. Set up Cloudflare Workers for:
   - Automated sync (cron)
   - Chat API endpoint
   - Insights generation

2. Build front-end for:
   - Project dashboards
   - Chat interface
   - Task management

## 📝 License

Private project - All rights reserved
