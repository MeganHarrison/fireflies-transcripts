#!/usr/bin/env python3
"""
Main entry point for Fireflies sync pipeline

Usage:
    python3 run_sync.py              # Sync all new transcripts once
    python3 run_sync.py --all        # Sync ALL transcripts (try larger limits)
    python3 run_sync.py --continuous # Run continuously every 30 minutes
    python3 run_sync.py -c -i 60    # Run continuously every 60 minutes
"""
import sys
import argparse

sys.path.append('scripts/sync')

from sync_all_transcripts_enhanced import sync_all_transcripts

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Sync Fireflies transcripts to Supabase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_sync.py                  # One-time sync of new transcripts
  python3 run_sync.py --all            # Fetch ALL available transcripts
  python3 run_sync.py --continuous     # Run every 30 minutes
  python3 run_sync.py -c --interval 60 # Run every 60 minutes
  
Note: Press Ctrl+C to stop continuous mode gracefully.
        """
    )
    
    parser.add_argument('--all', '-a', action='store_true',
                        help='Attempt to fetch ALL transcripts (not just 50)')
    parser.add_argument('--continuous', '-c', action='store_true',
                        help='Run continuously with scheduled syncs')
    parser.add_argument('--interval', '-i', type=int, default=30,
                        help='Minutes between syncs in continuous mode (default: 30)')
    
    args = parser.parse_args()
    
    if args.continuous:
        print(f"🔄 Starting continuous sync (every {args.interval} minutes)")
        print("   Press Ctrl+C to stop gracefully\n")
        sync_all_transcripts(continuous=True, interval_minutes=args.interval)
    else:
        if args.all:
            print("🚀 Starting sync of ALL available transcripts")
            print("   Will try increasing limits to fetch all transcripts\n")
        else:
            print("🚀 Starting one-time sync of new transcripts\n")
        sync_all_transcripts(continuous=False)
