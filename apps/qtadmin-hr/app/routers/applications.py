import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application, ApplicationStage
from app.models.candidate import Candidate
from app.models.requisition import Requisition
from app.schemas.application import (
    ApplicationCreate,
    ApplicationQuickCreate,
    ApplicationRead,
    ApplicationUpdate,
    StageTransition,
)
from app.services.org_client import get_org_position_by_name
from app.services.pipeline import get_stage_counts, transition_stage

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationRead])
def list_applications(
    stage: ApplicationStage | None = None,
    candidate_id: int | None = None,
    requisition_id: int | None = None,
    assigned_to: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    qb = db.query(Application)
    if stage:
        qb = qb.filter(Application.stage == stage)
    if candidate_id:
        qb = qb.filter(Application.candidate_id == candidate_id)
    if requisition_id:
        qb = qb.filter(Application.requisition_id == requisition_id)
    if assigned_to:
        qb = qb.filter(Application.assigned_to.ilike(f"%{assigned_to}%"))
    if date_from:
        qb = qb.filter(Application.created_at >= date_from)
    if date_to:
        qb = qb.filter(Application.created_at <= date_to)
    return qb.order_by(Application.updated_at.desc()).offset(skip).limit(limit).all()


@router.post("/import-csv", status_code=201)
def import_applications_csv(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only .csv files accepted")

    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    created = []
    for row in reader:
        name = row.get("name") or row.get("姓名", "").strip()
        email = row.get("email") or row.get("邮箱", "").strip()
        school = row.get("school") or row.get("学校", "").strip() or None
        major = row.get("major") or row.get("专业", "").strip() or None
        position_name = row.get("position") or row.get("岗位", "").strip()
        stage_str = (row.get("stage") or row.get("阶段") or "").strip()
        stage = ApplicationStage(stage_str) if stage_str in {s.value for s in ApplicationStage} else ApplicationStage.NEW
        if not name or not email or not position_name:
            continue

        candidate = db.query(Candidate).filter(Candidate.email == email).first()
        if not candidate:
            candidate = Candidate(name=name, email=email, school=school, major=major, source="csv_import")
            db.add(candidate)
            db.flush()

        org_pos = get_org_position_by_name(position_name)
        if not org_pos:
            continue

        requisition = db.query(Requisition).filter(Requisition.org_position_id == org_pos["id"], Requisition.status == "open").first()
        if not requisition:
            requisition = Requisition(org_position_id=org_pos["id"], org_position_name=org_pos["name"])
            db.add(requisition)
            db.flush()

        a = Application(candidate_id=candidate.id, requisition_id=requisition.id, stage=stage)
        db.add(a)
        db.flush()
        created.append({"name": name, "email": email, "position": position_name, "stage": stage.value, "application_id": a.id})

    db.commit()
    return {"imported": len(created), "applications": created}


@router.get("/stats", response_model=list[dict])
def stage_stats(db: Session = Depends(get_db)):
    return get_stage_counts(db)


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, db: Session = Depends(get_db)):
    a = db.query(Application).filter(Application.id == application_id).first()
    if not a:
        raise HTTPException(404, "Application not found")
    return a


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    a = Application(**data.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.post("/quick", response_model=ApplicationRead, status_code=201)
def create_application_quick(data: ApplicationQuickCreate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.email == data.candidate_email).first()
    if not candidate:
        candidate = Candidate(
            name=data.candidate_name,
            email=data.candidate_email,
            school=data.candidate_school,
            major=data.candidate_major,
            source="email",
        )
        db.add(candidate)
        db.flush()

    org_pos = get_org_position_by_name(data.org_position_name)
    if not org_pos:
        raise HTTPException(400, f"Position '{data.org_position_name}' not found in Org system")

    requisition = db.query(Requisition).filter(Requisition.org_position_id == org_pos["id"], Requisition.status == "open").first()
    if not requisition:
        requisition = Requisition(org_position_id=org_pos["id"], org_position_name=org_pos["name"])
        db.add(requisition)
        db.flush()

    a = Application(candidate_id=candidate.id, requisition_id=requisition.id, assigned_to=data.assigned_to)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(application_id: int, data: ApplicationUpdate, db: Session = Depends(get_db)):
    a = db.query(Application).filter(Application.id == application_id).first()
    if not a:
        raise HTTPException(404, "Application not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return a


@router.post("/{application_id}/transition", response_model=ApplicationRead)
def transition(application_id: int, data: StageTransition, db: Session = Depends(get_db)):
    a = db.query(Application).filter(Application.id == application_id).first()
    if not a:
        raise HTTPException(404, "Application not found")
    try:
        return transition_stage(db, a, data.stage)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    a = db.query(Application).filter(Application.id == application_id).first()
    if not a:
        raise HTTPException(404, "Application not found")
    db.delete(a)
    db.commit()
