"""
Verify the meetings uploaded to Supabase
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Checking uploaded meetings in Supabase...\n")

# Get recent meetings
try:
    meetings = supabase.table("meetings").select("*").order("created_at", desc=True).limit(10).execute()
    
    print(f"📊 Found {len(meetings.data)} recent meetings:\n")
    
    for i, meeting in enumerate(meetings.data, 1):
        # Handle different date formats
        date_str = meeting['date'].replace('Z', '+00:00')
        created_str = meeting['created_at'].replace('Z', '+00:00')
        
        # Fix microsecond precision if needed
        if '.' in date_str and '+' in date_str:
            date_parts = date_str.split('+')
            date_base = date_parts[0].split('.')
            if len(date_base[1]) > 6:
                date_str = f"{date_base[0]}.{date_base[1][:6]}+{date_parts[1]}"
        
        if '.' in created_str and '+' in created_str:
            created_parts = created_str.split('+')
            created_base = created_parts[0].split('.')
            if len(created_base[1]) > 6:
                created_str = f"{created_base[0]}.{created_base[1][:6]}+{created_parts[1]}"
        
        meeting_date = datetime.fromisoformat(date_str)
        try:
            created_at = datetime.fromisoformat(created_str)
        except:
            # Fallback for problematic dates
            created_at = datetime.now()
        
        print(f"{i}. {meeting['title']}")
        print(f"   📅 Meeting Date: {meeting_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   🆔 ID: {meeting['id']}")
        print(f"   📁 Project: {meeting.get('project_id', 'Not assigned')}")
        
        # Handle participants - could be string or list
        participants = meeting.get('participants', [])
        if isinstance(participants, str):
            try:
                import json
                participants = json.loads(participants)
            except:
                participants = []
        print(f"   👥 Participants: {len(participants) if isinstance(participants, list) else 0}")
        
        print(f"   📎 Storage: {meeting.get('storage_bucket_path', 'N/A')}")
        print(f"   🕐 Created: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check metadata
        metadata = meeting.get('raw_metadata', {})
        if isinstance(metadata, str):
            try:
                import json
                metadata = json.loads(metadata)
            except:
                metadata = {}
        if metadata:
            print(f"   📊 Fireflies ID: {metadata.get('fireflies_id', 'N/A')}")
            print(f"   ⏱️  Duration: {metadata.get('duration', 0)} minutes")
        
        # Check chunks
        chunks = supabase.table("meeting_chunks").select("id").eq("meeting_id", meeting['id']).execute()
        print(f"   📝 Chunks: {len(chunks.data)}")
        
        print()
    
    # Summary stats
    print("\n📈 Summary Statistics:")
    
    # Total meetings
    total_meetings = supabase.table("meetings").select("id", count="exact").execute()
    print(f"   Total meetings: {total_meetings.count}")
    
    # Total chunks
    total_chunks = supabase.table("meeting_chunks").select("id", count="exact").execute()
    print(f"   Total chunks: {total_chunks.count}")
    
    # Check storage files
    print("\n📦 Storage Bucket Contents:")
    try:
        files = supabase.storage.from_("meetings").list()
        print(f"   Files in storage: {len(files)}")
        
        # Show recent files
        if files:
            print("   Recent files:")
            for file in files[:5]:
                print(f"     - {file['name']} ({file.get('metadata', {}).get('size', 0)} bytes)")
    except Exception as e:
        print(f"   ⚠️  Could not list storage: {e}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ Verification complete!")