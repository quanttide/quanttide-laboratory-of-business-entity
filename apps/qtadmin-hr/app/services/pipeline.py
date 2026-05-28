import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.application import (
    STAGE_TRANSITIONS,
    Application,
    ApplicationStage,
)


def get_pipeline(db: Session) -> dict:
    stages = {}
    total = 0
    today_total = 0
    for stage in ApplicationStage:
        apps = (
            db.query(Application)
            .filter(Application.stage == stage)
            .order_by(Application.updated_at.desc())
            .all()
        )
        stages[stage.value] = [_app_to_card(a) for a in apps]
        total += len(apps)

    need_attention = len(stages.get("exam_received", [])) + len(stages.get("evaluating", []))
    return {
        "stages": stages,
        "summary": {
            "total": total,
            "by_stage": {s.value: len(stages.get(s.value, [])) for s in ApplicationStage},
            "need_attention": need_attention,
        },
    }


def _app_to_card(app: Application) -> dict:
    return {
        "id": app.id,
        "candidate": {"id": app.candidate.id, "name": app.candidate.name, "email": app.candidate.email, "school": app.candidate.school},
        "position": {"id": app.position.id, "name": app.position.name, "type": app.position.type},
        "stage": app.stage.value,
        "assigned_to": app.assigned_to,
        "created_at": app.created_at.isoformat(),
        "updated_at": app.updated_at.isoformat(),
    }


def can_transition(current: ApplicationStage, target: ApplicationStage) -> bool:
    return target in STAGE_TRANSITIONS.get(current, [])


def transition_stage(db: Session, application: Application, target: ApplicationStage) -> Application:
    if not can_transition(application.stage, target):
        raise ValueError(f"Cannot transition from {application.stage.value} to {target.value}")

    history = []
    if application.stage_history:
        history = json.loads(application.stage_history)
    history.append({
        "from": application.stage.value,
        "to": target.value,
        "at": datetime.utcnow().isoformat(),
    })

    application.stage = target
    application.stage_history = json.dumps(history)
    db.commit()
    db.refresh(application)
    return application


def get_stage_counts(db: Session) -> list[dict]:
    from sqlalchemy import func

    rows = (
        db.query(Application.stage, func.count(Application.id))
        .group_by(Application.stage)
        .all()
    )
    return [{"stage": stage.value, "count": count} for stage, count in rows]
