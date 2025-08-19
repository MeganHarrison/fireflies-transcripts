#!/usr/bin/env python3
"""Minimal test of sync functionality"""
import os
import sys
from dotenv import load_dotenv

print("Loading environment...")
load_dotenv()

print("Environment loaded, importing modules...")

# Don't use relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Importing FirefliesClient...")
from fireflies_client import FirefliesClient

print("Creating client...")
client = FirefliesClient()

print("Testing fetch...")
try:
    transcripts = client.fetch_transcripts(limit=1)
    print(f"Success! Got {len(transcripts)} transcripts")
except Exception as e:
    print(f"Error: {e}")

print("Done!")