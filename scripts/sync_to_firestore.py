#!/usr/bin/env python3
"""
sync_to_firestore.py — Full sync of all plugins to Firestore.

Uses merge=True to upsert metadata while leaving stats fields
(installCount, averageRating, ratingCount, ratingSum) untouched.

Environment:
    FIREBASE_SERVICE_ACCOUNT_JSON  — Service account JSON (as a string)

Usage:
    python scripts/sync_to_firestore.py
"""

import json
import os
import sys
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

STATS_FIELDS = {"installCount", "averageRating", "ratingCount", "ratingSum"}
COLLECTION = "plugins"
PLUGINS_DIR = Path(__file__).parent.parent / "plugins"


def init_firebase() -> firestore.Client:
    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        print("ERROR: FIREBASE_SERVICE_ACCOUNT_JSON env var not set", file=sys.stderr)
        sys.exit(1)

    sa_dict = json.loads(sa_json)
    cred = credentials.Certificate(sa_dict)
    firebase_admin.initialize_app(cred)
    return firestore.client()


def find_plugins() -> list[Path]:
    return sorted(PLUGINS_DIR.glob("*/*/plugin.json"))


def load_plugin(path: Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    # Defensively strip stats fields — they must never overwrite Firestore values
    for field in STATS_FIELDS:
        data.pop(field, None)
    return data


def sync(db: firestore.Client, plugins: list[Path]) -> tuple[int, int]:
    """Returns (synced_count, error_count)."""
    synced = 0
    errors = 0

    collection_ref = db.collection(COLLECTION)

    for plugin_path in plugins:
        try:
            data = load_plugin(plugin_path)
            marketplace_id = data.get("marketplaceId")
            if not marketplace_id:
                print(f"ERROR: {plugin_path} missing 'marketplaceId'", file=sys.stderr)
                errors += 1
                continue

            doc_ref = collection_ref.document(marketplace_id)
            doc_ref.set(data, merge=True)
            print(f"Synced: {marketplace_id}")
            synced += 1
        except Exception as e:
            print(f"ERROR syncing {plugin_path}: {e}", file=sys.stderr)
            errors += 1

    return synced, errors


def main():
    print("Initializing Firebase...")
    db = init_firebase()

    plugins = find_plugins()
    print(f"Found {len(plugins)} plugin(s) to sync")

    synced, errors = sync(db, plugins)

    print(f"\nSync complete: {synced} synced, {errors} error(s)")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
