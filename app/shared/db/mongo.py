from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.modules.auth.models import AdminDoc # <-- Add this import
from app.modules.endpoints.models import EndpointSetDoc
from app.modules.workflow.models import WorkflowDoc

async def init_db():
    client = AsyncIOMotorClient(settings.mongodb_uri)
    await init_beanie(
        database=client[settings.mongodb_db],
        document_models=[AdminDoc, EndpointSetDoc, WorkflowDoc], # <-- Register the model here
    )
    print("MongoDB Atlas connection established.")