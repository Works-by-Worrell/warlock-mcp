import logging
from typing import Any, Dict

from pydantic import ValidationError

from worksbyworrell.warlock.schemas.agent import AgentConfigSchema, AgentOverlaySchema
from worksbyworrell.warlock.schemas.profile import UserProfileSchema
from worksbyworrell.warlock.schemas.resource import ResourceSchema
from worksbyworrell.warlock.schemas.skill import SkillMetadataSchema

logger = logging.getLogger(__name__)


def validate_agent_config(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        model = AgentConfigSchema(**data)
        return model.model_dump()
    except ValidationError:
        logger.exception("Validation failed for AgentConfigSchema")
        raise


def validate_agent_overlay(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        model = AgentOverlaySchema(**data)
        return model.model_dump()
    except ValidationError:
        logger.exception("Validation failed for AgentOverlaySchema")
        raise


def validate_user_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        model = UserProfileSchema(**data)
        return model.model_dump()
    except ValidationError:
        logger.exception("Validation failed for UserProfileSchema")
        raise


def validate_system_resource(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        model = ResourceSchema(**data)
        return model.model_dump()
    except ValidationError:
        logger.exception("Validation failed for SystemResourceSchema")
        raise


def validate_skill_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        model = SkillMetadataSchema(**data)
        return model.model_dump()
    except ValidationError:
        logger.exception("Validation failed for SkillMetadataSchema")
        raise
