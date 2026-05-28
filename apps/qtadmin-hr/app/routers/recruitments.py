import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.applicant import Applicant, ApplicantStage, STAGE_TRANSITIONS
from app.models.plan import Plan
from app.models.recruitment import Recruitment
from app.schemas.applicant import ApplicantCreate, ApplicantRead, ApplicantTransition, ApplicantUpdate
from app.schemas.recruitment import RecruitmentCreate, RecruitmentRead, RecruitmentUpdate

router = APIRouter(prefix="/recruitments", tags=["recruitments"])


def _applicant_to_read(a: Applicant) -> ApplicantRead:
    return ApplicantRead.model_validate(a)


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


# ── Applicant 子路由 ──

@router.get("/{recruitment_id}/applicants", response_model=list[ApplicantRead])
def list_applicants(
    recruitment_id: int,
    stage: ApplicantStage | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    qb = db.query(Applicant).filter(Applicant.recruitment_id == recruitment_id)
    if stage:
        qb = qb.filter(Applicant.stage == stage)
    return qb.order_by(Applicant.updated_at.desc()).offset(skip).limit(limit).all()


@router.get("/{recruitment_id}/applicants/{applicant_id}", response_model=ApplicantRead)
def get_applicant(recruitment_id: int, applicant_id: int, db: Session = Depends(get_db)):
    a = db.query(Applicant).filter(Applicant.id == applicant_id, Applicant.recruitment_id == recruitment_id).first()
    if not a:
        raise HTTPException(404, "Applicant not found")
    return a


@router.post("/{recruitment_id}/applicants", response_model=ApplicantRead, status_code=201)
def create_applicant(recruitment_id: int, data: ApplicantCreate, db: Session = Depends(get_db)):
    recruitment = db.query(Recruitment).filter(Recruitment.id == recruitment_id).first()
    if not recruitment:
        raise HTTPException(404, "Recruitment not found")
    a = Applicant(recruitment_id=recruitment_id, **data.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.patch("/{recruitment_id}/applicants/{applicant_id}", response_model=ApplicantRead)
def update_applicant(recruitment_id: int, applicant_id: int, data: ApplicantUpdate, db: Session = Depends(get_db)):
    a = db.query(Applicant).filter(Applicant.id == applicant_id, Applicant.recruitment_id == recruitment_id).first()
    if not a:
        raise HTTPException(404, "Applicant not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return a


@router.post("/{recruitment_id}/applicants/{applicant_id}/transition", response_model=ApplicantRead)
def transition_applicant(recruitment_id: int, applicant_id: int, data: ApplicantTransition, db: Session = Depends(get_db)):
    a = db.query(Applicant).filter(Applicant.id == applicant_id, Applicant.recruitment_id == recruitment_id).first()
    if not a:
        raise HTTPException(404, "Applicant not found")

    target = data.stage
    if target not in STAGE_TRANSITIONS.get(a.stage, []):
        raise HTTPException(400, f"Cannot transition from {a.stage.value} to {target.value}")

    history = []
    if a.stage_history:
        history = json.loads(a.stage_history)
    history.append({"from": a.stage.value, "to": target.value, "at": datetime.utcnow().isoformat()})

    a.stage = target
    a.stage_history = json.dumps(history)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{recruitment_id}/applicants/{applicant_id}", status_code=204)
def delete_applicant(recruitment_id: int, applicant_id: int, db: Session = Depends(get_db)):
    a = db.query(Applicant).filter(Applicant.id == applicant_id, Applicant.recruitment_id == recruitment_id).first()
    if not a:
        raise HTTPException(404, "Applicant not found")
    db.delete(a)
    db.commit()
