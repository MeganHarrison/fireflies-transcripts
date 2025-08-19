"""
Enhanced sync script that can fetch ALL transcripts and run continuously
"""
import os
import sys
import time
import signal
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync.fireflies_client import FirefliesClient
from sync.markdown_converter import MarkdownConverter
from sync.supabase_uploader_adapter import SupabaseUploaderAdapter
from supabase import create_client
from openai import OpenAI
import tiktoken

load_dotenv()

# Global flag for graceful shutdown
keep_running = True

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global keep_running
    print("\n\n⚠️  Shutdown signal received. Finishing current sync...")
    keep_running = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class EnhancedFirefliesClient(FirefliesClient):
    """Enhanced client that can fetch all available transcripts"""
    
    def fetch_all_transcripts(self, batch_size=50):
        """Fetch ALL available transcripts using proper pagination"""
        # Use the new paginated method
        return self.fetch_all_transcripts_paginated(batch_size=batch_size)


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


def get_existing_transcript_ids():
    """Get list of transcript IDs already in database"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
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


def sync_all_transcripts(continuous=False, interval_minutes=30):
    """
    Sync all transcripts from Fireflies to Supabase
    
    Args:
        continuous: If True, run continuously every interval_minutes
        interval_minutes: Minutes between syncs (default 30)
    """
    global keep_running
    
    # Initialize components once
    fireflies = EnhancedFirefliesClient()
    converter = MarkdownConverter()
    uploader = FullSyncUploader()
    
    run_count = 0
    
    while keep_running:
        run_count += 1
        
        print(f"\n{'='*60}")
        print(f"🚀 Sync Run #{run_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        try:
            # Test connections
            print("🔌 Testing connections...")
            uploader.ensure_storage_bucket()
            test_embed = uploader.embed_text("test")
            print(f"✅ All systems operational\n")
            
            # Get existing IDs
            print("📋 Checking existing transcripts...")
            existing_ids = get_existing_transcript_ids()
            print(f"📊 Found {len(existing_ids)} transcripts already in database")
            
            # Fetch ALL transcripts
            print("\n📥 Fetching ALL transcripts from Fireflies...")
            all_transcripts = fireflies.fetch_all_transcripts()
            
            if not all_transcripts:
                print("❌ No transcripts retrieved from Fireflies")
                if continuous:
                    print(f"\n⏰ Waiting {interval_minutes} minutes until next sync...")
                    time.sleep(interval_minutes * 60)
                    continue
                else:
                    return
            
            print(f"\n📊 Fireflies has {len(all_transcripts)} total transcripts")
            
            # Sort by date (most recent first)
            all_transcripts.sort(key=lambda x: x['date'], reverse=True)
            
            # Filter out existing
            new_transcripts = [t for t in all_transcripts if t['id'] not in existing_ids]
            print(f"📊 {len(new_transcripts)} new transcripts to process")
            print(f"⏩ {len(all_transcripts) - len(new_transcripts)} already in database\n")
            
            if not new_transcripts:
                print("✅ All transcripts are already synced!")
                if continuous:
                    print(f"\n⏰ Waiting {interval_minutes} minutes until next sync...")
                    time.sleep(interval_minutes * 60)
                    continue
                else:
                    return
            
            # Process new transcripts
            processed = 0
            skipped = 0
            errors = 0
            
            for i, transcript_summary in enumerate(new_transcripts, 1):
                if not keep_running:
                    print("\n⚠️  Stopping sync...")
                    break
                    
                transcript_id = transcript_summary["id"]
                title = transcript_summary["title"]
                date = datetime.fromtimestamp(transcript_summary["date"] / 1000).strftime("%Y-%m-%d")
                
                print(f"\n{'='*60}")
                print(f"🔄 [{i}/{len(new_transcripts)}] Processing: {title}")
                print(f"   📅 Date: {date}")
                print(f"   🆔 ID: {transcript_id}")
                
                try:
                    # Fetch full transcript
                    print("   📥 Fetching full transcript...")
                    full_transcript = fireflies.fetch_transcript_detail(transcript_id)
                    
                    # Show stats
                    duration = full_transcript.get("duration", 0)
                    participants = full_transcript.get("participants", [])
                    sentences = full_transcript.get("sentences", []) or []
                    
                    print(f"   📊 Duration: {duration:.1f} minutes")
                    print(f"   👥 Participants: {len(participants) if participants else 0}")
                    print(f"   💬 Sentences: {len(sentences) if sentences else 0}")
                    
                    # Convert to markdown
                    print("   📝 Converting to markdown...")
                    filepath, markdown_text = converter.save_markdown(full_transcript)
                    print(f"   ✅ Saved: {os.path.basename(filepath)}")
                    
                    # Upload to Supabase
                    print("   ☁️  Uploading to Supabase...")
                    success = uploader.process_and_store(full_transcript, markdown_text, filepath)
                    
                    if success:
                        processed += 1
                        print("   ✅ Successfully processed!")
                    else:
                        skipped += 1
                        print("   ⏩ Skipped (already exists)")
                    
                    # Rate limiting
                    if i % 5 == 0 and i < len(new_transcripts):
                        print("\n⏸️  Rate limit pause (2 seconds)...")
                        time.sleep(2)
                        
                except KeyboardInterrupt:
                    keep_running = False
                    break
                    
                except Exception as e:
                    errors += 1
                    print(f"   ❌ Error: {str(e)}")
            
            # Summary
            print(f"\n{'='*60}")
            print(f"📊 Sync Summary:")
            print(f"   ✅ Processed: {processed}")
            print(f"   ⏩ Skipped: {skipped}")
            print(f"   ❌ Errors: {errors}")
            print(f"   📋 Total attempted: {len(new_transcripts)}")
            
            # Verify totals
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            supabase = create_client(supabase_url, supabase_key)
            
            meetings_count = supabase.table("meetings").select("id", count="exact").execute()
            chunks_count = supabase.table("meeting_chunks").select("id", count="exact").execute()
            
            print(f"\n📊 Database totals:")
            print(f"   Meetings: {meetings_count.count}")
            print(f"   Chunks: {chunks_count.count}")
            
            completion_rate = (meetings_count.count / len(all_transcripts) * 100) if all_transcripts else 100
            print(f"   Sync completion: {completion_rate:.1f}%")
            
        except Exception as e:
            print(f"\n❌ Sync error: {str(e)}")
            
        if continuous and keep_running:
            print(f"\n⏰ Next sync in {interval_minutes} minutes...")
            print("   Press Ctrl+C to stop")
            
            # Sleep in small increments to respond to shutdown signals
            for _ in range(interval_minutes * 60):
                if not keep_running:
                    break
                time.sleep(1)
        else:
            break
    
    print("\n✅ Sync complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync Fireflies transcripts to Supabase')
    parser.add_argument('--continuous', '-c', action='store_true', 
                        help='Run continuously every interval minutes')
    parser.add_argument('--interval', '-i', type=int, default=30,
                        help='Minutes between syncs in continuous mode (default: 30)')
    parser.add_argument('--once', action='store_true', default=True,
                        help='Run once and exit (default)')
    
    args = parser.parse_args()
    
    if args.continuous:
        print(f"🔄 Starting continuous sync (every {args.interval} minutes)")
        print("   Press Ctrl+C to stop gracefully")
        sync_all_transcripts(continuous=True, interval_minutes=args.interval)
    else:
        print("🚀 Starting one-time sync of ALL transcripts")
        sync_all_transcripts(continuous=False)