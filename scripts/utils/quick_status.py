"""
Quick status check of sync progress
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get counts
meetings = supabase.table('meetings').select('id', count='exact').execute()
chunks = supabase.table('meeting_chunks').select('id', count='exact').execute()

print(f"📊 Database Status:")
print(f"   Total meetings: {meetings.count}")
print(f"   Total chunks: {chunks.count}")

# Get recent additions
recent = supabase.table('meetings').select('title, created_at, raw_metadata').order('created_at', desc=True).limit(5).execute()

print(f"\n📅 Most recently added:")
for meeting in recent.data:
    created = meeting['created_at'][:19].replace('T', ' ')
    
    # Get Fireflies ID from metadata
    metadata = meeting.get('raw_metadata', {})
    if isinstance(metadata, str):
        import json
        try:
            metadata = json.loads(metadata)
        except:
            metadata = {}
    
    fireflies_id = metadata.get('fireflies_id', 'N/A')
    duration = metadata.get('duration', 0)
    
    print(f"   - {meeting['title'][:40]}... ({created})")
    print(f"     Duration: {duration:.1f} min, ID: {fireflies_id}")

# Check processing rate
one_minute_ago = datetime.utcnow().replace(second=0, microsecond=0)
recent_count = supabase.table('meetings').select('id', count='exact').gte('created_at', one_minute_ago.isoformat()).execute()

if recent_count.count > 0:
    print(f"\n⚡ Processing rate: {recent_count.count} meetings in the last minute")