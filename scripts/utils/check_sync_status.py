"""
Check sync status - compare Fireflies API with database
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from fireflies_client import FirefliesClient
from supabase import create_client

load_dotenv()

# Initialize clients
fireflies = FirefliesClient()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Checking sync status...\n")

# Get all transcripts from Fireflies
print("📥 Fetching from Fireflies API...")
try:
    # Try different limits to see if there are more
    for limit in [10, 25, 50, 100]:
        fireflies_transcripts = fireflies.fetch_transcripts(limit=limit)
        if fireflies_transcripts:
            print(f"   Limit {limit}: Got {len(fireflies_transcripts)} transcripts")
            if len(fireflies_transcripts) < limit:
                break
        else:
            print(f"   Limit {limit}: Got 0 transcripts")
            break
    
    if not fireflies_transcripts:
        print("❌ No transcripts returned from Fireflies")
        exit(1)
        
except Exception as e:
    print(f"❌ Error fetching from Fireflies: {e}")
    exit(1)

# Get all meetings from database
print("\n📊 Fetching from database...")
db_meetings = supabase.table("meetings").select("*, chunks:meeting_chunks(count)").execute()

# Extract Fireflies IDs from database
db_fireflies_ids = set()
for meeting in db_meetings.data:
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

# Compare
fireflies_ids = {t['id'] for t in fireflies_transcripts}

print(f"\n📊 Summary:")
print(f"   Fireflies API: {len(fireflies_ids)} transcripts")
print(f"   Database: {len(db_meetings.data)} meetings")
print(f"   Database (with Fireflies ID): {len(db_fireflies_ids)} meetings")

# Find differences
missing_from_db = fireflies_ids - db_fireflies_ids
extra_in_db = db_fireflies_ids - fireflies_ids

if missing_from_db:
    print(f"\n❌ Missing from database ({len(missing_from_db)}):")
    for transcript in fireflies_transcripts:
        if transcript['id'] in missing_from_db:
            date = datetime.fromtimestamp(transcript['date'] / 1000).strftime('%Y-%m-%d')
            print(f"   - {transcript['title']} ({date}) - ID: {transcript['id']}")
else:
    print(f"\n✅ All Fireflies transcripts are in the database!")

if extra_in_db:
    print(f"\n⚠️  In database but not in Fireflies API ({len(extra_in_db)}):")
    for fid in extra_in_db:
        print(f"   - ID: {fid}")

# Check chunks
print(f"\n📝 Chunk Status:")
total_chunks = 0
meetings_with_chunks = 0
meetings_without_chunks = 0

for meeting in db_meetings.data:
    chunk_count = meeting.get('chunks', [{}])[0].get('count', 0) if meeting.get('chunks') else 0
    total_chunks += chunk_count
    
    if chunk_count > 0:
        meetings_with_chunks += 1
    else:
        meetings_without_chunks += 1
        
print(f"   Total chunks: {total_chunks}")
print(f"   Meetings with chunks: {meetings_with_chunks}")
print(f"   Meetings without chunks: {meetings_without_chunks}")

if meetings_without_chunks > 0:
    print(f"\n⚠️  Meetings without chunks:")
    for meeting in db_meetings.data:
        chunk_count = meeting.get('chunks', [{}])[0].get('count', 0) if meeting.get('chunks') else 0
        if chunk_count == 0:
            print(f"   - {meeting['title']}")

print("\n✅ Sync status check complete!")