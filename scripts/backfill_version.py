#!/usr/bin/env python3
"""
backfill_version.py — Set version="1.0.0" on any plugin document missing the field.
Run once after deploying the version field. Safe to re-run (skips docs that already have it).

Usage:
    python scripts/backfill_version.py [service-account.json]
    or set FIREBASE_SERVICE_ACCOUNT_JSON env var with the JSON content.
"""
import json
import os
import sys
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore


def main():
    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        sa_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
        if sa_path and sa_path.exists():
            sa_json = sa_path.read_text()
        else:
            print("Usage: backfill_version.py [service-account.json]", file=sys.stderr)
            print("  or set FIREBASE_SERVICE_ACCOUNT_JSON env var", file=sys.stderr)
            sys.exit(1)
    cred = credentials.Certificate(json.loads(sa_json))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    docs = list(db.collection("plugins").stream())
    updated = skipped = 0
    for doc in docs:
        data = doc.to_dict()
        if "version" not in data:
            doc.reference.set({"version": "1.0.0"}, merge=True)
            print(f"Updated: {doc.id}")
            updated += 1
        else:
            print(f"Skipped (already has version={data['version']}): {doc.id}")
            skipped += 1
    print(f"\nDone: {updated} updated, {skipped} skipped")


if __name__ == "__main__":
    main()
