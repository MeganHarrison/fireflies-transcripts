"""
Convert Fireflies transcript JSON to Markdown format.
"""
import re
from datetime import datetime
from pathlib import Path


class MarkdownConverter:
    def __init__(self, output_dir="transcripts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    @staticmethod
    def sanitize_filename(filename):
        """Replace problematic characters in filenames."""
        return re.sub(r'[\\/:"*?<>|]+', '-', filename)
    
    def to_markdown(self, transcript):
        """Convert transcript JSON to Markdown format."""
        title = transcript["title"].strip()
        meeting_id = transcript["id"]
        duration = transcript.get("duration", 0)
        date_str = datetime.fromtimestamp(transcript["date"] / 1000).strftime("%Y-%m-%d")
        url = transcript["transcript_url"]
        participants = transcript.get("participants", [])[1:]  # Skip first participant (often system)
        
        # Create speaker mapping
        speaker_map = {
            i: email.split("@")[0].capitalize() 
            for i, email in enumerate(participants)
        }
        
        # Build markdown content
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
        
        # Add transcript sentences
        sentences = transcript.get("sentences") or []
        for sentence in sentences:
            # Validate sentence structure
            if not sentence or not isinstance(sentence, dict):
                continue
            
            speaker_id = sentence.get("speaker_id", 0)
            text = sentence.get("text", "")
            
            speaker = speaker_map.get(
                speaker_id, 
                f"Speaker {speaker_id}"
            )
            lines.append(f"**{speaker}**: {text}")
        
        # Generate safe filename
        safe_filename = self.sanitize_filename(f"{date_str} - {title[:60]}.md")
        
        return "\n".join(lines), safe_filename
    
    def save_markdown(self, transcript):
        """Convert transcript to markdown and save to file."""
        md_text, filename = self.to_markdown(transcript)
        filepath = self.output_dir / filename
        filepath.write_text(md_text, encoding="utf-8")
        return filepath, md_text