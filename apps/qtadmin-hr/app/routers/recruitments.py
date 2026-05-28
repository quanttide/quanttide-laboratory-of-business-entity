import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.talent import STAGE_TRANSITIONS, Talent, TalentStage
from app.models.plan import Plan
from app.models.recruitment import Recruitment
from app.schemas.talent import TalentCreate, TalentRead, TalentTransition, TalentUpdate
from app.schemas.recruitment import RecruitmentCreate, RecruitmentRead, RecruitmentUpdate

router = APIRouter(prefix="/recruitments", tags=["recruitments"])


# ── Recruitment CRUD ──

@router.get("", response_model=list[RecruitmentRead])
def list_recruitments(
    plan_id: int | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    qb = db.query(Recruitment)
    if plan_id:
        qb = qb.filter(Recruitment.plan_id == plan_id)
    if status:
        qb = qb.filter(Recruitment.status == status)
    return qb.order_by(Recruitment.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{recruitment_id}", response_model=RecruitmentRead)
def get_recruitment(recruitment_id: int, db: Session = Depends(get_db)):
    r = db.query(Recruitment).filter(Recruitment.id == recruitment_id).first()
    if not r:
        raise HTTPException(404, "Recruitment not found")
    return r


@router.post("", response_model=RecruitmentRead, status_code=201)
def create_recruitment(data: RecruitmentCreate, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == data.plan_id).first()
    if not plan:
        raise HTTPException(400, "Plan not found")
    r = Recruitment(**data.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/{recruitment_id}", response_model=RecruitmentRead)
def update_recruitment(recruitment_id: int, data: RecruitmentUpdate, db: Session = Depends(get_db)):
    r = db.query(Recruitment).filter(Recruitment.id == recruitment_id).first()
    if not r:
        raise HTTPException(404, "Recruitment not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{recruitment_id}", status_code=204)
def delete_recruitment(recruitment_id: int, db: Session = Depends(get_db)):
    r = db.query(Recruitment).filter(Recruitment.id == recruitment_id).first()
    if not r:
        raise HTTPException(404, "Recruitment not found")
    db.delete(r)
    db.commit()


# ── Talent 子路由 ──

@router.get("/{recruitment_id}/talents", response_model=list[TalentRead])
def list_talents(
    recruitment_id: int,
    stage: TalentStage | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    qb = db.query(Talent).filter(Talent.recruitment_id == recruitment_id)
    if stage:
        qb = qb.filter(Talent.stage == stage)
    return qb.order_by(Talent.updated_at.desc()).offset(skip).limit(limit).all()


@router.get("/{recruitment_id}/talents/{talent_id}", response_model=TalentRead)
def get_talent(recruitment_id: int, talent_id: int, db: Session = Depends(get_db)):
    t = db.query(Talent).filter(Talent.id == talent_id, Talent.recruitment_id == recruitment_id).first()
    if not t:
        raise HTTPException(404, "Talent not found")
    return t


@router.post("/{recruitment_id}/talents", response_model=TalentRead, status_code=201)
def create_talent(recruitment_id: int, data: TalentCreate, db: Session = Depends(get_db)):
    recruitment = db.query(Recruitment).filter(Recruitment.id == recruitment_id).first()
    if not recruitment:
        raise HTTPException(404, "Recruitment not found")
    t = Talent(recruitment_id=recruitment_id, **data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.patch("/{recruitment_id}/talents/{talent_id}", response_model=TalentRead)
def update_talent(recruitment_id: int, talent_id: int, data: TalentUpdate, db: Session = Depends(get_db)):
    t = db.query(Talent).filter(Talent.id == talent_id, Talent.recruitment_id == recruitment_id).first()
    if not t:
        raise HTTPException(404, "Talent not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t


@router.post("/{recruitment_id}/talents/{talent_id}/transition", response_model=TalentRead)
def transition_talent(recruitment_id: int, talent_id: int, data: TalentTransition, db: Session = Depends(get_db)):
    t = db.query(Talent).filter(Talent.id == talent_id, Talent.recruitment_id == recruitment_id).first()
    if not t:
        raise HTTPException(404, "Talent not found")

    target = data.stage
    if target not in STAGE_TRANSITIONS.get(t.stage, []):
        raise HTTPException(400, f"Cannot transition from {t.stage.value} to {target.value}")

    history = []
    if t.stage_history:
        history = json.loads(t.stage_history)
    history.append({"from": t.stage.value, "to": target.value, "at": datetime.utcnow().isoformat()})

    t.stage = target
    t.stage_history = json.dumps(history)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{recruitment_id}/talents/{talent_id}", status_code=204)
def delete_talent(recruitment_id: int, talent_id: int, db: Session = Depends(get_db)):
    t = db.query(Talent).filter(Talent.id == talent_id, Talent.recruitment_id == recruitment_id).first()
    if not t:
        raise HTTPException(404, "Talent not found")
    db.delete(t)
    db.commit()
