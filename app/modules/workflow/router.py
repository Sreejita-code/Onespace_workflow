from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.modules.auth.dependencies import require_admin
from app.modules.auth.models import AdminDoc
from app.modules.workflow import service
from app.modules.workflow.models import WorkflowDefinition, WorkflowDoc

router = APIRouter(tags=["Workflows"])

class BuildRequest(BaseModel):
    set_id: str
    description: str

@router.post("/build", response_model=WorkflowDefinition)
async def build_draft(
    request: BuildRequest, 
    admin: AdminDoc = Depends(require_admin)
):
    try:
        draft = await service.generate_draft(request.set_id, request.description)
        return draft
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/", response_model=WorkflowDoc)
async def publish_workflow(
    definition: WorkflowDefinition, 
    admin: AdminDoc = Depends(require_admin)
):
    return await service.save_workflow(admin.id, definition)

@router.get("/", response_model=list[WorkflowDoc])
async def list_workflows(admin: AdminDoc = Depends(require_admin)):
    return await service.get_all_active()