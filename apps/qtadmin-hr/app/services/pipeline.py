from sqlalchemy.orm import Session

from app.models.applicant import Applicant, ApplicantStage


def get_pipeline(db: Session) -> dict:
    stages = {}
    total = 0
    for stage in ApplicantStage:
        apps = (
            db.query(Applicant)
            .filter(Applicant.stage == stage)
            .order_by(Applicant.updated_at.desc())
            .all()
        )
        stages[stage.value] = [_applicant_to_card(a) for a in apps]
        total += len(apps)

    need_attention = len(stages.get("exam_received", [])) + len(stages.get("evaluating", []))
    return {
        "stages": stages,
        "summary": {
            "total": total,
            "by_stage": {s.value: len(stages.get(s.value, [])) for s in ApplicantStage},
            "need_attention": need_attention,
        },
    }


def _applicant_to_card(a: Applicant) -> dict:
    return {
        "id": a.id,
        "name": a.name,
        "email": a.email,
        "school": a.school,
        "recruitment_id": a.recruitment_id,
        "recruitment": {
            "id": a.recruitment.id,
            "name": a.recruitment.name,
            "plan_id": a.recruitment.plan_id,
        },
        "stage": a.stage.value,
        "assigned_to": a.assigned_to,
        "source": a.source,
        "created_at": a.created_at.isoformat(),
        "updated_at": a.updated_at.isoformat(),
    }


def get_stage_counts(db: Session) -> list[dict]:
    from sqlalchemy import func

    rows = (
        db.query(Applicant.stage, func.count(Applicant.id))
        .group_by(Applicant.stage)
        .all()
    )
    return [{"stage": stage.value, "count": count} for stage, count in rows]
