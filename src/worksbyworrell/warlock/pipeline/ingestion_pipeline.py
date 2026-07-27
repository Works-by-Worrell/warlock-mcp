import os

from google.cloud import firestore


class ConfigIngestionPipeline:
    def __init__(self, db: firestore.Client):
        self.db = db or firestore.Client()

    @staticmethod
    def calculate_content_hash(data: dict) -> str:
        """Compute MD5 checksum of target payload structure."""
        import hashlib
        import json

        serialized = json.dumps(data, sort_keys=True)
        # noinspection PyTypeChecker
        return hashlib.md5(serialized.encode("utf-8")).hexdigest()

    def sync_document(self, collection_name: str, doc_id: str, payload: dict) -> bool:
        """Syncs the payload to Firestore only if a change is detected."""
        # 1. Compute checksum of new document representation
        doc_hash = self.calculate_content_hash(payload)
        payload["_md5_hash"] = doc_hash
        payload["_version_hash"] = os.environ.get("GITHUB_SHA", "local-dev")[:7]

        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()

        if doc.exists:
            existing_data = doc.to_dict() or {}
            # If MD5 hashes match, skip write
            if existing_data.get("_md5_hash") == doc_hash:
                print(f"[{collection_name}/{doc_id}] No change detected. Skipping sync.")
                return False

        # If mismatch or new document, update database
        doc_ref.set(payload)
        print(f"[{collection_name}/{doc_id}] Delta found. Firestore updated.")
        return True
