"""
Clean up database and organize files for production
"""
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def cleanup_database():
    """Clean up database - remove test data and optimize"""
    print("🧹 Cleaning up database...\n")
    
    # 1. Remove meetings without chunks (failed uploads)
    print("📋 Checking for meetings without chunks...")
    meetings = supabase.table('meetings').select('id, title, (meeting_chunks!inner(count))').execute()
    
    meetings_without_chunks = []
    for meeting in meetings.data:
        # If no chunks relationship exists, this meeting has no chunks
        if not meeting.get('meeting_chunks'):
            meetings_without_chunks.append(meeting)
    
    if meetings_without_chunks:
        print(f"Found {len(meetings_without_chunks)} meetings without chunks:")
        for m in meetings_without_chunks:
            print(f"  - {m['title']}")
        
        response = input("\nDelete these meetings? (y/n): ")
        if response.lower() == 'y':
            for m in meetings_without_chunks:
                supabase.table('meetings').delete().eq('id', m['id']).execute()
                print(f"  ✅ Deleted: {m['title']}")
    else:
        print("✅ All meetings have chunks")
    
    # 2. Clean up orphaned chunks
    print("\n📋 Checking for orphaned chunks...")
    chunks = supabase.table('meeting_chunks').select('id, meeting_id').execute()
    meetings = supabase.table('meetings').select('id').execute()
    
    meeting_ids = {m['id'] for m in meetings.data}
    orphaned_chunks = [c for c in chunks.data if c['meeting_id'] not in meeting_ids]
    
    if orphaned_chunks:
        print(f"Found {len(orphaned_chunks)} orphaned chunks")
        response = input("Delete orphaned chunks? (y/n): ")
        if response.lower() == 'y':
            for chunk in orphaned_chunks:
                supabase.table('meeting_chunks').delete().eq('id', chunk['id']).execute()
            print(f"  ✅ Deleted {len(orphaned_chunks)} orphaned chunks")
    else:
        print("✅ No orphaned chunks found")
    
    # 3. Remove duplicate projects
    print("\n📋 Checking for duplicate projects...")
    projects = supabase.table('projects').select('*').order('name').execute()
    
    seen_names = {}
    duplicates = []
    
    for project in projects.data:
        name = project['name'].strip().lower()
        if name in seen_names:
            # Check which has more meetings
            existing_meetings = supabase.table('meetings').select('id', count='exact').eq('project_id', seen_names[name]['id']).execute()
            current_meetings = supabase.table('meetings').select('id', count='exact').eq('project_id', project['id']).execute()
            
            if current_meetings.count > existing_meetings.count:
                duplicates.append(seen_names[name])
                seen_names[name] = project
            else:
                duplicates.append(project)
        else:
            seen_names[name] = project
    
    if duplicates:
        print(f"Found {len(duplicates)} duplicate projects:")
        for p in duplicates:
            print(f"  - {p['name']} (ID: {p['id']})")
        
        response = input("\nMerge and remove duplicates? (y/n): ")
        if response.lower() == 'y':
            for dup in duplicates:
                # Find the keeper
                keeper = seen_names[dup['name'].strip().lower()]
                
                # Move all meetings to keeper
                supabase.table('meetings').update({'project_id': keeper['id']}).eq('project_id', dup['id']).execute()
                
                # Delete duplicate
                supabase.table('projects').delete().eq('id', dup['id']).execute()
                print(f"  ✅ Merged {dup['name']} into project {keeper['id']}")
    else:
        print("✅ No duplicate projects found")
    
    print("\n✅ Database cleanup complete!")


