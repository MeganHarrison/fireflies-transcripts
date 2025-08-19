"""
Updated Supabase integration that works with the new schema.
This version:
- Uses the new table structure (meetings, meeting_chunks)
- Uploads to 'fireflies-transcripts' storage bucket
- Links transcripts to projects
- Stores proper metadata
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
import numpy as np

load_dotenv()


class SupabaseUploaderV2:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")
        self.bucket = "fireflies-transcripts"  # Updated bucket name
    
    def ensure_storage_bucket(self):
        """Ensure the storage bucket exists."""
        try:
            # Try to list the bucket contents to check if it exists
            self.supabase.storage.from_(self.bucket).list()
            print(f"✅ Storage bucket '{self.bucket}' exists")
        except Exception as e:
            if "Bucket not found" in str(e):
                print(f"❌ Storage bucket '{self.bucket}' not found. Please create it in Supabase.")
                print("   Run this SQL in Supabase SQL Editor:")
                print(f"   INSERT INTO storage.buckets (id, name, public)")
                print(f"   VALUES ('{self.bucket}', '{self.bucket}', false);")
            raise
    
    def upload_to_storage(self, filepath):
        """Upload file to Supabase storage."""
        filepath = Path(filepath)
        storage_path = f"{datetime.now().strftime('%Y/%m')}/{filepath.name}"
        
        with open(filepath, "rb") as f:
            self.supabase.storage.from_(self.bucket).upload(
                storage_path, 
                f, 
                {"cacheControl": "3600", "upsert": "true"}
            )
        
        # Return the relative path for storage in database
        return storage_path
    
    def meeting_already_exists(self, fireflies_transcript_id):
        """Check if meeting has already been processed."""
        result = self.supabase.table("meetings").select("id").eq("fireflies_transcript_id", fireflies_transcript_id).execute()
        return bool(result.data)
    
    def find_or_create_project(self, transcript):
        """Find existing project or create a new one based on transcript metadata."""
        title = transcript.get("title", "")
        participants = transcript.get("participants", [])
        
        # Try to match by keywords in title
        # This is a simple implementation - you can make it more sophisticated
        keywords = title.lower().split()
        
        # Search for existing projects
        projects = self.supabase.table("projects").select("*").execute()
        
        best_match = None
        best_score = 0
        
        for project in projects.data:
            score = 0
            project_keywords = [kw.lower() for kw in project.get("keywords", [])]
            
            # Check keyword matches
            for keyword in keywords:
                if keyword in project_keywords:
                    score += 1
            
            # Check participant matches
            for participant in participants:
                if participant in project.get("team_members", []):
                    score += 2  # Weight participant matches higher
            
            if score > best_score:
                best_score = score
                best_match = project
        
        # If we found a good match (score > 2), use it
        if best_match and best_score > 2:
            confidence = min(best_score / 10, 1.0)  # Simple confidence calculation
            return best_match["id"], confidence
        
        # Otherwise, create a new project or return None for manual assignment
        # For now, return None to flag for manual review
        return None, 0.0
    
    def store_meeting(self, transcript, storage_path):
        """Store meeting metadata in the meetings table."""
        fireflies_id = transcript["id"]
        title = transcript["title"]
        
        # Convert date from milliseconds to datetime
        meeting_date = datetime.fromtimestamp(transcript["date"] / 1000, tz=timezone.utc)
        
        # Find or create project
        project_id, confidence = self.find_or_create_project(transcript)
        
        meeting_data = {
            "fireflies_transcript_id": fireflies_id,
            "project_id": project_id,
            "title": title,
            "meeting_date": meeting_date.isoformat(),
            "duration_seconds": transcript.get("duration", 0) * 60,  # Convert from minutes
            "participants": json.dumps(transcript.get("participants", [])),
            "storage_bucket_path": storage_path,
            "confidence_score": confidence,
            "needs_review": confidence < 0.7,  # Flag for review if confidence is low
            "raw_metadata": json.dumps({
                "transcript_url": transcript.get("transcript_url"),
                "original_date": transcript.get("date"),
                "speaker_count": len(transcript.get("participants", []))
            })
        }
        
        result = self.supabase.table("meetings").insert(meeting_data).execute()
        meeting_id = result.data[0]["id"]
        
        print(f"📝 Meeting stored: {title} (Project confidence: {confidence:.2f})")
        
        return meeting_id, project_id
    
    def chunk_text_with_metadata(self, text, sentences, chunk_size=800, overlap=200):
        """Split text into overlapping chunks while preserving speaker information."""
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_start_time = 0
        chunk_speakers = set()
        
        for i, sentence in enumerate(sentences):
            sentence_text = sentence.get("text", "")
            speaker_id = sentence.get("speaker_id", 0)
            
            # Estimate tokens (rough approximation)
            sentence_tokens = len(self.tokenizer.encode(sentence_text))
            
            if current_tokens + sentence_tokens > chunk_size and current_chunk:
                # Create chunk
                chunk_text = " ".join([s["text"] for s in current_chunk])
                chunk_end_time = current_chunk[-1].get("start_time", 0) + 10  # Estimate
                
                chunks.append({
                    "text": chunk_text,
                    "speakers": list(chunk_speakers),
                    "start_time": chunk_start_time,
                    "end_time": chunk_end_time,
                    "sentence_count": len(current_chunk)
                })
                
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - 5)  # Keep last 5 sentences
                current_chunk = current_chunk[overlap_start:]
                current_tokens = sum(len(self.tokenizer.encode(s["text"])) for s in current_chunk)
                chunk_speakers = set(s.get("speaker_id", 0) for s in current_chunk)
                if current_chunk:
                    chunk_start_time = current_chunk[0].get("start_time", 0)
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
            chunk_speakers.add(speaker_id)
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = " ".join([s["text"] for s in current_chunk])
            chunk_end_time = current_chunk[-1].get("start_time", 0) + 10
            
            chunks.append({
                "text": chunk_text,
                "speakers": list(chunk_speakers),
                "start_time": chunk_start_time,
                "end_time": chunk_end_time,
                "sentence_count": len(current_chunk)
            })
        
        return chunks
    
    def embed_text(self, text, retries=3):
        """Generate embedding for text with retry logic."""
        for attempt in range(retries):
            try:
                res = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",  # Using ada-002 for 1536 dimensions
                    input=text
                )
                return res.data[0].embedding
            except Exception as e:
                if attempt < retries - 1:
                    print(f"Retrying embedding (attempt {attempt + 1}): {e}")
                    time.sleep(1)
                else:
                    raise RuntimeError(f"Embedding failed after {retries} attempts: {e}")
    
    def store_meeting_chunks(self, meeting_id, project_id, chunks, participants):
        """Store meeting chunks with embeddings in the meeting_chunks table."""
        # Create speaker map
        speaker_map = {i: email.split("@")[0] for i, email in enumerate(participants[1:])}
        
        for i, chunk in enumerate(chunks):
            embedding = self.embed_text(chunk["text"])
            
            # Map speaker IDs to names
            speaker_names = [speaker_map.get(sid, f"Speaker {sid}") for sid in chunk["speakers"]]
            
            chunk_data = {
                "meeting_id": meeting_id,
                "project_id": project_id,
                "chunk_index": i,
                "content": chunk["text"],
                "embedding": embedding,
                "speaker_info": json.dumps({
                    "speakers": speaker_names,
                    "speaker_ids": chunk["speakers"]
                }),
                "start_timestamp": chunk["start_time"],
                "end_timestamp": chunk["end_time"],
                "metadata": json.dumps({
                    "sentence_count": chunk["sentence_count"],
                    "chunk_number": i + 1,
                    "total_chunks": len(chunks)
                })
            }
            
            self.supabase.table("meeting_chunks").insert(chunk_data).execute()
        
        print(f"✅ {len(chunks)} chunks stored with embeddings")
    
    def process_and_store(self, transcript, markdown_text, filepath):
        """Complete pipeline to store meeting and its chunks with embeddings."""
        fireflies_id = transcript["id"]
        title = transcript["title"]
        
        # Check if already processed
        if self.meeting_already_exists(fireflies_id):
            print(f"⏩ Meeting {title} already processed.")
            return False
        
        # Ensure storage bucket exists
        self.ensure_storage_bucket()
        
        # Upload file to storage
        storage_path = self.upload_to_storage(filepath)
        
        # Store meeting metadata
        meeting_id, project_id = self.store_meeting(transcript, storage_path)
        
        # Chunk text with metadata
        sentences = transcript.get("sentences", [])
        participants = transcript.get("participants", [])
        
        if sentences:
            chunks = self.chunk_text_with_metadata(markdown_text, sentences)
        else:
            # Fallback to simple chunking if no sentence data
            simple_chunks = self.chunk_text(markdown_text)
            chunks = [{"text": chunk[2], "speakers": [], "start_time": 0, "end_time": 0, "sentence_count": 0} 
                     for chunk in simple_chunks]
        
        # Store chunks with embeddings
        self.store_meeting_chunks(meeting_id, project_id, chunks, participants)
        
        return True
    
    def chunk_text(self, text, chunk_size=800, overlap=200):
        """Simple text chunking fallback (when no sentence data available)."""
        tokens = self.tokenizer.encode(text)
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk = self.tokenizer.decode(tokens[start:end])
            chunks.append((start, end, chunk))
            start += (chunk_size - overlap)
        
        return chunks


# Quick test function
if __name__ == "__main__":
    uploader = SupabaseUploaderV2()
    
    # Test storage bucket
    try:
        uploader.ensure_storage_bucket()
        print("✅ Storage bucket check passed")
    except Exception as e:
        print(f"❌ Storage bucket error: {e}")
    
    # Test database connection
    try:
        result = uploader.supabase.table("meetings").select("id").limit(1).execute()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database error: {e}")