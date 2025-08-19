"""
Test script to process the last 10 Fireflies meetings
and upload them to Supabase using the new schema.
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Import our modules
from fireflies_client import FirefliesClient
from markdown_converter import MarkdownConverter
from supabase_uploader_adapter import SupabaseUploaderAdapter

load_dotenv()


def test_pipeline(limit=10):
    """Test the pipeline with a limited number of meetings."""
    
    print(f"🚀 Starting pipeline test with {limit} meetings...")
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize components
    try:
        fireflies = FirefliesClient()
        converter = MarkdownConverter()
        uploader = SupabaseUploaderAdapter()
        
        # Test storage bucket first
        print("🪣 Checking storage bucket...")
        uploader.ensure_storage_bucket()
        print("✅ Storage bucket ready\n")
        
    except Exception as e:
        print(f"❌ Failed to initialize components: {e}")
        return
    
    # Fetch transcripts
    try:
        print(f"📋 Fetching last {limit} transcripts from Fireflies...")
        transcripts = fireflies.fetch_transcripts(limit=limit)
        print(f"✅ Found {len(transcripts)} transcripts\n")
        
        if not transcripts:
            print("❌ No transcripts found!")
            return
        
        # Show what we're going to process
        print("📝 Transcripts to process:")
        for i, t in enumerate(transcripts, 1):
            date = datetime.fromtimestamp(t["date"] / 1000).strftime("%Y-%m-%d")
            print(f"   {i}. {t['title'][:50]}... ({date})")
        print()
        
    except Exception as e:
        print(f"❌ Failed to fetch transcripts: {e}")
        return
    
    # Process each transcript
    processed = 0
    skipped = 0
    errors = 0
    
    for i, transcript_summary in enumerate(transcripts, 1):
        transcript_id = transcript_summary["id"]
        title = transcript_summary["title"]
        
        print(f"\n{'='*60}")
        print(f"🔄 [{i}/{len(transcripts)}] Processing: {title}")
        print(f"   ID: {transcript_id}")
        
        try:
            # Step 1: Fetch full transcript
            print("   📥 Fetching full transcript...")
            full_transcript = fireflies.fetch_transcript_detail(transcript_id)
            
            # Show some stats
            duration = full_transcript.get("duration", 0)
            participants = full_transcript.get("participants", [])
            sentences = full_transcript.get("sentences", [])
            
            print(f"   📊 Duration: {duration} minutes")
            print(f"   👥 Participants: {len(participants)}")
            print(f"   💬 Sentences: {len(sentences)}")
            
            # Step 2: Convert to markdown
            print("   📝 Converting to markdown...")
            filepath, markdown_text = converter.save_markdown(full_transcript)
            print(f"   ✅ Saved to: {filepath}")
            
            # Step 3: Upload to Supabase
            print("   ☁️  Uploading to Supabase...")
            success = uploader.process_and_store(full_transcript, markdown_text, filepath)
            
            if success:
                processed += 1
                print("   ✅ Successfully processed!")
            else:
                skipped += 1
                print("   ⏩ Skipped (already exists)")
                
        except Exception as e:
            errors += 1
            print(f"   ❌ Error: {str(e)}")
            
            # More detailed error info
            import traceback
            if "--debug" in sys.argv:
                print("\n   Debug trace:")
                traceback.print_exc()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Test Pipeline Summary:")
    print(f"   ✅ Processed: {processed}")
    print(f"   ⏩ Skipped: {skipped}")
    print(f"   ❌ Errors: {errors}")
    print(f"   📋 Total: {len(transcripts)}")
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify in database
    if processed > 0:
        print("\n🔍 Verifying in database...")
        try:
            from supabase import create_client
            
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            supabase = create_client(supabase_url, supabase_key)
            
            # Check meetings table
            meetings = supabase.table("meetings").select("id, title, created_at").order("created_at", desc=True).limit(processed).execute()
            print(f"\n📋 Recent meetings in database:")
            for meeting in meetings.data:
                print(f"   - {meeting['title'][:50]}... (ID: {meeting['id'][:8]}...)")
            
            # Check chunks
            chunks_count = supabase.table("meeting_chunks").select("id", count="exact").execute()
            print(f"\n📊 Total chunks in database: {chunks_count.count}")
            
        except Exception as e:
            print(f"❌ Could not verify database: {e}")


if __name__ == "__main__":
    # Check for custom limit
    limit = 10
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except:
            pass
    
    test_pipeline(limit=limit)