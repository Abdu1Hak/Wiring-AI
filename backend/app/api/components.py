from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.schemas.component_schema import ComponentDetailResponse, ComponentsListResponse
from app.services.catalog_service import get_component_detail, list_components

router = APIRouter(prefix="/api/components", tags=["components"])


@router.get("", response_model=ComponentsListResponse)
def get_components(session: Session = Depends(get_session)):
    return ComponentsListResponse(components=list_components(session))


@router.get("/{component_id}", response_model=ComponentDetailResponse)
def get_component(component_id: str, session: Session = Depends(get_session)):
    detail = get_component_detail(session, component_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Component not found")
    return ComponentDetailResponse(component=detail)
