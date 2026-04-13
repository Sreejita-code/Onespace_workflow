# app/modules/workflow/models.py

from datetime import datetime
from typing import Literal
from beanie import Document, PydanticObjectId, Indexed
from pydantic import BaseModel, Field

class SlotSchema(BaseModel):
    name: str
    type: Literal["text", "date", "enum"]
    prompt: str
    values: list[str] | None = None

class StepTransition(BaseModel):
    """Defines the path to the next node based on a condition."""
    target_id: str
    condition: str | None = None  # e.g., "response.status == 200" or "slots.choice == 'Yes'"

class StepSchema(BaseModel):
    id: str
    name: str
    # Added 'logic' type for if-else branching
    type: Literal["start", "api", "logic", "end"] = "api"
    
    method: str | None = None
    url: str | None = None
    params: dict | None = None
    body: dict | None = None
    
    next_steps: list[StepTransition] = [] 
    output_map: dict[str, str] = {}

    # PERSISTENCE: Stores (x, y) coordinates so the graph doesn't reset on refresh
    position: dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0})
    
    condition_fail_message: str | None = None

class WorkflowDefinition(BaseModel):
    name: str
    triggers: list[str]
    slots: list[SlotSchema]
    # Collection of nodes in a directed graph
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
        indexes = ["is_active"]
