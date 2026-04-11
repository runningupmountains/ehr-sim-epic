import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.deps import get_db, require_api_key
from app.models.provider import Provider
from app.schemas.provider import ProviderOut

router = APIRouter(
    prefix="/api/epic/v1/providers",
    tags=["providers"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=list[ProviderOut])
def list_providers(
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(Provider)
        .order_by(Provider.last_name)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{provider_id}", response_model=ProviderOut)
def get_provider(provider_id: uuid.UUID, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.provider_id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider
