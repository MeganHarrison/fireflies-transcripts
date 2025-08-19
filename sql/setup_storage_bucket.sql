-- Create storage bucket for Fireflies transcripts
-- Run this in Supabase SQL Editor

-- Create the storage bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public)
VALUES ('fireflies-transcripts', 'fireflies-transcripts', false)
ON CONFLICT (id) DO NOTHING;

-- Set up RLS policies for the bucket (service role only)
CREATE POLICY "Service role can upload to fireflies-transcripts" 
ON storage.objects FOR INSERT 
TO service_role
WITH CHECK (bucket_id = 'fireflies-transcripts');

CREATE POLICY "Service role can update fireflies-transcripts" 
ON storage.objects FOR UPDATE 
TO service_role
USING (bucket_id = 'fireflies-transcripts');

CREATE POLICY "Service role can delete from fireflies-transcripts" 
ON storage.objects FOR DELETE 
TO service_role
USING (bucket_id = 'fireflies-transcripts');

CREATE POLICY "Authenticated users can read fireflies-transcripts" 
ON storage.objects FOR SELECT 
TO authenticated
USING (bucket_id = 'fireflies-transcripts');

-- Verify bucket was created
SELECT 'Storage bucket "fireflies-transcripts" is ready!' as message;