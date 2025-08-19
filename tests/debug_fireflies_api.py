"""
Debug Fireflies API to see what's happening
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

FF_API_KEY = os.getenv("FIREFLIES_API_KEY") or os.getenv("FF_API_KEY")
print(f"API Key: {FF_API_KEY[:10]}...{FF_API_KEY[-10:]}")

# Test the API directly
query = """
query GetTranscripts($limit: Int) {
    transcripts(limit: $limit) {
        id title date
    }
}
"""

response = requests.post(
    "https://api.fireflies.ai/graphql",
    headers={"Authorization": f"Bearer {FF_API_KEY}"},
    json={"query": query, "variables": {"limit": 10}},
)

print(f"\nStatus Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"\nResponse Body:")
print(response.text[:500])

# Try parsing
try:
    data = response.json()
    print(f"\nParsed JSON:")
    print(data)
    
    if "data" in data and "transcripts" in data["data"]:
        transcripts = data["data"]["transcripts"]
        print(f"\nFound {len(transcripts) if transcripts else 0} transcripts")
        if transcripts:
            for t in transcripts[:3]:
                print(f"  - {t['title']}")
except Exception as e:
    print(f"\nError parsing JSON: {e}")