from datetime import datetime
from beanie import Document, Indexed
from pydantic import Field

class AdminDoc(Document):
    email: Indexed(str, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "admins"