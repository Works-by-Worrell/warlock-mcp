import argparse
import logging
import os

from google.cloud import firestore

from worksbyworrell.warlock.pipeline.ingestion_pipeline import ConfigIngestionPipeline
from worksbyworrell.warlock.pipeline.validator import (
    validate_agent_config,
    validate_agent_overlay,
    validate_skill_metadata,
    validate_system_resource,
    validate_user_profile,
)

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GitOps Config Ingestion Syncer for Works-by-Worrell"
    )
    parser.add_argument(
        "--public-dir",
        required=True,
        help="Absolute path to the public configuration directory (wbw-config)",
    )
    parser.add_argument(
        "--private-dir",
        help="Absolute path to the private configuration directory overlay (wbw-config-private)",
    )
    parser.add_argument("--project-id", help="Google Cloud Project ID for Firestore authentication")
    parser.add_argument(
        "--github-sha",
        help="The short SHA of the triggering Git commit to inject as version metadata",
    )
    parser.add_argument(
        "--database",
        default="(default)",
        help="The Firestore database name to connect to (e.g., wbw-firestore-nprd)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run validation without persisting changes to Firestore",
    )

    logger.debug("Parsing CLI arguments")
    args = parser.parse_args()

    if args.project_id:
        db = firestore.Client(project=args.project_id, database=args.database)
    else:
        db = firestore.Client(database=args.database)

    if args.github_sha:
        os.environ["GITHUB_SHA"] = args.github_sha

    public_agents_dir = os.path.join(args.public_dir, "agents")
    public_profiles_dir = os.path.join(args.public_dir, "profiles")
    resources_dir = os.path.join(args.public_dir, "resources")
    skills_dir = os.path.join(args.public_dir, "skills")

    pipeline = ConfigIngestionPipeline(db=db, dry_run=args.dry_run)

    if os.path.isdir(public_agents_dir):
        pipeline.sync_standard_directory(
            collection_name="agent_configurations",
            directory_path=public_agents_dir,
            validator_fn=validate_agent_config,
        )

    if os.path.isdir(public_profiles_dir):
        pipeline.sync_standard_directory(
            collection_name="user_profiles",
            directory_path=public_profiles_dir,
            validator_fn=validate_user_profile,
        )

    if os.path.isdir(resources_dir):
        pipeline.sync_standard_directory(
            collection_name="system_resources",
            directory_path=resources_dir,
            validator_fn=validate_system_resource,
        )

    if os.path.isdir(skills_dir):
        pipeline.sync_skills_directory(
            collection_name="skill_metadata",
            directory_path=skills_dir,
            validator_fn=validate_skill_metadata,
        )

    if args.private_dir:
        private_agents_dir = os.path.join(args.private_dir, "agents")
        private_profiles_dir = os.path.join(args.private_dir, "profiles")

        if os.path.isdir(private_agents_dir):
            pipeline.sync_standard_directory(
                collection_name="agent_overlays",
                directory_path=private_agents_dir,
                validator_fn=validate_agent_overlay,
            )

        if os.path.isdir(private_profiles_dir):
            pipeline.sync_standard_directory(
                collection_name="user_profile_overlays",
                directory_path=private_profiles_dir,
                validator_fn=validate_user_profile,
            )
