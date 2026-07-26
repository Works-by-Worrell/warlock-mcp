from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class UserProfileSchema(BaseModel):
    username: str = Field(..., pattern=r"^[a-z0-9-_]+$")
    system_prompt: str
    metadata: Optional[Dict[str, Any]] = None
