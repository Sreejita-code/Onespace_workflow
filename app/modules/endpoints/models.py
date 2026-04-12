from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

class EndpointDoc(BaseModel):
    method: str
    url: str
    description: str | None = ""
    request_body: dict | None = None
    response_body: dict | None = None
    position: int = 0

class EndpointSetDoc(Document):
    admin_id: PydanticObjectId
    name: str | None = "Untitled Set"
    endpoints: list[EndpointDoc] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "endpoint_sets"