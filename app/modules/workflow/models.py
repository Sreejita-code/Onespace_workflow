from datetime import datetime
from typing import Literal
from beanie import Document, PydanticObjectId, Indexed
from pydantic import BaseModel, Field

class SlotSchema(BaseModel):
    name: str
    type: Literal["text", "date", "enum"]
    prompt: str
    values: list[str] | None = None

class StepSchema(BaseModel):
    id: str
    name: str
    method: str
    url: str
    params: dict | None = None
    body: dict | None = None
    condition: str | None = None
    condition_fail_message: str | None = None
    output_map: dict[str, str] = {}

class WorkflowDefinition(BaseModel):
    name: str
    triggers: list[str]
    slots: list[SlotSchema]
    steps: list[StepSchema]
    response_template: str
    summary: str

class WorkflowDoc(Document):
    definition: WorkflowDefinition
    admin_id: PydanticObjectId
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "workflows"
        # We index is_active for fast filtering
        indexes = ["is_active"]