import requests
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import re

class FirefliesMarkdownDownloader:
    def __init__(self, api_key, output_dir="fireflies_markdown"):
        self.api_key = api_key
        self.base_url = "https://api.fireflies.ai/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def gql(self, query, variables):
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": query, "variables": variables}
        )
        response.raise_for_status()
        result = response.json()
        if "errors" in result:
            raise RuntimeError(result["errors"])
        return result["data"]

    def get_transcripts(self, to_date=None, limit=25):
        query = """
        query GetTranscripts($limit: Int, $toDate: DateTime) {
            transcripts(limit: $limit, toDate: $toDate) {
                id title date
            }
        }
        """
        variables = {
            "limit": min(limit, 25),
            "toDate": to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z") if to_date else None
        }
        return self.gql(query, variables)["transcripts"]

    def get_transcript_content(self, transcript_id):
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
                }
            }
        }
        """
        return self.gql(query, {"id": transcript_id})["transcript"]

    def clean_filename(self, name):
        return re.sub(r"[^\w\s.-]", "_", name).strip()

    def save_as_markdown(self, transcript):
        # Extract metadata
        title = transcript.get("title", "Untitled").strip()
        meeting_id = transcript["id"]
        url = transcript.get("transcript_url", "")
        duration = transcript.get("duration", 0)
        date_ts = transcript.get("date", 0)
        date_str = datetime.utcfromtimestamp(date_ts / 1000).strftime("%Y-%m-%d")
        participants = transcript.get("participants", [])[1:] if len(transcript.get("participants", [])) > 1 else []
        speaker_map = {i: email.split("@")[0].capitalize() for i, email in enumerate(participants)}

        # Markdown header
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

        # Body
        for sentence in transcript.get("sentences", []):
            speaker = speaker_map.get(sentence["speaker_id"], f"Speaker {sentence['speaker_id']}")
            lines.append(f"**{speaker}**: {sentence['text']}")

        # Save .md file
        safe_title = self.clean_filename(title)
        filename = f"{date_str} - {safe_title[:50]}.md"
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"✅ Saved: {filename}")

    def run(self):
        seen_ids = {p.stem.split("_")[-1] for p in self.output_dir.glob("*.md")}
        last_date = datetime.now()

        while True:
            transcripts = self.get_transcripts(to_date=last_date)
            if not transcripts:
                break

            earliest = None
            for t in transcripts:
                tid = t["id"]
                if tid in seen_ids:
                    continue

                full = self.get_transcript_content(tid)
                self.save_as_markdown(full)

                date_obj = datetime.utcfromtimestamp(full["date"] / 1000)
                if earliest is None or date_obj < earliest:
                    earliest = date_obj

                time.sleep(1)

            if not earliest:
                break
            last_date = earliest - timedelta(seconds=1)

# Run it
if __name__ == "__main__":
    api_key = os.getenv("FIREFLIES_API_KEY")
    if not api_key:
        print("❌ Please set FIREFLIES_API_KEY environment variable")
    else:
        FirefliesMarkdownDownloader(api_key).run()