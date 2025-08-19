"""
Sync all remaining Fireflies transcripts to Supabase
Processes from most recent to oldest
"""
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Import our modules
from fireflies_client import FirefliesClient
from markdown_converter import MarkdownConverter
from supabase_uploader_adapter import SupabaseUploaderAdapter
from supabase import create_client
from openai import OpenAI
import tiktoken

load_dotenv()


class FullSyncUploader(SupabaseUploaderAdapter):
    """Enhanced uploader with embeddings for full sync"""
    
    def __init__(self):
        super().__init__()
        self.processed_count = 0
        self.skip_count = 0
        self.error_count = 0
        
    def embed_text(self, text, retries=3):
        """Generate embedding for text with retry logic."""
        for attempt in range(retries):
            try:
                res = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return res.data[0].embedding
            except Exception as e:
                if attempt < retries - 1:
                    print(f"   Retrying embedding (attempt {attempt + 1}): {str(e)[:50]}")
                    time.sleep(1)
                else:
                    raise RuntimeError(f"Embedding failed after {retries} attempts: {e}")
    
    def store_meeting_chunks(self, meeting_id, project_id, chunks, title):
        """Store meeting chunks with embeddings"""
        stored = 0
        
        for i, (start, end, chunk_text) in enumerate(chunks):
            try:
                print(f"   📊 Processing chunk {i+1}/{len(chunks)}...", end="\r")
                embedding = self.embed_text(chunk_text)
                
                chunk_data = {
                    "meeting_id": meeting_id,
                    "chunk_index": i,
                    "content": chunk_text,
                    "embedding": embedding,
                    "metadata": {
                        "token_range": {"start": start, "end": end},
                        "chunk_number": i + 1,
                        "total_chunks": len(chunks),
                        "project_id": project_id,
                        "meeting_title": title
                    }
                }
                
                self.supabase.table("meeting_chunks").insert(chunk_data).execute()
                stored += 1
                
            except Exception as e:
                print(f"\n   ⚠️  Error storing chunk {i}: {str(e)[:100]}")
        
        print(f"\n   ✅ {stored}/{len(chunks)} chunks stored with embeddings")
        return stored > 0
    
    def get_stats(self):
        """Get processing statistics"""
        return {
            "processed": self.processed_count,
            "skipped": self.skip_count,
            "errors": self.error_count
        }


