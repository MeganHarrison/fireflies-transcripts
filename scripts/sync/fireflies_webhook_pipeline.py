
import os
import json
import time
import uuid
import tiktoken
import requests
import re
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from openai import OpenAI
from supabase import create_client
import uvicorn

# === Load env from .env ===
load_dotenv()
FF_API_KEY = os.getenv("FIREFLIES_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
print("DEBUG: SUPABASE_URL=", SUPABASE_URL)
print("DEBUG: SUPABASE_SERVICE_ROLE_KEY=", SUPABASE_SERVICE_ROLE_KEY)

client = OpenAI(api_key=OPENAI_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")

TRANSCRIPT_DIR = Path("transcripts")
TRANSCRIPT_DIR.mkdir(exist_ok=True)
BUCKET = "meetings"

app = FastAPI()

# === Fireflies API ===
def fetch_transcripts(limit=25):
    query = """
    query GetTranscripts($limit: Int) {
        transcripts(limit: $limit) {
            id title date
        }
    }
    """
    res = requests.post(
        "https://api.fireflies.ai/graphql",
        headers={"Authorization": f"Bearer {FF_API_KEY}"},
        json={"query": query, "variables": {"limit": limit}},
    )
    res.raise_for_status()
    return res.json()["data"]["transcripts"]

def fetch_transcript_detail(tid):
    query = """
    query GetTranscriptContent($id: String!) {
        transcript(id: $id) {
            title id transcript_url duration date participants
            sentences { text speaker_id }
        }
    }
    """
    res = requests.post(
        "https://api.fireflies.ai/graphql",
        headers={"Authorization": f"Bearer {FF_API_KEY}"},
        json={"query": query, "variables": {"id": tid}},
    )
    res.raise_for_status()
    return res.json()["data"]["transcript"]

# === Markdown Conversion ===
def sanitize_filename(filename):
    # Replace slashes and other problematic characters with a dash
    return re.sub(r'[\\/:"*?<>|]+', '-', filename)

def to_markdown(transcript):
    title = transcript["title"].strip()
    meeting_id = transcript["id"]
    duration = transcript.get("duration", 0)
    date_str = datetime.fromtimestamp(transcript["date"] / 1000).strftime("%Y-%m-%d")
    url = transcript["transcript_url"]
    participants = transcript.get("participants", [])[1:]
    speaker_map = {i: email.split("@")[0].capitalize() for i, email in enumerate(participants)}

    lines = [
        f"# {title}",
        f"**Meeting ID**: {meeting_id}",
        f"**Date**: {date_str}",
        f"**Duration**: {duration} minutes",
        f"**Transcript**: [View Transcript]({url})",
        f"**Participants**: {', '.join(participants)}",
        "",
        "## Transcript"
    ]
    for s in transcript["sentences"] or []:
        speaker = speaker_map.get(s["speaker_id"], f"Speaker {s['speaker_id']}")
        lines.append(f"**{speaker}**: {s['text']}")
    safe_filename = sanitize_filename(f"{date_str} - {title[:60]}.md")
    return "\n".join(lines), safe_filename

# === Supabase Integration ===
def upload_to_storage(filepath):
    with open(filepath, "rb") as f:
        supabase.storage.from_(BUCKET).upload(filepath.name, f, {"cacheControl": "3600", "upsert": "true"})
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filepath.name}"

def transcript_already_ingested(transcript_id):
    result = supabase.table("document_metadata").select("id").eq("id", transcript_id).execute()
    return bool(result.data)

def chunk_text(text):
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + 800, len(tokens))
        chunk = tokenizer.decode(tokens[start:end])
        chunks.append((start, end, chunk))
        start += 600
    return chunks

def embed_chunk(text):
    for _ in range(3):
        try:
            res = client.embeddings.create(model="text-embedding-3-small", input=text)
            return res.data[0].embedding
        except Exception as e:
            print("Retrying embedding:", e)
            time.sleep(1)
    raise RuntimeError("Embedding failed")

def process_transcript(tid):
    if transcript_already_ingested(tid):
        print(f"⏩ Transcript {tid} already ingested.")
        return

    full = fetch_transcript_detail(tid)
    md_text, filename = to_markdown(full)
    md_path = TRANSCRIPT_DIR / filename
    md_path.write_text(md_text, encoding="utf-8")
    url = upload_to_storage(md_path)

    metadata_insert = {
        "id": full["id"],  # Store Fireflies transcript.id as primary key
        "title": full["title"],
        "url": url,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    supabase.table("document_metadata").insert(metadata_insert).execute()
    print(f"📝 Metadata inserted: {filename}")

    chunks = chunk_text(md_text)
    for i, (start, end, chunk) in enumerate(chunks):
        embedding = embed_chunk(chunk)
        supabase.table("documents").insert({
            "title": full["title"],
            "content": chunk,
            "metadata": json.dumps({
                "loc": {"from": start, "to": end},
                "file": filename,
                "chunk_index": i,
                "metadata_id": full["id"]
            }),
            "embedding": embedding,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
    print(f"✅ {len(chunks)} chunks stored for {full['title']}")

# === Webhook + Manual Entry ===
@app.post("/run-fireflies-pipeline")
async def run_fireflies_pipeline(request: Request):
    try:
        transcripts = fetch_transcripts()
        for t in transcripts:
            process_transcript(t["id"])
        return {"status": "success", "message": "Pipeline completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# === CLI Support ===
if __name__ == "__main__":
    import sys
    if "serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        transcripts = fetch_transcripts()
        for t in transcripts:
            process_transcript(t["id"])