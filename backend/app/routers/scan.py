"""
Card 4: Scanner Endpoints

POST /scan   — trigger a full repo scan, persist results to DB
GET  /endpoints — return all persisted endpoints

Scan strategy (three passes):
  Pass 1+2  discover_api_files()  — spec files by name then content-sniff
  Pass 3    infer_endpoints()     — Claude AI inference from source code
                                    (only runs when Pass 1+2 find nothing)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.discovery import collect_source_files, discover_api_files
from app.inference import infer_endpoints
from app.models import Endpoint
from app.parser import parse_all
from app.schemas import EndpointCreate, EndpointRead, ScanRequest, ScanResponse

router = APIRouter()


@router.post("/scan", response_model=ScanResponse)
async def scan_repo(body: ScanRequest, db: AsyncSession = Depends(get_db)):
    # ── Pass 1 + 2: spec-file discovery ──────────────────────────────────────
    try:
        discovered = await discover_api_files(body.repo_url, body.token)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Repo fetch failed: {exc}")

    parsed: list[EndpointCreate] = parse_all(discovered)

    # ── Pass 3: AI inference (only when spec files yield nothing) ─────────────
    if not parsed:
        try:
            source_files = await collect_source_files(body.repo_url, body.token)
            inferred = await infer_endpoints(source_files)
            parsed = inferred
        except Exception as exc:
            # Inference failure is non-fatal — log and continue with empty result
            import logging
            logging.getLogger(__name__).warning("AI inference failed: %s", exc)

    # ── Persist to DB ─────────────────────────────────────────────────────────
    if parsed:
        await db.execute(
            Endpoint.__table__.delete().where(
                Endpoint.source_file.in_({ep.source_file for ep in parsed})
            )
        )

    db_endpoints: list[Endpoint] = []
    for ep in parsed:
        row = Endpoint(
            endpoint_path=ep.endpoint_path,
            http_method=ep.http_method.value,
            source_file=ep.source_file,
            is_deprecated=ep.is_deprecated,
        )
        db.add(row)
        db_endpoints.append(row)

    await db.commit()
    for row in db_endpoints:
        await db.refresh(row)

    return ScanResponse(
        endpoints_discovered=len(db_endpoints),
        endpoints=[EndpointRead.model_validate(row) for row in db_endpoints],
    )


@router.get("/endpoints", response_model=list[EndpointRead])
async def list_endpoints(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint).order_by(Endpoint.id))
    return [EndpointRead.model_validate(row) for row in result.scalars().all()]
