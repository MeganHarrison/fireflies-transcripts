#!/usr/bin/env python3
"""
Optimized Fireflies to Supabase Sync Pipeline
Implements best practices for RAG systems
"""

import os
import json
import time
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import re
import tiktoken
import numpy as np
from dotenv import load_dotenv
import requests
from openai import OpenAI
from supabase import create_client
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
class Config:
    # API Keys
    FIREFLIES_API_KEY = os.getenv("FIREFLIES_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    
    # Chunking parameters (optimized for RAG)
    CHUNK_SIZE = 512  # Tokens per chunk (smaller for better precision)
    CHUNK_OVERLAP = 128  # Overlap between chunks
    MIN_CHUNK_SIZE = 100  # Minimum tokens for a chunk
    
    # Embedding model
    EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI's latest
    EMBEDDING_DIMENSION = 1536  # For text-embedding-3-small
    
    # Storage
    STORAGE_BUCKET = "meetings"
    LOCAL_TRANSCRIPT_DIR = Path("transcripts")
    
    # Processing
    BATCH_SIZE = 10  # Process in batches
    MAX_RETRIES = 3
    RETRY_DELAY = 2


class FirefliesClient:
    """Enhanced Fireflies API client"""
    
    def __init__(self):
        self.api_key = Config.FIREFLIES_API_KEY
        self.base_url = "https://api.fireflies.ai/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def fetch_transcript(self, transcript_id: str) -> Optional[Dict]:
        """Fetch detailed transcript with all metadata"""
        query = """
        query GetTranscriptContent($id: String!) {
            transcript(id: $id) {
                title
                id
                transcript_url
                duration
                date
                participants
                sentences {
                    text
                    speaker_id
                    start_time
                    end_time
                }
                summary {
                    keywords
                    action_items
                    outline
                    shorthand_bullet
                    overview
                    notes
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": {"id": transcript_id}}
            )
            response.raise_for_status()
            
            data = response.json()
            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return None
                
            return data["data"]["transcript"]
            
        except Exception as e:
            logger.error(f"Error fetching transcript {transcript_id}: {e}")
            return None


class ChunkingStrategy:
    """Advanced chunking strategy for optimal RAG performance"""
    
    def __init__(self):
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
    
    def create_chunks(
        self, 
        transcript: Dict,
        chunk_size: int = Config.CHUNK_SIZE,
        overlap: int = Config.CHUNK_OVERLAP
    ) -> List[Dict]:
        """
        Create overlapping chunks with rich metadata
        
        Returns chunks with:
        - Text content
        - Speaker information
        - Temporal context
        - Semantic boundaries
        """
        chunks = []
        sentences = transcript.get("sentences", [])
        
        if not sentences:
            return chunks
        
        # Group sentences by semantic boundaries (speaker changes, time gaps)
        semantic_groups = self._group_by_semantics(sentences)
        
        # Create chunks from semantic groups
        current_chunk = {
            "text": "",
            "sentences": [],
            "speakers": set(),
            "start_time": None,
            "end_time": None,
            "tokens": 0
        }
        
        for group in semantic_groups:
            group_text = self._format_group(group)
            group_tokens = len(self.tokenizer.encode(group_text))
            
            # Check if adding this group exceeds chunk size
            if current_chunk["tokens"] + group_tokens > chunk_size and current_chunk["text"]:
                # Save current chunk
                chunks.append(self._finalize_chunk(current_chunk, len(chunks)))
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, overlap)
                current_chunk = {
                    "text": overlap_text,
                    "sentences": [],
                    "speakers": set(),
                    "start_time": group[0]["start_time"],
                    "end_time": None,
                    "tokens": len(self.tokenizer.encode(overlap_text))
                }
            
            # Add group to current chunk
            current_chunk["text"] += group_text + "\n"
            current_chunk["sentences"].extend(group)
            current_chunk["speakers"].update(s.get("speaker_id", 0) for s in group)
            if current_chunk["start_time"] is None:
                current_chunk["start_time"] = group[0].get("start_time", 0)
            current_chunk["end_time"] = group[-1].get("end_time", 0)
            current_chunk["tokens"] += group_tokens
        
        # Don't forget the last chunk
        if current_chunk["text"].strip():
            chunks.append(self._finalize_chunk(current_chunk, len(chunks)))
        
        # Add chunk metadata
        return self._enrich_chunks(chunks, transcript)
    
    def _group_by_semantics(self, sentences: List[Dict]) -> List[List[Dict]]:
        """Group sentences by speaker and temporal proximity"""
        groups = []
        current_group = []
        last_speaker = None
        last_time = 0
        
        for sentence in sentences:
            speaker = sentence.get("speaker_id", 0)
            start_time = sentence.get("start_time", 0)
            
            # New group if speaker changes or large time gap (>5 seconds)
            if (speaker != last_speaker or start_time - last_time > 5000) and current_group:
                groups.append(current_group)
                current_group = []
            
            current_group.append(sentence)
            last_speaker = speaker
            last_time = sentence.get("end_time", start_time)
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _format_group(self, group: List[Dict]) -> str:
        """Format a group of sentences with speaker labels"""
        if not group:
            return ""
        
        speaker_id = group[0].get("speaker_id", 0)
        speaker_label = f"Speaker {speaker_id + 1}"
        
        texts = [s["text"] for s in group if s.get("text")]
        return f"[{speaker_label}]: {' '.join(texts)}"
    
    def _get_overlap_text(self, chunk: Dict, overlap_tokens: int) -> str:
        """Get overlap text from the end of a chunk"""
        if not chunk["text"]:
            return ""
        
        tokens = self.tokenizer.encode(chunk["text"])
        if len(tokens) <= overlap_tokens:
            return chunk["text"]
        
        overlap_tokens_list = tokens[-overlap_tokens:]
        return self.tokenizer.decode(overlap_tokens_list)
    
    def _finalize_chunk(self, chunk: Dict, index: int) -> Dict:
        """Finalize chunk with proper formatting"""
        return {
            "index": index,
            "text": chunk["text"].strip(),
            "speakers": list(chunk["speakers"]),
            "start_time": chunk["start_time"],
            "end_time": chunk["end_time"],
            "token_count": chunk["tokens"]
        }
    
    def _enrich_chunks(self, chunks: List[Dict], transcript: Dict) -> List[Dict]:
        """Add rich metadata to chunks for better retrieval"""
        
        # Extract entities and topics (you could use NER here)
        summary = transcript.get("summary", {})
        keywords = summary.get("keywords", [])
        action_items = summary.get("action_items", [])
        
        for i, chunk in enumerate(chunks):
            # Determine if chunk contains action items
            chunk_lower = chunk["text"].lower()
            has_actions = any(
                keyword in chunk_lower 
                for keyword in ["action", "todo", "will do", "next step", "follow up"]
            )
            
            # Check for decisions
            has_decisions = any(
                keyword in chunk_lower 
                for keyword in ["decided", "agree", "confirm", "approved", "rejected"]
            )
            
            # Calculate importance score (simple heuristic)
            importance = 0.5
            if has_actions:
                importance += 0.2
            if has_decisions:
                importance += 0.2
            if i == 0 or i == len(chunks) - 1:  # Beginning and end often important
                importance += 0.1
            
            # Add metadata
            chunk["metadata"] = {
                "chunk_type": "transcript",
                "position": f"{i+1}/{len(chunks)}",
                "has_action_items": has_actions,
                "has_decisions": has_decisions,
                "importance_score": min(importance, 1.0),
                "keywords": [kw for kw in keywords if kw.lower() in chunk_lower][:5],
                "chunk_overlap": {
                    "previous": Config.CHUNK_OVERLAP if i > 0 else 0,
                    "next": Config.CHUNK_OVERLAP if i < len(chunks) - 1 else 0
                }
            }
        
        return chunks


class SupabaseUploader:
    """Handles all Supabase operations with optimizations"""
    
    def __init__(self):
        self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
        self.openai = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.chunker = ChunkingStrategy()
    
    def process_transcript(self, transcript: Dict) -> bool:
        """
        Complete pipeline to process and store a transcript
        
        Steps:
        1. Check if already processed
        2. Store meeting record
        3. Upload transcript to storage
        4. Create and embed chunks
        5. Generate summaries
        """
        
        transcript_id = transcript["id"]
        
        try:
            # Check if already processed
            existing = self.supabase.table("meetings").select("id").eq("transcript_id", transcript_id).execute()
            if existing.data:
                logger.info(f"Transcript {transcript_id} already processed")
                return False
            
            # 1. Create meeting record
            meeting_id = self._store_meeting(transcript)
            if not meeting_id:
                return False
            
            # 2. Upload transcript to storage
            storage_path = self._upload_to_storage(transcript, meeting_id)
            
            # 3. Create chunks
            chunks = self.chunker.create_chunks(transcript)
            logger.info(f"Created {len(chunks)} chunks for transcript {transcript_id}")
            
            # 4. Generate embeddings and store chunks
            self._store_chunks(meeting_id, chunks)
            
            # 5. Generate and store summaries
            self._generate_summaries(meeting_id, transcript, chunks)
            
            # 6. Mark as processed
            self.supabase.table("meetings").update({
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "storage_bucket_path": storage_path
            }).eq("id", meeting_id).execute()
            
            logger.info(f"Successfully processed transcript {transcript_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing transcript {transcript_id}: {e}")
            return False
    
    def _store_meeting(self, transcript: Dict) -> Optional[str]:
        """Store meeting record in database"""
        
        meeting_date = datetime.fromtimestamp(transcript["date"] / 1000, tz=timezone.utc)
        participants = transcript.get("participants", [])
        
        # Calculate metadata
        sentences = transcript.get("sentences", [])
        word_count = sum(len(s.get("text", "").split()) for s in sentences)
        speaker_count = len(set(s.get("speaker_id", 0) for s in sentences))
        
        meeting_data = {
            "title": transcript["title"],
            "transcript_id": transcript["id"],
            "date": meeting_date.isoformat(),
            "transcript_url": transcript.get("transcript_url"),
            "participants": participants,
            "duration_minutes": transcript.get("duration", 0),
            "word_count": word_count,
            "speaker_count": speaker_count,
            "raw_metadata": {
                "fireflies_id": transcript["id"],
                "summary": transcript.get("summary", {}),
                "participant_count": len(participants)
            },
            "tags": transcript.get("summary", {}).get("keywords", [])[:10]
        }
        
        try:
            result = self.supabase.table("meetings").insert(meeting_data).execute()
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            logger.error(f"Error storing meeting: {e}")
            return None
    
    def _upload_to_storage(self, transcript: Dict, meeting_id: str) -> str:
        """Upload transcript as markdown to storage bucket"""
        
        # Convert to markdown
        markdown = self._convert_to_markdown(transcript)
        
        # Create filename
        date_str = datetime.fromtimestamp(transcript["date"] / 1000).strftime("%Y-%m-%d")
        safe_title = re.sub(r'[^\w\s-]', '', transcript["title"])[:50]
        filename = f"{date_str}_{safe_title}_{meeting_id}.md"
        
        # Upload to Supabase storage
        try:
            file_path = f"transcripts/{meeting_id}/{filename}"
            self.supabase.storage.from_(Config.STORAGE_BUCKET).upload(
                file_path,
                markdown.encode('utf-8'),
                {"content-type": "text/markdown"}
            )
            
            logger.info(f"Uploaded transcript to storage: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error uploading to storage: {e}")
            return ""
    
    def _convert_to_markdown(self, transcript: Dict) -> str:
        """Convert transcript to well-formatted markdown"""
        
        date = datetime.fromtimestamp(transcript["date"] / 1000)
        participants = transcript.get("participants", [])
        
        # Build markdown
        md = f"# {transcript['title']}\n\n"
        md += f"**Date:** {date.strftime('%Y-%m-%d %H:%M')}\n"
        md += f"**Duration:** {transcript.get('duration', 0)} minutes\n"
        md += f"**Participants:** {', '.join(participants)}\n\n"
        
        # Add summary if available
        summary = transcript.get("summary", {})
        if summary.get("overview"):
            md += "## Summary\n\n"
            md += f"{summary['overview']}\n\n"
        
        if summary.get("action_items"):
            md += "## Action Items\n\n"
            for item in summary["action_items"]:
                md += f"- {item}\n"
            md += "\n"
        
        if summary.get("keywords"):
            md += f"**Keywords:** {', '.join(summary['keywords'])}\n\n"
        
        # Add transcript
        md += "## Transcript\n\n"
        
        # Create speaker map
        speaker_map = {}
        for i, email in enumerate(participants[1:] if len(participants) > 1 else []):
            name = email.split('@')[0].capitalize()
            speaker_map[i] = name
        
        current_speaker = None
        paragraph = []
        
        for sentence in transcript.get("sentences", []):
            speaker_id = sentence.get("speaker_id", 0)
            speaker = speaker_map.get(speaker_id, f"Speaker {speaker_id + 1}")
            text = sentence.get("text", "").strip()
            
            if not text:
                continue
            
            if speaker != current_speaker:
                if paragraph:
                    md += f"**{current_speaker}:** {' '.join(paragraph)}\n\n"
                current_speaker = speaker
                paragraph = [text]
            else:
                paragraph.append(text)
        
        # Don't forget the last paragraph
        if paragraph and current_speaker:
            md += f"**{current_speaker}:** {' '.join(paragraph)}\n\n"
        
        return md
    
    def _store_chunks(self, meeting_id: str, chunks: List[Dict]):
        """Generate embeddings and store chunks"""
        
        batch_size = 10
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Generate embeddings for batch
            texts = [chunk["text"] for chunk in batch]
            embeddings = self._generate_embeddings(texts)
            
            # Store chunks
            for chunk, embedding in zip(batch, embeddings):
                chunk_data = {
                    "meeting_id": meeting_id,
                    "chunk_index": chunk["index"],
                    "chunk_type": chunk["metadata"]["chunk_type"],
                    "content": chunk["text"],
                    "content_tokens": chunk["token_count"],
                    "embedding": embedding,
                    "speaker_info": {
                        "speakers": chunk["speakers"],
                        "speaker_count": len(chunk["speakers"])
                    },
                    "start_timestamp": chunk["start_time"],
                    "end_timestamp": chunk["end_time"],
                    "metadata": chunk["metadata"]
                }
                
                try:
                    self.supabase.table("meeting_chunks").insert(chunk_data).execute()
                except Exception as e:
                    logger.error(f"Error storing chunk {chunk['index']}: {e}")
            
            time.sleep(0.5)  # Rate limiting
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        
        try:
            response = self.openai.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [[0] * Config.EMBEDDING_DIMENSION] * len(texts)
    
    def _generate_summaries(self, meeting_id: str, transcript: Dict, chunks: List[Dict]):
        """Generate and store various summaries"""
        
        # Use existing summary if available
        summary = transcript.get("summary", {})
        
        # Store executive summary
        if summary.get("overview"):
            self._store_summary(
                meeting_id,
                "executive",
                summary["overview"],
                {
                    "keywords": summary.get("keywords", []),
                    "outline": summary.get("outline", [])
                }
            )
        
        # Store action items
        if summary.get("action_items"):
            self._store_summary(
                meeting_id,
                "action_items",
                "\n".join(f"â€¢ {item}" for item in summary["action_items"]),
                {
                    "action_items": summary["action_items"],
                    "count": len(summary["action_items"])
                }
            )
        
        # You could generate additional summaries using GPT-4 here
        # For example: technical summary, decisions made, questions raised
    
    def _store_summary(self, meeting_id: str, summary_type: str, text: str, metadata: Dict):
        """Store a summary in the database"""
        
        summary_data = {
            "meeting_id": meeting_id,
            "summary_type": summary_type,
            "summary_text": text,
            "key_points": metadata.get("key_points", []),
            "action_items": metadata.get("action_items", []),
            "generated_by": "fireflies"
        }
        
        try:
            self.supabase.table("meeting_summaries").insert(summary_data).execute()
        except Exception as e:
            logger.error(f"Error storing summary: {e}")


class SyncPipeline:
    """Main sync pipeline orchestrator"""
    
    def __init__(self):
        self.fireflies = FirefliesClient()
        self.uploader = SupabaseUploader()
    
    def sync_transcript(self, transcript_id: str) -> bool:
        """Sync a single transcript"""
        
        logger.info(f"Syncing transcript: {transcript_id}")
        
        # Fetch from Fireflies
        transcript = self.fireflies.fetch_transcript(transcript_id)
        if not transcript:
            logger.error(f"Failed to fetch transcript {transcript_id}")
            return False
        
        # Process and upload
        return self.uploader.process_transcript(transcript)
    
    def sync_batch(self, transcript_ids: List[str]):
        """Sync a batch of transcripts"""
        
        success_count = 0
        
        for tid in transcript_ids:
            try:
                if self.sync_transcript(tid):
                    success_count += 1
                time.sleep(2)  # Rate limiting
            except Exception as e:
                logger.error(f"Error syncing {tid}: {e}")
        
        logger.info(f"Synced {success_count}/{len(transcript_ids)} transcripts")
        return success_count


# Example usage
if __name__ == "__main__":
    pipeline = SyncPipeline()
    
    # Sync a single transcript
    # pipeline.sync_transcript("your-transcript-id")
    
    # Or sync multiple
    # pipeline.sync_batch(["id1", "id2", "id3"])