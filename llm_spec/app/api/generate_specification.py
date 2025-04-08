from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Body
from typing import Optional, List
from uuid import uuid4
import logging
from app.services.refinement_loop import run_verification_process
from app.utils.utils import Utils

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate_specification")
async def generate_specification(
    llm_model: str = Body(...),
    verifier: str = Body(...),
    requested_type: str = Body(...),
    context_types: List[str] = Body(default=[]),
    background_tasks: BackgroundTasks = None
):
    supported_llm_models = ["openai", "llama", "claude"]
    supported_verifiers = ["solc_verify", "smtchecker"]
    supported_erc_standards = ["erc20", "erc721", "erc1155"]

    # Validate parameters
    if llm_model.lower() not in supported_llm_models:
        raise HTTPException(status_code=400, detail=f"Unsupported LLM model. Supported models: {supported_llm_models}")
    
    if verifier.lower() not in supported_verifiers:
        raise HTTPException(status_code=400, detail=f"Unsupported verifier. Supported verifiers: {supported_verifiers}")
    
    requested_type = requested_type.lower()
    if requested_type not in supported_erc_standards:
        raise HTTPException(status_code=400, detail=f"Unsupported ERC standard for requested_type. Supported standards: {supported_erc_standards}")
    
    # Validate context types
    valid_context_types = []
    for ctx_type in context_types:
        ctx_type = ctx_type.lower()
        if ctx_type in supported_erc_standards:
            valid_context_types.append(ctx_type)
        else:
            # Log warning for invalid context type but don't fail the request
            logger.warning(f"Ignoring unsupported context type: {ctx_type}")
    
    # Always include the requested type in the context if it's not already there
    # if requested_type not in valid_context_types:
    #     valid_context_types.append(requested_type)

    prompt = Utils.build_initial_prompt(
        requested_type=requested_type,
        context_types=valid_context_types,
        verifier=verifier.lower()
    )
    
    task_id = str(uuid4())
    
    strcontext = "".join(valid_context_types)

    background_tasks.add_task(
        run_verification_process,
        prompt=prompt,
        llm_model=llm_model,
        verifier_option=verifier,
        task_id=task_id,
        requested_type=requested_type,
        str_context=str_context # Pass the requested_type to run_verification_process
    )

    return {
        "message": "Verification process started", 
        "task_id": task_id,
        "requested_type": requested_type,
        "context_types": valid_context_types
    }