def organize_files():
    """Organize project files into proper directory structure"""
    print("\n📁 Organizing project files...\n")
    
    # Create organized directory structure
    directories = {
        'scripts': 'Python scripts for pipeline operations',
        'scripts/sync': 'Sync and ingestion scripts',
        'scripts/utils': 'Utility scripts',
        'sql': 'SQL schema and queries',
        'docs': 'Documentation',
        'config': 'Configuration files',
        'workers': 'Cloudflare worker templates',
        'tests': 'Test scripts',
        'archive': 'Old/unused files'
    }
    
    for dir_path, description in directories.items():
        os.makedirs(dir_path, exist_ok=True)
        # Create README in each directory
        with open(f"{dir_path}/README.md", "w") as f:
            f.write(f"# {dir_path.split('/')[-1].title()}\n\n{description}\n")
    
    # Move files to appropriate directories
    file_mappings = {
        # Sync scripts
        'fireflies_client.py': 'scripts/sync/fireflies_client.py',
        'markdown_converter.py': 'scripts/sync/markdown_converter.py',
        'supabase_uploader.py': 'scripts/sync/supabase_uploader.py',
        'supabase_uploader_v2.py': 'scripts/sync/supabase_uploader_v2.py',
        'supabase_uploader_adapter.py': 'scripts/sync/supabase_uploader_adapter.py',
        'pipeline_orchestrator.py': 'scripts/sync/pipeline_orchestrator.py',
        'sync_all_transcripts.py': 'scripts/sync/sync_all_transcripts.py',
        'reprocess_chunks.py': 'scripts/sync/reprocess_chunks.py',
        
        # Utils
        'check_sync_status.py': 'scripts/utils/check_sync_status.py',
        'verify_uploads.py': 'scripts/utils/verify_uploads.py',
        'quick_status.py': 'scripts/utils/quick_status.py',
        'sync_report.py': 'scripts/utils/sync_report.py',
        'update_project_assignments.py': 'scripts/utils/update_project_assignments.py',
        'setup_projects.py': 'scripts/utils/setup_projects.py',
        
        # SQL files
        'supabase_schema.sql': 'sql/supabase_schema.sql',
        'add_missing_components.sql': 'sql/add_missing_components.sql',
        'setup_storage_bucket.sql': 'sql/setup_storage_bucket.sql',
        'supabase_simple_schema.sql': 'sql/supabase_simple_schema.sql',
        
        # Documentation
        'supabase_implementation_guide.md': 'docs/supabase_implementation_guide.md',
        'CLAUDE.md': 'docs/CLAUDE.md',
        
        # Tests
        'test_pipeline.py': 'tests/test_pipeline.py',
        'test_pipeline_no_embeddings.py': 'tests/test_pipeline_no_embeddings.py',
        'test_openai_key.py': 'tests/test_openai_key.py',
        'debug_fireflies_api.py': 'tests/debug_fireflies_api.py',
        
        # Config
        '.env.example': 'config/.env.example',
        
        # Archive old versions
        'fireflies_webhook_pipeline.py': 'archive/fireflies_webhook_pipeline.py',
        'web_api.py': 'archive/web_api.py',
        'execute_supabase_schema.py': 'archive/execute_supabase_schema.py',
        'check_meetings_schema.py': 'archive/check_meetings_schema.py',
        'check_actual_schema.py': 'archive/check_actual_schema.py',
        'setup_supabase_direct.py': 'archive/setup_supabase_direct.py'
    }
    
    moved_count = 0
    for src, dst in file_mappings.items():
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            print(f"  ✅ Moved {src} → {dst}")
            moved_count += 1
    
    print(f"\n✅ Moved {moved_count} files")
    
    # Create main entry point script
    with open("run_sync.py", "w") as f:
        f.write('''#!/usr/bin/env python3
"""
Main entry point for Fireflies sync pipeline
"""
import sys
sys.path.append('scripts/sync')

from sync_all_transcripts import sync_all_transcripts

if __name__ == "__main__":
    limit = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        limit = int(sys.argv[1])
    
    sync_all_transcripts(limit=limit)
''')
    
    os.chmod("run_sync.py", 0o755)
    print("✅ Created run_sync.py entry point")
    
    # Create project README
    create_main_readme()


def create_main_readme():
    """Create comprehensive project README"""
    readme_content = '''# Fireflies Transcripts RAG Pipeline

A complete pipeline for syncing Fireflies.ai meeting transcripts to Supabase with vector embeddings for RAG (Retrieval-Augmented Generation).

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config/.env.example .env
# Edit .env with your credentials

# Run the sync
python run_sync.py

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
│   │   └── sync_all_transcripts.py
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

### Sync All Transcripts
```bash
python run_sync.py
```

### Sync Limited Number
```bash
python run_sync.py 25  # Sync 25 most recent
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
'''
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ Created comprehensive README.md")


def cleanup_temp_files():
    """Remove temporary and unnecessary files"""
    print("\n🗑️  Cleaning up temporary files...\n")
    
    # Files to remove
    remove_patterns = [
        "*.pyc",
        "__pycache__",
        ".DS_Store",
        "*.log",
        "test_*.md"  # Test markdown files
    ]
    
    removed_count = 0
    
    # Remove Python cache
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))
            print(f"  ✅ Removed {root}/__pycache__")
            removed_count += 1
        
        for file in files:
            if file.endswith(".pyc") or file == ".DS_Store":
                os.remove(os.path.join(root, file))
                print(f"  ✅ Removed {os.path.join(root, file)}")
                removed_count += 1
    
    print(f"\n✅ Removed {removed_count} temporary files")


def main(auto_yes=False):
    """Run all cleanup and organization tasks"""
    print("🚀 Starting cleanup and organization...\n")
    
    # 1. Clean database
    if auto_yes:
        print("Skipping database cleanup in auto mode")
    else:
        response = input("Clean up database? (y/n): ")
        if response.lower() == 'y':
            cleanup_database()
    
    # 2. Organize files
    if auto_yes:
        print("\n📁 Auto-organizing files...")
        organize_files()
    else:
        response = input("\nOrganize project files? (y/n): ")
        if response.lower() == 'y':
            organize_files()
    
    # 3. Clean temporary files
    if auto_yes:
        print("\n🗑️  Auto-cleaning temporary files...")
        cleanup_temp_files()
    else:
        response = input("\nRemove temporary files? (y/n): ")
        if response.lower() == 'y':
            cleanup_temp_files()
    
    print("\n✅ Cleanup and organization complete!")
    print("\n📋 Next steps:")
    print("1. Review the new file structure")
    print("2. Update any import paths in your code")
    print("3. Commit the organized structure to git")
    print("4. Set up Cloudflare Workers using the templates in workers/")


if __name__ == "__main__":
    import sys
    auto = "--auto" in sys.argv
    main(auto_yes=auto)