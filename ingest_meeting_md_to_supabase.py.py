import os
import json
import uuid
import time
import tiktoken
from datetime import datetime, timezone
from pathlib import Path
from supabase import create_client, Client
from openai import OpenAI

# === ENV CONFIG ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

TRANSCRIPT_DIR = Path("transcripts")
BUCKET_NAME = "meetings"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
EMBED_MODEL = "text-embedding-3-small"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
tokenizer = tiktoken.encoding_for_model(EMBED_MODEL)

# === HELPERS ===

def chunk_text(text: str):
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append((start, end, chunk_text))
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

def embed_chunk(text: str):
    for _ in range(3):
        try:
            res = client.embeddings.create(
                model=EMBED_MODEL,
                input=text
            )
            return res.data[0].embedding
        except Exception as e:
            print(f"Retrying embedding: {e}")
            time.sleep(1)
    raise RuntimeError("Embedding failed after 3 attempts")

def build_public_url(filename: str):
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{filename}"

def ingest_markdown_file(file_path: Path):
    title = file_path.stem
    metadata_id = str(uuid.uuid4())
    content = file_path.read_text(encoding="utf-8")

    # Insert into document_metadata
    metadata_insert = {
        "id": metadata_id,
        "title": title,
        "url": build_public_url(file_path.name),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    supabase.table("document_metadata").insert(metadata_insert).execute()
    print(f"📝 Inserted metadata for {title}")

    # Chunk and embed
    chunks = chunk_text(content)
    for i, (start, end, chunk) in enumerate(chunks):
        embedding = embed_chunk(chunk)
        metadata = {
            "loc": {"from": start, "to": end},
            "file": file_path.name,
            "chunk_index": i,
            "metadata_id": metadata_id
        }

        doc_insert = {
            "title": title,
            "content": chunk,
            "metadata": json.dumps(metadata),
            "embedding": embedding,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        supabase.table("documents").insert(doc_insert).execute()

    print(f"✅ Inserted {len(chunks)} chunks for {title}")

def run_ingestion():
    if not TRANSCRIPT_DIR.exists():
        print(f"❌ Folder not found: {TRANSCRIPT_DIR}")
        return

    files = list(TRANSCRIPT_DIR.glob("*.md"))
    if not files:
        print("❌ No .md files found in transcripts/")
        return

    for file in files:
        try:
            ingest_markdown_file(file)
        except Exception as e:
            print(f"⚠️ Error processing {file.name}: {e}")

if __name__ == "__main__":
    run_ingestion()