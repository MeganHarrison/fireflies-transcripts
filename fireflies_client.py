"""
Fireflies API client for fetching meeting transcripts.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class FirefliesClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("FIREFLIES_API_KEY")
        self.base_url = "https://api.fireflies.ai/graphql"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def fetch_transcripts(self, limit=25, skip=0):
        """Fetch list of transcript metadata with pagination support."""
        query = """
        query GetTranscripts($limit: Int, $skip: Int) {
            transcripts(limit: $limit, skip: $skip) {
                id title date
            }
        }
        """
        res = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": query, "variables": {"limit": limit, "skip": skip}},
            timeout=30
        )
        res.raise_for_status()
        return res.json()["data"]["transcripts"]
    
    def fetch_all_transcripts_paginated(self, batch_size=50):
        """Fetch ALL transcripts using pagination."""
        all_transcripts = []
        skip = 0
        
        print("   Using pagination to fetch all transcripts...")
        
        while True:
            print(f"   Fetching batch: skip={skip}, limit={batch_size}...", end="")
            try:
                batch = self.fetch_transcripts(limit=batch_size, skip=skip)
                
                if not batch:
                    print(" (empty batch, done)")
                    break
                
                print(f" ✓ Got {len(batch)} transcripts")
                all_transcripts.extend(batch)
                skip += batch_size
                
                # Show progress
                if skip % 200 == 0 and skip > 0:
                    print(f"   📊 Progress: {len(all_transcripts)} transcripts fetched so far...")
                    
            except Exception as e:
                print(f"\n   ❌ Error at skip={skip}: {str(e)}")
                break
        
        return all_transcripts
    
    def fetch_transcript_detail(self, transcript_id):
        """Fetch full transcript content and metadata."""
        query = """
        query GetTranscriptContent($id: String!) {
            transcript(id: $id) {
                title id transcript_url duration date participants
                sentences { text speaker_id }
            }
        }
        """
        res = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": query, "variables": {"id": transcript_id}},
            timeout=30
        )
        res.raise_for_status()
        
        # Validate response structure
        data = res.json()
        if not data or "data" not in data:
            raise ValueError(f"Invalid API response for transcript {transcript_id}")
        
        transcript = data["data"].get("transcript")
        if not transcript:
            raise ValueError(f"No transcript data found for ID {transcript_id}")
        
        # Ensure lists are always lists (handle None case)
        if transcript.get("sentences") is None:
            transcript["sentences"] = []
        if transcript.get("participants") is None:
            transcript["participants"] = []
        
        return transcript