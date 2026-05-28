from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateRead, CandidateUpdate

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", response_model=list[CandidateRead])
def list_candidates(
    q: str | None = Query(
        None, min_length=1, description="全文搜索：姓名/邮箱/学校/专业"
    ),
    school: str | None = None,
    source: str | None = None,
    degree: str | None = None,
    tag: str | None = Query(None, alias="tag"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    qb = db.query(Candidate)
    if q:
        like = f"%{q}%"
        qb = qb.filter(
            or_(
                Candidate.name.ilike(like),
                Candidate.email.ilike(like),
                Candidate.school.ilike(like),
                Candidate.major.ilike(like),
            )
        )
    if school:
        qb = qb.filter(Candidate.school.ilike(f"%{school}%"))
    if source:
        qb = qb.filter(Candidate.source == source)
    if degree:
        qb = qb.filter(Candidate.degree == degree)
    if tag:
        qb = qb.filter(Candidate.tags.ilike(f"%{tag}%"))
    if date_from:
        qb = qb.filter(Candidate.created_at >= date_from)
    if date_to:
        qb = qb.filter(Candidate.created_at <= date_to)
    return qb.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(404, "Candidate not found")
    return c


@router.post("", response_model=CandidateRead, status_code=201)
def create_candidate(data: CandidateCreate, db: Session = Depends(get_db)):
    c = Candidate(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.patch("/{candidate_id}", response_model=CandidateRead)
def update_candidate(
    candidate_id: int, data: CandidateUpdate, db: Session = Depends(get_db)
):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(404, "Candidate not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{candidate_id}", status_code=204)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(404, "Candidate not found")
    db.delete(c)
    db.commit()
