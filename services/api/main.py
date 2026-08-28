from __future__ import annotations

import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from services.api.case_runner import (
    _case_dir,
    case_payload,
    list_cases,
    load_cached_result,
    load_case,
    load_result,
    run_case,
)
from services.api.schemas import RunRequest


app = FastAPI(title="OceanTrace API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "version": app.version}


@app.get("/api/cases")
def get_cases() -> list[dict]:
    return list_cases()


@app.get("/api/cases/{case_id}")
def get_case(case_id: str) -> dict:
    try:
        return case_payload(case_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/cases/{case_id}/run")
def run_case_endpoint(case_id: str, request: RunRequest) -> dict:
    try:
        if request.use_cached_result or request.mode == "cached":
            cached = load_cached_result(case_id, request.seed)
            if cached is not None:
                return cached.model_dump(mode="json")
        return run_case(case_id, seed=request.seed).model_dump(mode="json")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/cases/{case_id}/results/{run_id}")
def get_result(case_id: str, run_id: str) -> dict:
    result = load_result(case_id, run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return result.model_dump(mode="json")


@app.get("/api/cases/{case_id}/sar/image")
def get_sar_image(case_id: str) -> FileResponse:
    try:
        case = load_case(case_id)
        image_path = _case_dir(case_id) / case.image_path
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        return FileResponse(image_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


@app.get("/api/cases/{case_id}/sar/bounds")
def get_sar_bounds(case_id: str) -> dict:
    try:
        case = load_case(case_id)
        bounds_path = _case_dir(case_id) / case.image_bounds_path
        if not bounds_path.exists():
            raise HTTPException(status_code=404, detail="Bounds not found")
        return json.loads(bounds_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
