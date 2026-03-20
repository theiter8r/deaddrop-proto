"""
Card 4: Scanner Endpoints

POST /scan   — trigger a full repo scan, persist results to DB
GET  /endpoints — return all persisted endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.discovery import discover_api_files
from app.models import Endpoint
from app.parser import parse_all
from app.schemas import EndpointRead, ScanRequest, ScanResponse

router = APIRouter()


@router.post("/scan", response_model=ScanResponse)
async def scan_repo(body: ScanRequest, db: AsyncSession = Depends(get_db)):
    # 1. Discover spec files in the repo
    try:
        discovered = await discover_api_files(body.repo_url, body.token)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Repo fetch failed: {exc}")

    # 2. Parse all discovered files into normalized endpoints
    parsed = parse_all(discovered)

    # 3. Persist to DB (upsert-style: delete old entries for this repo, insert fresh)
    await db.execute(
        Endpoint.__table__.delete().where(
            Endpoint.source_file.in_([ep.source_file for ep in parsed])
        )
        if parsed
        else Endpoint.__table__.delete().where(False)  # no-op if nothing found
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
