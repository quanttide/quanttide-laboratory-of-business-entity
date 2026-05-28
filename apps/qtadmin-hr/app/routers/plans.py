from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanRead, PlanUpdate
from app.services.org_client import get_org_position_by_id

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanRead])
def list_plans(
    status: str | None = None,
    org_position_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    qb = db.query(Plan)
    if status:
        qb = qb.filter(Plan.status == status)
    if org_position_id:
        qb = qb.filter(Plan.org_position_id == org_position_id)
    return qb.order_by(Plan.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{plan_id}", response_model=PlanRead)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    p = db.query(Plan).filter(Plan.id == plan_id).first()
    if not p:
        raise HTTPException(404, "Plan not found")
    return p


@router.post("", response_model=PlanRead, status_code=201)
def create_plan(data: PlanCreate, db: Session = Depends(get_db)):
    org_pos = get_org_position_by_id(data.org_position_id)
    p = Plan(
        org_position_id=data.org_position_id,
        org_position_name=org_pos["name"] if org_pos else None,
        headcount=data.headcount,
        reason=data.reason,
        period=data.period,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.patch("/{plan_id}", response_model=PlanRead)
def update_plan(plan_id: int, data: PlanUpdate, db: Session = Depends(get_db)):
    p = db.query(Plan).filter(Plan.id == plan_id).first()
    if not p:
        raise HTTPException(404, "Plan not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{plan_id}", status_code=204)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    p = db.query(Plan).filter(Plan.id == plan_id).first()
    if not p:
        raise HTTPException(404, "Plan not found")
    db.delete(p)
    db.commit()
