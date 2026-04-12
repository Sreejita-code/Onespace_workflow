from app.modules.endpoints import repository

async def get_set_by_id(set_id: str):
    return await repository.get_set_by_id(set_id)