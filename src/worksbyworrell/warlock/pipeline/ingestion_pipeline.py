import os
from typing import Any, Callable, Dict

from google.cloud import firestore

from worksbyworrell.warlock.pipeline.crawler import crawl_skills_directory, crawl_standard_directory
from worksbyworrell.warlock.pipeline.normalizer import normalize_keys


class ConfigIngestionPipeline:
    def __init__(self, db: firestore.Client, dry_run: bool = False):
        self.db = db or firestore.Client()
        self.dry_run = dry_run

    @staticmethod
    def calculate_content_hash(data: dict) -> str:
        """Compute MD5 checksum of target payload structure."""
        import hashlib
        import json

        serialized = json.dumps(data, sort_keys=True)
        # noinspection PyTypeChecker
        return hashlib.md5(serialized.encode("utf-8")).hexdigest()

    def _sync_directory(
        self,
        collection_name: str,
        directory_path: str,
        crawler_fn: Callable[[str], Dict[str, Any]],
        validator_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> int:
        raw_docs = crawler_fn(directory_path)
        updated_count = 0

        for doc_id, raw_doc in raw_docs.items():
            normalized_doc = normalize_keys(raw_doc)

            # Dynamically inject identifiers based on the filename
            normalized_doc["agent_id"] = doc_id
            normalized_doc["profile_id"] = doc_id
            normalized_doc["resource_id"] = doc_id

            validated_doc = validator_fn(normalized_doc)
            if self.sync_document(collection_name, doc_id, validated_doc):
                updated_count += 1

        return updated_count

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
        if self.dry_run:
            print(f"[{collection_name}/{doc_id}] Delta found (Dry Run). Skipping Firestore update.")
            return True
        doc_ref.set(payload)
        print(f"[{collection_name}/{doc_id}] Delta found. Firestore updated.")
        return True

    def sync_skills_directory(
        self,
        collection_name: str,
        directory_path: str,
        validator_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> int:
        """
        Crawls, normalizes, validates, and syncs the skills directory.

        Returns the count of skills that were updated (or would have been updated).
        """
        return self._sync_directory(
            collection_name=collection_name,
            directory_path=directory_path,
            crawler_fn=crawl_skills_directory,
            validator_fn=validator_fn,
        )

    def sync_standard_directory(
        self,
        collection_name: str,
        directory_path: str,
        validator_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> int:
        """
        Crawls, normalizes, validates, and syncs the skills directory.

        Returns the count of skills that were updated (or would have been updated).
        """
        return self._sync_directory(
            collection_name=collection_name,
            directory_path=directory_path,
            crawler_fn=crawl_standard_directory,
            validator_fn=validator_fn,
        )
