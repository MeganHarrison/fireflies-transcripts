"""
Orchestrator for the Fireflies transcript processing pipeline.
"""
from fireflies_client import FirefliesClient
from markdown_converter import MarkdownConverter
from supabase_uploader import SupabaseUploader


class TranscriptPipeline:
    def __init__(self):
        self.fireflies = FirefliesClient()
        self.converter = MarkdownConverter()
        self.uploader = SupabaseUploader()
    
    def process_single_transcript(self, transcript_id):
        """Process a single transcript through the entire pipeline."""
        try:
            # Fetch full transcript details
            transcript = self.fireflies.fetch_transcript_detail(transcript_id)
            
            # Convert to markdown and save
            filepath, markdown_text = self.converter.save_markdown(transcript)
            
            # Upload to Supabase with embeddings
            success = self.uploader.process_and_store(transcript, markdown_text, filepath)
            
            return success
            
        except Exception as e:
            print(f"❌ Error processing transcript {transcript_id}: {e}")
            raise
    
    def run_pipeline(self, limit=25):
        """Run the pipeline for multiple transcripts."""
        processed = 0
        skipped = 0
        errors = 0
        
        try:
            # Fetch list of transcripts
            transcripts = self.fireflies.fetch_transcripts(limit=limit)
            print(f"📋 Found {len(transcripts)} transcripts to process")
            
            # Process each transcript
            for transcript in transcripts:
                transcript_id = transcript["id"]
                title = transcript["title"]
                
                try:
                    print(f"\n🔄 Processing: {title}")
                    success = self.process_single_transcript(transcript_id)
                    
                    if success:
                        processed += 1
                    else:
                        skipped += 1
                        
                except Exception as e:
                    print(f"❌ Failed to process {title}: {e}")
                    errors += 1
            
            # Summary
            print(f"\n📊 Pipeline Summary:")
            print(f"   - Processed: {processed}")
            print(f"   - Skipped (already exists): {skipped}")
            print(f"   - Errors: {errors}")
            print(f"   - Total: {len(transcripts)}")
            
            return {
                "status": "success",
                "processed": processed,
                "skipped": skipped,
                "errors": errors,
                "total": len(transcripts)
            }
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


if __name__ == "__main__":
    pipeline = TranscriptPipeline()
    pipeline.run_pipeline()