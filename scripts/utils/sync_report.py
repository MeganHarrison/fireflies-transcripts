"""
Generate a comprehensive sync report
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from fireflies_client import FirefliesClient
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
fireflies = FirefliesClient()

print("📊 FIREFLIES SYNC REPORT")
print("=" * 60)
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Database stats
meetings = supabase.table('meetings').select('id, date, raw_metadata', count='exact').execute()
chunks = supabase.table('meeting_chunks').select('id', count='exact').execute()

print("📈 DATABASE STATISTICS:")
print(f"   Total meetings: {meetings.count}")
print(f"   Total chunks: {chunks.count}")
print(f"   Average chunks per meeting: {chunks.count / meetings.count:.1f}")

# Date range
if meetings.data:
    dates = []
    for m in meetings.data:
        try:
            dates.append(datetime.fromisoformat(m['date'].replace('Z', '+00:00')))
        except:
            pass
    
    if dates:
        oldest = min(dates)
        newest = max(dates)
        print(f"   Date range: {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}")
        print(f"   Days covered: {(newest - oldest).days + 1}")

# Get Fireflies IDs
db_fireflies_ids = set()
for meeting in meetings.data:
    metadata = meeting.get('raw_metadata', {})
    if isinstance(metadata, str):
        import json
        try:
            metadata = json.loads(metadata)
        except:
            continue
    fireflies_id = metadata.get('fireflies_id')
    if fireflies_id:
        db_fireflies_ids.add(fireflies_id)

# Compare with Fireflies API
print("\n📡 FIREFLIES API STATUS:")
try:
    fireflies_transcripts = fireflies.fetch_transcripts(limit=50)
    if fireflies_transcripts:
        fireflies_ids = {t['id'] for t in fireflies_transcripts}
        
        print(f"   Available transcripts: {len(fireflies_ids)}")
        print(f"   Synced to database: {len(db_fireflies_ids)}")
        
        missing = fireflies_ids - db_fireflies_ids
        print(f"   Not yet synced: {len(missing)}")
        
        if missing:
            print("\n   📋 Missing transcripts (first 5):")
            for transcript in fireflies_transcripts[:5]:
                if transcript['id'] in missing:
                    date = datetime.fromtimestamp(transcript['date'] / 1000).strftime('%Y-%m-%d')
                    print(f"      - {transcript['title'][:40]}... ({date})")
except Exception as e:
    print(f"   ❌ Error fetching from API: {e}")

# Project distribution
print("\n🏢 PROJECT DISTRIBUTION:")
project_stats = supabase.table('meetings').select('project_id, project:projects(name)').execute()

project_counts = {}
for meeting in project_stats.data:
    project_name = "Not Assigned"
    if meeting.get('project') and meeting['project'].get('name'):
        project_name = meeting['project']['name']
    elif meeting.get('project_id'):
        project_name = f"Project ID {meeting['project_id']}"
    
    project_counts[project_name] = project_counts.get(project_name, 0) + 1

# Sort by count
sorted_projects = sorted(project_counts.items(), key=lambda x: x[1], reverse=True)
for project, count in sorted_projects[:10]:
    print(f"   {project}: {count} meetings")

if len(sorted_projects) > 10:
    print(f"   ... and {len(sorted_projects) - 10} more projects")

# Storage stats
print("\n💾 STORAGE STATISTICS:")
try:
    files = supabase.storage.from_("meetings").list()
    total_size = sum(f.get('metadata', {}).get('size', 0) for f in files)
    print(f"   Files in storage: {len(files)}")
    print(f"   Total size: {total_size / 1024 / 1024:.1f} MB")
    print(f"   Average file size: {total_size / len(files) / 1024:.1f} KB")
except Exception as e:
    print(f"   ⚠️  Could not get storage stats: {e}")

print("\n✅ SYNC SUMMARY:")
sync_percentage = (len(db_fireflies_ids) / len(fireflies_ids) * 100) if fireflies_ids else 100
print(f"   Sync completion: {sync_percentage:.1f}%")
print(f"   Ready for RAG: {'Yes' if chunks.count > 0 else 'No'}")
print(f"   Vector search enabled: {'Yes' if chunks.count > 0 else 'No'}")

print("\n" + "=" * 60)