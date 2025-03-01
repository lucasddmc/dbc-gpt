from fastapi import APIRouter, HTTPException
import os
import json

router = APIRouter()

@router.get("/status/{task_id}")
def get_status(task_id: str):
    status_path = os.path.join("results", f"{task_id}_status.json")
    spec_path = os.path.join("results", f"{task_id}_spec.sol")

    if not os.path.exists(status_path):
        raise HTTPException(status_code=404, detail="Task ID not found.")

    with open(status_path, 'r') as f:
        status_messages = json.load(f)

    result = {
        "task_id": task_id,
        "status_messages": status_messages,
        "specification_available": os.path.exists(spec_path)
    }

    return result