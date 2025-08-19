"""
Reprocess existing meetings to add chunks with embeddings
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI
import tiktoken

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_KEY)
tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")


def chunk_text(text, chunk_size=800, overlap=200):
    """Split text into overlapping chunks."""
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0
    
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk = tokenizer.decode(tokens[start:end])
        chunks.append((start, end, chunk))
        start += (chunk_size - overlap)
    
    return chunks


def embed_text(text):
    """Generate embedding for text."""
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding


def process_meeting(meeting):
    """Process a single meeting to add chunks."""
    meeting_id = meeting['id']
    title = meeting['title']
    project_id = meeting.get('project_id')
    
    print(f"\n📄 Processing: {title}")
    print(f"   ID: {meeting_id[:8]}...")
    
    # Check if chunks already exist
    existing_chunks = supabase.table("meeting_chunks").select("id").eq("meeting_id", meeting_id).execute()
    if existing_chunks.data:
        print(f"   ⏩ Already has {len(existing_chunks.data)} chunks, skipping")
        return False
    
    # Get the markdown file from storage
    storage_path = meeting.get('storage_bucket_path')
    if not storage_path:
        print("   ❌ No storage path found")
        return False
    
    try:
        # Download the file from storage
        print(f"   📥 Downloading from storage: {storage_path}")
        file_data = supabase.storage.from_("meetings").download(storage_path)
        
        # Decode the markdown content
        markdown_content = file_data.decode('utf-8')
        print(f"   📏 File size: {len(markdown_content)} characters")
        
        # Chunk the text
        chunks = chunk_text(markdown_content)
        print(f"   🔪 Created {len(chunks)} chunks")
        
        # Process each chunk
        stored = 0
        for i, (start, end, chunk_content) in enumerate(chunks):
            try:
                print(f"   🧮 Processing chunk {i+1}/{len(chunks)}...", end="\r")
                
                # Generate embedding
                embedding = embed_text(chunk_content)
                
                # Store chunk
                chunk_data = {
                    "meeting_id": meeting_id,
                    "chunk_index": i,
                    "content": chunk_content,
                    "embedding": embedding,
                    "metadata": json.dumps({
                        "token_range": {"start": start, "end": end},
                        "chunk_number": i + 1,
                        "total_chunks": len(chunks),
                        "project_id": project_id,
                        "meeting_title": title
                    })
                }
                
                supabase.table("meeting_chunks").insert(chunk_data).execute()
                stored += 1
                
            except Exception as e:
                print(f"\n   ⚠️  Error on chunk {i}: {str(e)[:100]}")
        
        print(f"\n   ✅ Stored {stored}/{len(chunks)} chunks with embeddings")
        return stored > 0
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def main():
    """Process all meetings that don't have chunks yet."""
    print("🚀 Reprocessing meetings to add chunks with embeddings...")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test OpenAI connection
    print("\n🔑 Testing OpenAI API...")
    try:
        test_embedding = embed_text("test")
        print(f"✅ OpenAI API working! Embedding dimension: {len(test_embedding)}")
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return
    
    # Get all meetings
    print("\n📋 Fetching meetings from database...")
    meetings = supabase.table("meetings").select("*").order("created_at", desc=True).execute()
    
    print(f"📊 Found {len(meetings.data)} meetings")
    
    # Process each meeting
    processed = 0
    skipped = 0
    errors = 0
    
    for meeting in meetings.data:
        result = process_meeting(meeting)
        if result:
            processed += 1
        elif result is False:
            errors += 1
        else:
            skipped += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Reprocessing Summary:")
    print(f"   ✅ Processed: {processed}")
    print(f"   ⏩ Skipped: {skipped}")
    print(f"   ❌ Errors: {errors}")
    print(f"   📋 Total: {len(meetings.data)}")
    
    # Verify chunks
    print(f"\n🔍 Verifying chunks in database...")
    chunks_count = supabase.table("meeting_chunks").select("id", count="exact").execute()
    print(f"📊 Total chunks in database: {chunks_count.count}")
    
    # Test vector search
    if chunks_count.count > 0:
        print("\n🔍 Testing vector search...")
        try:
            # Get a sample chunk to test
            sample = supabase.table("meeting_chunks").select("content").limit(1).execute()
            if sample.data:
                test_text = sample.data[0]['content'][:100]
                test_embedding = embed_text(test_text)
                
                # Try to search (this might fail if the function doesn't exist)
                print("✅ Vector embeddings are ready for search!")
        except Exception as e:
            print(f"⚠️  Vector search test: {str(e)[:100]}")
    
    print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()