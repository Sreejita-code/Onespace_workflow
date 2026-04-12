from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from app.modules.auth.dependencies import require_admin
from app.modules.auth.models import AdminDoc
from app.modules.endpoints import repository
from app.modules.endpoints.models import EndpointDoc
from app.modules.endpoints.parsers import docx_parser, xlsx_parser, text_parser

router = APIRouter(tags=["Endpoints"])

# --- SCHEMAS ---

class CreateSetRequest(BaseModel):
    name: str

# --- ROUTES ---

@router.post("/sets", status_code=status.HTTP_201_CREATED)
async def create_endpoint_set(
    request: CreateSetRequest, 
    admin: AdminDoc = Depends(require_admin)
):
    new_set = await repository.create_empty_set(admin.id, request.name)
    return new_set


@router.get("/sets/{set_id}")
async def get_endpoint_set(
    set_id: str, 
    admin: AdminDoc = Depends(require_admin)
):
    endpoint_set = await repository.get_set_by_id(set_id)
    if not endpoint_set or endpoint_set.admin_id != admin.id:
        raise HTTPException(status_code=404, detail="Endpoint set not found")
    return endpoint_set


@router.post("/sets/{set_id}/import")
async def import_endpoints_unified(
    set_id: str,
    file: UploadFile | None = File(None),
    text_content: str | None = Form(None),
    admin: AdminDoc = Depends(require_admin)
):
    """
    Unified ingestion API. Accepts EITHER a .docx/.xlsx file OR raw text via form data.
    """
    endpoint_set = await repository.get_set_by_id(set_id)
    if not endpoint_set or endpoint_set.admin_id != admin.id:
        raise HTTPException(status_code=404, detail="Endpoint set not found")

    if not file and not text_content:
        raise HTTPException(status_code=400, detail="You must provide either a 'file' or 'text_content'.")

    parsed_data = []

    try:
        # Scenario 1: A file was uploaded
        if file:
            content = await file.read()
            if file.filename.endswith(".docx"):
                parsed_data = docx_parser.parse_docx(content)
            elif file.filename.endswith(".xlsx"):
                parsed_data = xlsx_parser.parse_xlsx(content)
            else:
                raise HTTPException(status_code=400, detail="File must be .docx or .xlsx")
                
        # Scenario 2: Raw text was provided
        elif text_content:
            parsed_data = await text_parser.parse_raw_text(text_content)
            if not parsed_data:
                return {"message": "No valid endpoints found in the provided text.", "set": endpoint_set}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process input: {str(e)}")

    updated_set = await repository.update_set_endpoints(endpoint_set, parsed_data)
    
    source = "file" if file else "text"
    return {
        "message": f"Successfully extracted {len(parsed_data)} endpoints from {source}", 
        "set": updated_set
    }


@router.post("/sets/{set_id}/endpoints")
async def add_single_endpoint(
    set_id: str,
    endpoint: EndpointDoc,
    admin: AdminDoc = Depends(require_admin)
):
    """Manually append a single, pre-structured endpoint to the set."""
    endpoint_set = await repository.get_set_by_id(set_id)
    if not endpoint_set or endpoint_set.admin_id != admin.id:
        raise HTTPException(status_code=404, detail="Endpoint set not found")

    # Set the position to the end of the current list
    endpoint.position = len(endpoint_set.endpoints)
    endpoint_set.endpoints.append(endpoint)
    
    updated_set = await endpoint_set.save()
    return {"message": "Endpoint added manually", "set": updated_set}