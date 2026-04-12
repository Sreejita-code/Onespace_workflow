from beanie import PydanticObjectId
from app.modules.endpoints.models import EndpointSetDoc, EndpointDoc

async def create_empty_set(admin_id: PydanticObjectId, name: str) -> EndpointSetDoc:
    new_set = EndpointSetDoc(admin_id=admin_id, name=name)
    return await new_set.insert()

async def get_set_by_id(set_id: str | PydanticObjectId) -> EndpointSetDoc | None:
    return await EndpointSetDoc.get(set_id)

async def update_set_endpoints(set_doc: EndpointSetDoc, parsed_data: list[dict]) -> EndpointSetDoc:
    # Convert raw dicts to Pydantic models
    endpoints = [EndpointDoc(**data, position=i) for i, data in enumerate(parsed_data)]
    set_doc.endpoints.extend(endpoints)
    return await set_doc.save()
    