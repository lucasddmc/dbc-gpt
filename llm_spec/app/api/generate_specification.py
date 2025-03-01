from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Body
from typing import Optional
from uuid import uuid4
from app.services.refinement_loop import run_verification_process
from app.utils.utils import Utils

router = APIRouter()

@router.post("/generate_specification")
async def generate_specification(
    llm_model: str = Body(...),
    verifier: str = Body(...),
    erc_standard: str = Body(...),
    # contract_file: UploadFile = File(...),
    # reference_file: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None
):
    supported_llm_models = ["openai", "llama", "claude"]
    supported_verifiers = ["solc_verify", "smtchecker"]
    supported_erc_standards = ["erc20", "erc721", "erc1155"]

    if llm_model.lower() not in supported_llm_models:
        raise HTTPException(status_code=400, detail=f"Unsupported LLM model. Supported models: {supported_llm_models}")
    if verifier.lower() not in supported_verifiers:
        raise HTTPException(status_code=400, detail=f"Unsupported verifier. Supported verifiers: {supported_verifiers}")
    if erc_standard.lower() not in supported_erc_standards:
        raise HTTPException(status_code=400, detail=f"Unsupported ERC standard. Supported standards: {supported_erc_standards}")

    # contract_content = (await contract_file.read()).decode('utf-8')
    # reference_content = None
    # if reference_file:
    #    reference_content = (await reference_file.read()).decode('utf-8')

    prompt = Utils.build_initial_prompt(
        erc_standard=erc_standard.lower(),
        verifier=verifier.lower()
    )
    
    task_id = str(uuid4())
    
    background_tasks.add_task(
        run_verification_process,
        prompt=prompt,
        llm_model=llm_model,
        verifier_option=verifier,
        task_id=task_id
    )

    return {"message": "Verification process started", "task_id": task_id}