def get_existing_transcript_ids():
    """Get list of transcript IDs already in database"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    # Get all existing transcript IDs from raw_metadata
    meetings = supabase.table("meetings").select("raw_metadata").execute()
    
    existing_ids = set()
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
            existing_ids.add(fireflies_id)
    
    return existing_ids


def sync_all_transcripts(limit=None, skip_existing=True):
    """Sync all transcripts from Fireflies to Supabase"""
    
    print(f"🚀 Starting full Fireflies sync...")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize components
    try:
        fireflies = FirefliesClient()
        converter = MarkdownConverter()
        uploader = FullSyncUploader()
        
        # Test connections
        print("🔌 Testing connections...")
        uploader.ensure_storage_bucket()
        print("✅ Storage bucket ready")
        
        # Test OpenAI
        test_embed = uploader.embed_text("test")
        print(f"✅ OpenAI embeddings working (dim: {len(test_embed)})")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Get existing transcript IDs
    existing_ids = set()
    if skip_existing:
        print("\n📋 Checking existing transcripts...")
        existing_ids = get_existing_transcript_ids()
        print(f"📊 Found {len(existing_ids)} transcripts already in database")
    
    # Fetch all transcripts
    try:
        print(f"\n📥 Fetching transcripts from Fireflies...")
        
        # Fireflies API seems to have limits on how many it returns
        # Start with a known working limit
        fetch_limit = limit if limit else 50  # 50 works based on our testing
        
        print(f"   Requesting up to {fetch_limit} transcripts...")
        all_transcripts = fireflies.fetch_transcripts(limit=fetch_limit)
        
        # Handle None response
        if all_transcripts is None:
            print("   API returned None, trying smaller limit...")
            for try_limit in [25, 10]:
                all_transcripts = fireflies.fetch_transcripts(limit=try_limit)
                if all_transcripts is not None:
                    print(f"   Got {len(all_transcripts)} transcripts with limit {try_limit}")
                    break
        
        if all_transcripts is None:
            all_transcripts = []
            print("   ⚠️  Could not fetch any transcripts")
        
        print(f"✅ Found {len(all_transcripts)} total transcripts\n")
        
        # Sort by date (most recent first)
        all_transcripts.sort(key=lambda x: x['date'], reverse=True)
        
        # Filter out existing if requested
        if skip_existing:
            new_transcripts = [t for t in all_transcripts if t['id'] not in existing_ids]
            print(f"📊 {len(new_transcripts)} new transcripts to process")
            print(f"⏩ {len(all_transcripts) - len(new_transcripts)} already in database\n")
            transcripts_to_process = new_transcripts
        else:
            transcripts_to_process = all_transcripts
        
        if not transcripts_to_process:
            print("✅ All transcripts are already synced!")
            return
        
        # Show what we're going to process
        print("📝 Transcripts to process (most recent first):")
        for i, t in enumerate(transcripts_to_process[:10]):  # Show first 10
            date = datetime.fromtimestamp(t["date"] / 1000).strftime("%Y-%m-%d")
            print(f"   {i+1}. {t['title'][:50]}... ({date})")
        if len(transcripts_to_process) > 10:
            print(f"   ... and {len(transcripts_to_process) - 10} more")
        print()
        
    except Exception as e:
        print(f"❌ Failed to fetch transcripts: {e}")
        return
    
    # Process each transcript
    for i, transcript_summary in enumerate(transcripts_to_process, 1):
        transcript_id = transcript_summary["id"]
        title = transcript_summary["title"]
        date = datetime.fromtimestamp(transcript_summary["date"] / 1000).strftime("%Y-%m-%d")
        
        print(f"\n{'='*60}")
        print(f"🔄 [{i}/{len(transcripts_to_process)}] Processing: {title}")
        print(f"   📅 Date: {date}")
        print(f"   🆔 ID: {transcript_id}")
        
        try:
            # Fetch full transcript
            print("   📥 Fetching full transcript...")
            full_transcript = fireflies.fetch_transcript_detail(transcript_id)
            
            # Show stats
            duration = full_transcript.get("duration", 0)
            participants = full_transcript.get("participants") or []
            sentences = full_transcript.get("sentences") or []
            
            print(f"   📊 Duration: {duration:.1f} minutes")
            print(f"   👥 Participants: {len(participants)}")
            print(f"   💬 Sentences: {len(sentences)}")
            
            # Convert to markdown
            print("   📝 Converting to markdown...")
            filepath, markdown_text = converter.save_markdown(full_transcript)
            print(f"   ✅ Saved: {os.path.basename(filepath)}")
            
            # Upload to Supabase
            print("   ☁️  Uploading to Supabase...")
            success = uploader.process_and_store(full_transcript, markdown_text, filepath)
            
            if success:
                uploader.processed_count += 1
                print("   ✅ Successfully processed!")
            else:
                uploader.skip_count += 1
                print("   ⏩ Skipped (already exists)")
            
            # Rate limiting
            if i % 5 == 0:
                print("\n⏸️  Pausing for rate limit...")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Sync interrupted by user")
            break
            
        except Exception as e:
            uploader.error_count += 1
            print(f"   ❌ Error: {str(e)}")
            
            # More detailed error info
            import traceback
            if "--debug" in sys.argv:
                print("\n   Debug trace:")
                traceback.print_exc()
    
    # Summary
    stats = uploader.get_stats()
    print(f"\n{'='*60}")
    print(f"📊 Sync Summary:")
    print(f"   ✅ Processed: {stats['processed']}")
    print(f"   ⏩ Skipped: {stats['skipped']}")
    print(f"   ❌ Errors: {stats['errors']}")
    print(f"   📋 Total attempted: {len(transcripts_to_process)}")
    
    # Verify in database
    print("\n🔍 Verifying database...")
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        # Count totals
        meetings_count = supabase.table("meetings").select("id", count="exact").execute()
        chunks_count = supabase.table("meeting_chunks").select("id", count="exact").execute()
        
        print(f"📊 Total meetings in database: {meetings_count.count}")
        print(f"📊 Total chunks in database: {chunks_count.count}")
        
        # Show recent additions
        if stats['processed'] > 0:
            recent = supabase.table("meetings").select("title, created_at").order("created_at", desc=True).limit(5).execute()
            print("\n📋 Recently added meetings:")
            for meeting in recent.data:
                print(f"   - {meeting['title'][:60]}...")
        
    except Exception as e:
        print(f"❌ Could not verify database: {e}")
    
    print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✅ Sync complete!")


if __name__ == "__main__":
    # Parse arguments
    limit = None
    skip_existing = True
    
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            limit = int(sys.argv[1])
        elif sys.argv[1] == "--all":
            skip_existing = False
    
    if "--help" in sys.argv:
        print("Usage: python sync_all_transcripts.py [limit] [--all]")
        print("  limit: Maximum number of transcripts to process")
        print("  --all: Process all transcripts, including existing ones")
        sys.exit(0)
    
    sync_all_transcripts(limit=limit, skip_existing=skip_existing)