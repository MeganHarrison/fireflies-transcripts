#!/usr/bin/env python3
"""
Sync remaining transcripts with resume capability
Designed to handle 500+ transcripts efficiently
"""
import os
import sys
import time
import signal
from datetime import datetime

# Load environment variables first, before any imports that might also load them
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fireflies_client import FirefliesClient
from markdown_converter import MarkdownConverter
from supabase_uploader_adapter import SupabaseUploaderAdapter
from supabase import create_client

# Global flag for graceful shutdown
keep_running = True

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global keep_running
    print("\n\n⚠️  Shutdown signal received. Finishing current transcript...")
    keep_running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class EfficientSyncUploader(SupabaseUploaderAdapter):
    """Optimized uploader for large-scale sync"""
    
    def __init__(self):
        super().__init__()
        self.processed_count = 0
        self.skip_count = 0
        self.error_count = 0
        
    def embed_text(self, text, retries=2):
        """Generate embedding with fewer retries for speed"""
        for attempt in range(retries):
            try:
                res = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return res.data[0].embedding
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(0.5)
                else:
                    raise RuntimeError(f"Embedding failed: {e}")


def get_synced_ids():
    """Get set of already synced transcript IDs"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    print(f"🔍 Creating Supabase client...")
    supabase = create_client(supabase_url, supabase_key)
    
    print("📋 Loading existing transcript IDs...")
    print("🔍 Fetching meetings from Supabase...")
    meetings = supabase.table("meetings").select("raw_metadata").execute()
    print(f"✅ Fetched {len(meetings.data)} meetings")
    
    existing_ids = set()
    for meeting in meetings.data:
        metadata = meeting.get('raw_metadata', {})
        if metadata is None:
            continue
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


def sync_remaining(start_from=0, batch_size=10):
    """
    Sync remaining transcripts with ability to start from specific index
    
    Args:
        start_from: Index to start from (for resuming)
        batch_size: Number to process before saving progress
    """
    global keep_running
    
    print(f"🚀 Starting sync of remaining transcripts...")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize components
    fireflies = FirefliesClient()
    converter = MarkdownConverter()
    uploader = EfficientSyncUploader()
    
    # Get existing IDs
    existing_ids = get_synced_ids()
    print(f"📊 Found {len(existing_ids)} already synced transcripts\n")
    
    # Fetch all transcripts using pagination
    print("📥 Fetching all transcripts from Fireflies...")
    all_transcripts = fireflies.fetch_all_transcripts_paginated(batch_size=50)
    print(f"✅ Found {len(all_transcripts)} total transcripts\n")
    
    # Sort by date (most recent first)
    all_transcripts.sort(key=lambda x: x['date'], reverse=True)
    
    # Filter out existing
    new_transcripts = []
    for t in all_transcripts:
        if t['id'] not in existing_ids:
            new_transcripts.append(t)
    
    print(f"📊 Summary:")
    print(f"   Total in Fireflies: {len(all_transcripts)}")
    print(f"   Already synced: {len(existing_ids)}")
    print(f"   To be synced: {len(new_transcripts)}")
    
    if start_from > 0:
        print(f"   Starting from index: {start_from}")
        new_transcripts = new_transcripts[start_from:]
    
    if not new_transcripts:
        print("\n✅ All transcripts are already synced!")
        return
    
    print(f"\n🔄 Processing {len(new_transcripts)} transcripts...\n")
    
    # Process in batches
    processed_in_batch = 0
    total_processed = start_from
    
    for i, transcript_summary in enumerate(new_transcripts):
        if not keep_running:
            print("\n⚠️  Stopping sync...")
            break
        
        transcript_id = transcript_summary["id"]
        title = transcript_summary["title"]
        date = datetime.fromtimestamp(transcript_summary["date"] / 1000).strftime("%Y-%m-%d")
        
        current_index = start_from + i + 1
        total_remaining = len(all_transcripts) - len(existing_ids)
        
        print(f"{'='*60}")
        print(f"🔄 [{current_index}/{total_remaining}] {title[:50]}...")
        print(f"   📅 {date} | 🆔 {transcript_id}")
        
        try:
            # Fetch and process
            full_transcript = fireflies.fetch_transcript_detail(transcript_id)
            
            # Quick stats
            duration = full_transcript.get("duration", 0)
            print(f"   ⏱️  {duration:.1f} min", end="")
            
            # Convert and upload
            filepath, markdown_text = converter.save_markdown(full_transcript)
            print(f" | 📝 Saved", end="")
            
            success = uploader.process_and_store(full_transcript, markdown_text, filepath)
            
            if success:
                uploader.processed_count += 1
                print(" | ✅ Uploaded")
            else:
                uploader.skip_count += 1
                print(" | ⏩ Skipped")
            
            processed_in_batch += 1
            total_processed += 1
            
            # Progress checkpoint every batch_size transcripts
            if processed_in_batch >= batch_size:
                print(f"\n📊 Checkpoint: {total_processed} transcripts processed")
                print(f"   Continue from index {total_processed} if interrupted\n")
                processed_in_batch = 0
                
                # Brief pause to avoid rate limits
                time.sleep(1)
                
        except KeyboardInterrupt:
            keep_running = False
            break
            
        except Exception as e:
            uploader.error_count += 1
            print(f" | ❌ Error: {str(e)[:50]}")
            
            # On error, save progress
            if uploader.error_count % 5 == 0:
                print(f"\n⚠️  Multiple errors. Current index: {total_processed}")
                print("   Consider resuming from this index\n")
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"📊 Sync Summary:")
    print(f"   ✅ Processed: {uploader.processed_count}")
    print(f"   ⏩ Skipped: {uploader.skip_count}")
    print(f"   ❌ Errors: {uploader.error_count}")
    print(f"   📍 Last index: {total_processed}")
    
    if total_processed < len(new_transcripts):
        print(f"\n💡 To resume, run:")
        print(f"   python3 sync_remaining_transcripts.py --start {total_processed}")
    
    print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync remaining Fireflies transcripts')
    parser.add_argument('--start', type=int, default=0,
                        help='Index to start from (for resuming)')
    parser.add_argument('--batch', type=int, default=10,
                        help='Number to process before checkpoint (default: 10)')
    
    args = parser.parse_args()
    
    sync_remaining(start_from=args.start, batch_size=args.batch)