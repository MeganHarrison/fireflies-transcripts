"""
Supabase integration for storing documents and embeddings.
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


class SupabaseUploader:
    def __init__(self, bucket_name="meetings"):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")
        self.bucket = bucket_name
    
    def upload_to_storage(self, filepath):
        """Upload file to Supabase storage."""
        filepath = Path(filepath)
        with open(filepath, "rb") as f:
            self.supabase.storage.from_(self.bucket).upload(
                filepath.name, 
                f, 
                {"cacheControl": "3600", "upsert": "true"}
            )
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{filepath.name}"
    
    def transcript_already_ingested(self, transcript_id):
        """Check if transcript has already been processed."""
        result = self.supabase.table("document_metadata").select("id").eq("id", transcript_id).execute()
        return bool(result.data)
    
    def chunk_text(self, text, chunk_size=800, overlap=200):
        """Split text into overlapping chunks based on token count."""
        tokens = self.tokenizer.encode(text)
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk = self.tokenizer.decode(tokens[start:end])
            chunks.append((start, end, chunk))
            start += (chunk_size - overlap)
        
        return chunks
    
    def embed_chunk(self, text, retries=3):
        """Generate embedding for text chunk with retry logic."""
        for attempt in range(retries):
            try:
                res = self.openai_client.embeddings.create(
                    model="text-embedding-3-small", 
                    input=text
                )
                return res.data[0].embedding
            except Exception as e:
                if attempt < retries - 1:
                    print(f"Retrying embedding (attempt {attempt + 1}): {e}")
                    time.sleep(1)
                else:
                    raise RuntimeError(f"Embedding failed after {retries} attempts: {e}")
    
    def store_document_metadata(self, transcript_id, title, url):
        """Store document metadata in Supabase."""
        metadata_insert = {
            "id": transcript_id,  # Fireflies transcript ID as primary key
            "title": title,
            "url": url,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self.supabase.table("document_metadata").insert(metadata_insert).execute()
        print(f"📝 Metadata inserted: {title}")
    
    def store_document_chunks(self, transcript_id, title, filename, chunks):
        """Store document chunks with embeddings in Supabase."""
        for i, (start, end, chunk) in enumerate(chunks):
            embedding = self.embed_chunk(chunk)
            
            self.supabase.table("documents").insert({
                "title": title,
                "content": chunk,
                "metadata": json.dumps({
                    "loc": {"from": start, "to": end},
                    "file": filename,
                    "chunk_index": i,
                    "metadata_id": transcript_id
                }),
                "embedding": embedding,
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
        
        print(f"✅ {len(chunks)} chunks stored for {title}")
    
    def process_and_store(self, transcript, markdown_text, filepath):
        """Complete pipeline to store document and its embeddings."""
        transcript_id = transcript["id"]
        title = transcript["title"]
        
        # Check if already processed
        if self.transcript_already_ingested(transcript_id):
            print(f"⏩ Transcript {transcript_id} already ingested.")
            return False
        
        # Upload file to storage
        url = self.upload_to_storage(filepath)
        
        # Store metadata
        self.store_document_metadata(transcript_id, title, url)
        
        # Chunk and store with embeddings
        chunks = self.chunk_text(markdown_text)
        self.store_document_chunks(transcript_id, title, Path(filepath).name, chunks)
        
        return True