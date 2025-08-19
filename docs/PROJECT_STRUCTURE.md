# Project Structure

## 📁 Directory Layout

```
fireflies-transcripts/
├── run_sync.py              # Main entry point for syncing
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
├── .env                    # Environment variables (not in git)
├── PROJECT_STRUCTURE.md    # This file
│
├── scripts/                # All Python scripts
│   ├── sync/              # Sync and ingestion scripts
│   │   ├── fireflies_client.py        # Fireflies API client
│   │   ├── markdown_converter.py      # JSON to Markdown converter
│   │   ├── supabase_uploader_adapter.py  # Supabase upload handler
│   │   ├── sync_all_transcripts.py   # Main sync script
│   │   └── reprocess_chunks.py       # Reprocess for embeddings
│   │
│   └── utils/             # Utility scripts
│       ├── sync_report.py            # Generate sync reports
│       ├── verify_uploads.py         # Verify uploads
│       ├── quick_status.py           # Quick status check
│       └── update_project_assignments.py  # Manage projects
│
├── sql/                   # Database schemas
│   ├── supabase_schema.sql          # Main database schema
│   ├── add_missing_components.sql   # Additional components
│   └── setup_storage_bucket.sql     # Storage setup
│
├── docs/                  # Documentation
│   ├── CLAUDE.md                    # AI assistant instructions
│   └── supabase_implementation_guide.md  # Implementation guide
│
├── config/                # Configuration files
│   └── .env.example                 # Example environment variables
│
├── tests/                 # Test scripts
│   ├── test_pipeline.py             # Pipeline tests
│   ├── test_openai_key.py          # API key tests
│   └── debug_fireflies_api.py      # API debugging
│
├── transcripts/          # Downloaded markdown files (36 files)
│
├── workers/              # Cloudflare worker templates
│   └── README.md                    # Worker documentation
│
├── archive/              # Old/unused files
│   └── [various old scripts]
│
└── alleato-elements-workers/  # Cloudflare worker implementations
    ├── fireflies-ingest-worker/
    ├── vectorize-worker/
    └── ai-agent-worker/
```

## 🚀 Quick Commands

### Sync Transcripts
```bash
python run_sync.py          # Sync all new transcripts
python run_sync.py 25       # Sync 25 most recent
```

### Check Status
```bash
python scripts/utils/sync_report.py    # Full report
python scripts/utils/quick_status.py   # Quick status
```

### Manage Projects
```bash
python scripts/utils/update_project_assignments.py
```

## 📊 Current Status

- **36 meetings** synced to Supabase
- **460 chunks** with vector embeddings
- **0.9 MB** of transcript data
- **72%** of available transcripts synced

## 🔧 Configuration

All configuration is in `.env`:
- `FIREFLIES_API_KEY` - Fireflies.ai API key
- `OPENAI_API_KEY` - OpenAI API key for embeddings
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service role key

## 📝 Next Steps

1. Complete sync of remaining transcripts
2. Set up Cloudflare Workers for automation
3. Implement insights generation
4. Build front-end dashboard