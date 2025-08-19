"""
Adapter for the existing meetings table schema.
Works with the current schema while the full migration happens.
"""
import os
import json
import time
import tiktoken
from datetime import datetime, timezone
from pathlib import Path
from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()


class SupabaseUploaderAdapter:
    """Adapter that works with the existing meetings table schema"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")
        self.bucket = "meetings"  # Use existing bucket
    
    def ensure_storage_bucket(self):
        """Ensure the storage bucket exists."""
        try:
            # Try to list the bucket contents to check if it exists
            self.supabase.storage.from_(self.bucket).list()
            print(f"✅ Storage bucket '{self.bucket}' exists")
        except Exception as e:
            if "Bucket not found" in str(e):
                print(f"⚠️  Creating storage bucket '{self.bucket}'...")
                # The bucket should already exist based on existing code
            else:
                print(f"⚠️  Storage bucket check: {e}")
    
    def upload_to_storage(self, filepath):
        """Upload file to Supabase storage."""
        filepath = Path(filepath)
        
        with open(filepath, "rb") as f:
            self.supabase.storage.from_(self.bucket).upload(
                filepath.name, 
                f, 
                {"cacheControl": "3600", "upsert": "true"}
            )
        
        # Return full URL as expected by existing schema
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{filepath.name}"
    
    def meeting_already_exists(self, title, date):
        """Check if meeting already exists by title and date."""
        # Convert date to match database format
        meeting_date = datetime.fromtimestamp(date / 1000, tz=timezone.utc)
        
        result = self.supabase.table("meetings").select("id").eq("title", title).eq("date", meeting_date.isoformat()).execute()
        return bool(result.data)
    
    def store_meeting(self, transcript, storage_url):
        """Store meeting in the existing schema format."""
        title = transcript["title"]
        
        # Convert date from milliseconds to datetime
        meeting_date = datetime.fromtimestamp(transcript["date"] / 1000, tz=timezone.utc)
        
        # Find or create project (simplified for now)
        project_id = None
        projects = self.supabase.table("projects").select("id").limit(1).execute()
        if projects.data:
            project_id = projects.data[0]["id"]
        
        meeting_data = {
            "title": title,
            "date": meeting_date.isoformat(),
            "project_id": project_id,
            "participants": transcript.get("participants", []),
            "transcript_url": storage_url,
            "storage_bucket_path": storage_url.split("/")[-1],  # Just filename
            "raw_metadata": {
                "fireflies_id": transcript["id"],
                "duration": transcript.get("duration", 0),
                "original_url": transcript.get("transcript_url"),
                "speaker_count": len(transcript.get("participants", []))
            }
        }
        
        result = self.supabase.table("meetings").insert(meeting_data).execute()
        meeting_id = result.data[0]["id"]
        
        print(f"📝 Meeting stored: {title} (ID: {meeting_id[:8]}...)")
        
        return meeting_id, project_id
    
    def chunk_text(self, text, chunk_size=800, overlap=200):
        """Simple text chunking."""
        tokens = self.tokenizer.encode(text)
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk = self.tokenizer.decode(tokens[start:end])
            chunks.append((start, end, chunk))
            start += (chunk_size - overlap)
        
        return chunks
    
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
                    print(f"   Retrying embedding (attempt {attempt + 1}): {e}")
                    time.sleep(1)
                else:
                    raise RuntimeError(f"Embedding failed after {retries} attempts: {e}")
    
    def store_meeting_chunks(self, meeting_id, project_id, chunks, title):
        """Store meeting chunks in the meeting_chunks table."""
        stored = 0
        
        for i, (start, end, chunk_text) in enumerate(chunks):
            try:
                print(f"   📊 Processing chunk {i+1}/{len(chunks)}...", end="\r")
                embedding = self.embed_text(chunk_text)
                
                chunk_data = {
                    "meeting_id": meeting_id,
                    "project_id": project_id,
                    "chunk_index": i,
                    "content": chunk_text,
                    "embedding": embedding,
                    "metadata": json.dumps({
                        "token_range": {"start": start, "end": end},
                        "chunk_number": i + 1,
                        "total_chunks": len(chunks)
                    })
                }
                
                self.supabase.table("meeting_chunks").insert(chunk_data).execute()
                stored += 1
                
            except Exception as e:
                print(f"\n   ⚠️  Error storing chunk {i}: {str(e)[:100]}")
        
        print(f"\n   ✅ {stored}/{len(chunks)} chunks stored with embeddings")
        return stored > 0
    
    def process_and_store(self, transcript, markdown_text, filepath):
        """Complete pipeline to store meeting and chunks."""
        title = transcript["title"]
        date = transcript["date"]
        
        # Check if already processed
        if self.meeting_already_exists(title, date):
            print(f"   ⏩ Meeting already exists in database")
            return False
        
        try:
            # Upload file to storage
            print("   📤 Uploading to storage...")
            storage_url = self.upload_to_storage(filepath)
            
            # Store meeting metadata
            print("   💾 Storing meeting metadata...")
            meeting_id, project_id = self.store_meeting(transcript, storage_url)
            
            # Chunk and store with embeddings
            print("   🔪 Chunking text...")
            chunks = self.chunk_text(markdown_text)
            print(f"   📊 Created {len(chunks)} chunks")
            
            # Store chunks
            print("   🧮 Generating embeddings and storing chunks...")
            success = self.store_meeting_chunks(meeting_id, project_id, chunks, title)
            
            return success
            
        except Exception as e:
            print(f"   ❌ Pipeline error: {str(e)}")
            raise


# Test the adapter
if __name__ == "__main__":
    adapter = SupabaseUploaderAdapter()
    
    # Test storage bucket
    try:
        adapter.ensure_storage_bucket()
        print("✅ Storage bucket check passed")
    except Exception as e:
        print(f"❌ Storage bucket error: {e}")
    
    # Test database connection
    try:
        result = adapter.supabase.table("meetings").select("id").limit(1).execute()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database error: {e}")