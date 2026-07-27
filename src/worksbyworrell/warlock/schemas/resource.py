from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ResourceSchema(BaseModel):
    resource_id: str = Field(..., pattern=r"^[a-z0-9-_]+$")
    name: str = Field(..., min_length=1)
    system_prompt: str
    metadata: Optional[Dict[str, Any]] = None
