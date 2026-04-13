from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.modules.auth.dependencies import require_admin
from app.modules.auth.models import AdminDoc
from app.modules.workflow import service
from app.modules.workflow.models import WorkflowDefinition, WorkflowDoc, StepSchema

router = APIRouter(tags=["Workflows"])

# --- SCHEMAS ---

class BuildRequest(BaseModel):
    set_id: str
    description: str

# --- ROUTES ---

@router.post("/build", response_model=WorkflowDefinition)
async def build_draft(
    request: BuildRequest, 
    admin: AdminDoc = Depends(require_admin)
):
    """Generate a graph-based workflow draft using AI."""
    try:
        # service.generate_draft now returns the graph-based WorkflowDefinition
        draft = await service.generate_draft(request.set_id, request.description)
        return draft
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/", response_model=WorkflowDoc, status_code=status.HTTP_201_CREATED)
async def publish_workflow(
    definition: WorkflowDefinition, 
    admin: AdminDoc = Depends(require_admin)
):
    """Save a new graph-based workflow definition to the database."""
    return await service.save_workflow(admin.id, definition)


@router.get("/", response_model=list[WorkflowDoc])
async def list_workflows(admin: AdminDoc = Depends(require_admin)):
    """List all active workflows for the admin."""
    return await service.get_all_active()


@router.get("/{workflow_id}", response_model=WorkflowDoc)
async def get_workflow(workflow_id: str, admin: AdminDoc = Depends(require_admin)):
    """Fetch a specific workflow by ID for the editor."""
    workflow = await WorkflowDoc.get(workflow_id)
    if not workflow or workflow.admin_id != admin.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.patch("/{workflow_id}/steps/{step_id}", response_model=WorkflowDoc)
async def edit_step(
    workflow_id: str, 
    step_id: str, 
    updated_step: StepSchema, 
    admin: AdminDoc = Depends(require_admin)
):
    """Modify a specific node (step) or its transitions (next_steps) within the graph."""
    workflow = await WorkflowDoc.get(workflow_id)
    if not workflow or workflow.admin_id != admin.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Find and update the node in the definition
    for i, step in enumerate(workflow.definition.steps):
        if step.id == step_id:
            workflow.definition.steps[i] = updated_step
            workflow.updated_at = datetime.utcnow()
            await workflow.save()
            return workflow
            
    raise HTTPException(status_code=404, detail="Step not found in this workflow")


@router.post("/{workflow_id}/steps", response_model=WorkflowDoc)
async def add_step(
    workflow_id: str, 
    new_step: StepSchema, 
    admin: AdminDoc = Depends(require_admin)
):
    """Manually add a new node (Start, API, or End) to the workflow graph."""
    workflow = await WorkflowDoc.get(workflow_id)
    if not workflow or workflow.admin_id != admin.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Ensure ID uniqueness within the graph
    if any(s.id == new_step.id for s in workflow.definition.steps):
        raise HTTPException(status_code=400, detail="A step with this ID already exists")

    workflow.definition.steps.append(new_step)
    workflow.updated_at = datetime.utcnow()
    await workflow.save()
    return workflow


@router.delete("/{workflow_id}/steps/{step_id}", response_model=WorkflowDoc)
async def delete_step(
    workflow_id: str,
    step_id: str,
    admin: AdminDoc = Depends(require_admin)
):
    """Remove a node from the workflow graph."""
    workflow = await WorkflowDoc.get(workflow_id)
    if not workflow or workflow.admin_id != admin.id:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.definition.steps = [s for s in workflow.definition.steps if s.id != step_id]
    workflow.updated_at = datetime.utcnow()
    await workflow.save()
    return workflow
