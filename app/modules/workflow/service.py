import json
from pathlib import Path
from pydantic import ValidationError
from app.modules.endpoints.service import get_set_by_id
from app.modules.workflow.models import WorkflowDefinition, WorkflowDoc
from app.shared.llm import client
from app.shared.llm.client import LLMError

# Load prompt once at startup
SYSTEM_PROMPT = Path("app/modules/workflow/prompts/build_workflow.txt").read_text()

def _build_prompt(endpoint_set, description: str) -> tuple[str, str]:
    ep_text = "\n\n".join(
        f"{ep.method} {ep.url}\n"
        f"Description: {ep.description}\n"
        f"Request: {json.dumps(ep.request_body)}\n"
        f"Response: {json.dumps(ep.response_body)}"
        for ep in endpoint_set.endpoints
    )
    user = f"API Endpoints:\n{ep_text}\n\nWorkflow Description:\n{description}"
    return SYSTEM_PROMPT, user

async def generate_draft(set_id: str, description: str) -> WorkflowDefinition:
    endpoint_set = await get_set_by_id(set_id)
    if not endpoint_set:
        raise ValueError("Endpoint set not found")

    system, user = _build_prompt(endpoint_set, description)
    
    # Try generating and validating the definition
    for attempt in range(2):
        try:
            raw_json = await client.complete_with_retry(system, user)
            data = json.loads(raw_json)
            # This is the strict enforcement:
            return WorkflowDefinition.model_validate(data) 
        except (json.JSONDecodeError, ValidationError) as e:
            if attempt == 1:
                raise LLMError(f"Failed to generate valid schema: {str(e)}")
            # If we fail, append the error to the prompt and try once more
            user += f"\n\nERROR ON PREVIOUS ATTEMPT. FIX THIS SCHEMA ERROR:\n{str(e)}"

async def save_workflow(admin_id, definition: WorkflowDefinition) -> WorkflowDoc:
    doc = WorkflowDoc(definition=definition, admin_id=admin_id)
    return await doc.insert()
    
async def get_all_active() -> list[WorkflowDoc]:
    return await WorkflowDoc.find(WorkflowDoc.is_active == True).to_list()