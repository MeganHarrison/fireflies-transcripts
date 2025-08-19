#!/usr/bin/env python3
"""
fireflies_bulk_download.py
Bulk‑download every Fireflies.ai transcript (speaker‑by‑speaker text).

Quick start:
    pip install requests
    export FIREFLIES_TOKEN="your-api-key"
    python3 fireflies_bulk_download.py
"""

import os, pathlib, time, requests, re, sys

API_URL = "https://api.fireflies.ai/graphql"
TOKEN = os.getenv("FIREFLIES_TOKEN")
OUT_DIR = pathlib.Path("output")
PAGE_SIZE = 50

if not TOKEN:
    sys.exit("❌  Set FIREFLIES_TOKEN first.")

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

LIST_QUERY = """
query ($skip:Int!, $limit:Int!){
  transcripts(skip:$skip, limit:$limit){
    id title
  }
}
"""

TRANSCRIPT_QUERY = """
query ($id:String!){
  transcript(id:$id){
    sentences{ speaker_name text }
  }
}
"""


def gql(query: str, variables: dict):
    r = requests.post(API_URL,
                      json={
                          "query": query,
                          "variables": variables
                      },
                      headers=HEADERS,
                      timeout=30)
    r.raise_for_status()
    j = r.json()
    if "errors" in j:
        raise RuntimeError(j["errors"])
    return j["data"]


def clean(name: str) -> str:
    return re.sub(r"[^\w\s.-]", "_", name).strip()[:100] or "untitled"


def main():
    OUT_DIR.mkdir(exist_ok=True)
    skip = 0

    while True:
        batch = gql(LIST_QUERY, {
            "skip": skip,
            "limit": PAGE_SIZE
        })["transcripts"]
        if not batch:
            break

        for t in batch:
            tid, title = t["id"], clean(t.get("title") or tid)
            fn = OUT_DIR / f"{title}_{tid}.txt"
            if fn.exists():
                print(f"✔︎  {fn.name} exists; skipping")
                continue

            # ── fetch full transcript, skipping 404s ──────────────
            try:
                sent_data = gql(TRANSCRIPT_QUERY,
                                {"id": tid})["transcript"]["sentences"]
            except RuntimeError as err:
                # Fireflies returns 404 object_not_found when a transcript is missing
                print(f"⚠️  {title}: {err.args[0][0]['message']} – skipped")
                continue

            if not sent_data:
                print(f"⚠️  {title}: no sentence data – skipped")
                continue

            text = "\n".join(f"{s['speaker_name']}: {s['text']}"
                             for s in sent_data)
            fn.write_text(text, encoding="utf-8")
            print(f"⬇︎  saved {fn.name}")
            time.sleep(0.2)
        # ─────────────────────────────────────────────────────────
        skip += PAGE_SIZE

    print(f"\n✅  Done! Transcripts in → {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
