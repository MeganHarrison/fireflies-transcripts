import requests
import json
import os
from datetime import datetime, timedelta
import time

class FirefliesDownloader:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.fireflies.ai/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_transcript_content(self, transcript_id):
        """
        Fetch detailed content for a specific transcript
        """
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
                }
                summary {
                    keywords
                    action_items
                }
            }
        }
        """
        
        variables = {
            "id": transcript_id
        }
        
        try:
            print(f"Fetching content for transcript {transcript_id}...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": variables}
            )
            
            if response.status_code != 200:
                print(f"Error getting transcript content: {response.status_code}")
                print(response.text)
                return None
                
            data = response.json()
            if "errors" in data:
                print("API returned errors:", json.dumps(data["errors"], indent=2))
                return None
                
            return data["data"]["transcript"]
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transcript content: {e}")
            return None

    def get_transcripts(self, limit=25, to_date=None):
        """
        Fetch list of transcripts with date filtering
        """
        query = """
        query GetTranscripts($limit: Int, $toDate: DateTime) {
            transcripts(limit: $limit, toDate: $toDate) {
                title
                id
                transcript_url
                duration
                date
                participants
            }
        }
        """
        
        variables = {
            "limit": min(limit, 25),
            "toDate": to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z") if to_date else None
        }
        
        try:
            print(f"Making API request for transcripts up to date {to_date if to_date else 'now'}...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": variables}
            )
            
            data = response.json()
            if "errors" in data:
                print("API returned errors:", json.dumps(data["errors"], indent=2))
                return None
                
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transcripts: {e}")
            return None

    def save_transcripts(self, output_dir="transcripts", to_date=None):
        """
        Save all transcripts with their content
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Get existing transcripts to avoid duplicates
        existing_files = set()
        existing_ids = set()
        for filename in os.listdir(output_dir):
            if filename.endswith('.json'):
                existing_files.add(filename)
                try:
                    with open(os.path.join(output_dir, filename)) as f:
                        data = json.load(f)
                        existing_ids.add(data['id'])
                except:
                    pass
        
        last_date = to_date or datetime.now()
        while True:
            result = self.get_transcripts(limit=25, to_date=last_date)
            if not result or "data" not in result or "transcripts" not in result["data"]:
                print("No more transcripts found or error in API response")
                break
                
            transcripts = result["data"]["transcripts"]
            if not transcripts:
                print("No more transcripts found")
                break
                
            print(f"\nFound {len(transcripts)} transcripts")
            
            earliest_date = None
            for transcript in transcripts:
                # Skip if we already have this transcript
                if transcript['id'] in existing_ids:
                    print(f"Skipping existing transcript: {transcript['title']}")
                    continue
                
                print(f"\nProcessing: {transcript['title']}")
                
                # Get detailed content
                content = self.get_transcript_content(transcript['id'])
                if content:
                    transcript = content  # Replace with full content
                
                # Save the file
                date_obj = datetime.fromtimestamp(int(transcript["date"]) / 1000)
                safe_title = ''.join(c for c in transcript['title'] if c.isalnum() or c in (' ', '-', '_', '.'))
                filename = f"{date_obj.strftime('%Y-%m-%d')}_{safe_title[:50]}.json"
                
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(transcript, f, indent=2, ensure_ascii=False)
                
                print(f"Saved transcript: {filename}")
                
                # Track earliest date we've seen
                if earliest_date is None or date_obj < earliest_date:
                    earliest_date = date_obj
                
                time.sleep(1)  # Be nice to the API
            
            if earliest_date:
                # Subtract 1 second to avoid getting the same transcript again
                last_date = earliest_date - timedelta(seconds=1)
                time.sleep(1)  # Extra pause between batches
            else:
                break

def main():
    api_key = os.getenv("FIREFLIES_API_KEY")
    if not api_key:
        print("Please set your FIREFLIES_API_KEY environment variable")
        return
    
    print(f"Using API key: {api_key[:5]}...{api_key[-5:]}")
    
    # Find the earliest date from existing files
    earliest_date = None
    if os.path.exists("transcripts"):
        files = os.listdir("transcripts")
        if files:
            try:
                for file in files:
                    if file.endswith('.json'):
                        with open(os.path.join("transcripts", file)) as f:
                            data = json.load(f)
                            date = datetime.fromtimestamp(int(data["date"]) / 1000)
                            if earliest_date is None or date < earliest_date:
                                earliest_date = date
                
                if earliest_date:
                    print(f"Starting from before date: {earliest_date}")
            except Exception as e:
                print(f"Error reading files: {e}")
    
    downloader = FirefliesDownloader(api_key)
    downloader.save_transcripts(to_date=earliest_date)

if __name__ == "__main__":
    main()