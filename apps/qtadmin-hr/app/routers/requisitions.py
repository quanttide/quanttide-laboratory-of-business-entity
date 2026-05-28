from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.requisition import Requisition
from app.schemas.requisition import RequisitionCreate, RequisitionRead, RequisitionUpdate
from app.services.org_client import get_org_position_by_id

router = APIRouter(prefix="/requisitions", tags=["requisitions"])


@router.get("", response_model=list[RequisitionRead])
def list_requisitions(
    status: str | None = None,
    recruiter: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    qb = db.query(Requisition)
    if status:
        qb = qb.filter(Requisition.status == status)
    if recruiter:
        qb = qb.filter(Requisition.recruiter.ilike(f"%{recruiter}%"))
    return qb.offset(skip).limit(limit).order_by(Requisition.created_at.desc()).all()


@router.get("/{requisition_id}", response_model=RequisitionRead)
def get_requisition(requisition_id: int, db: Session = Depends(get_db)):
    r = db.query(Requisition).filter(Requisition.id == requisition_id).first()
    if not r:
        raise HTTPException(404, "Requisition not found")
    return r


@router.post("", response_model=RequisitionRead, status_code=201)
def create_requisition(data: RequisitionCreate, db: Session = Depends(get_db)):
    org_pos = get_org_position_by_id(data.org_position_id)
    r = Requisition(
        org_position_id=data.org_position_id,
        org_position_name=org_pos["name"] if org_pos else None,
        headcount=data.headcount,
        reason=data.reason,
        recruiter=data.recruiter,
        target_start_date=data.target_start_date,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/{requisition_id}", response_model=RequisitionRead)
def update_requisition(requisition_id: int, data: RequisitionUpdate, db: Session = Depends(get_db)):
    r = db.query(Requisition).filter(Requisition.id == requisition_id).first()
    if not r:
        raise HTTPException(404, "Requisition not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{requisition_id}", status_code=204)
def delete_requisition(requisition_id: int, db: Session = Depends(get_db)):
    r = db.query(Requisition).filter(Requisition.id == requisition_id).first()
    if not r:
        raise HTTPException(404, "Requisition not found")
    db.delete(r)
    db.commit()
