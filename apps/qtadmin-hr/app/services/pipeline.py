from sqlalchemy.orm import Session

from app.models.talent import Talent, TalentStage
from app.services.auth_client import get_user_profile


def get_pipeline(db: Session) -> dict:
    stages = {}
    total = 0
    for stage in TalentStage:
        talents = (
            db.query(Talent)
            .filter(Talent.stage == stage)
            .order_by(Talent.updated_at.desc())
            .all()
        )
        stages[stage.value] = [_talent_to_card(t) for t in talents]
        total += len(talents)

    need_attention = len(stages.get("exam_received", [])) + len(stages.get("evaluating", []))
    return {
        "stages": stages,
        "summary": {
            "total": total,
            "by_stage": {s.value: len(stages.get(s.value, [])) for s in TalentStage},
            "need_attention": need_attention,
        },
    }


def _talent_to_card(t: Talent) -> dict:
    profile = get_user_profile(t.user_profile_id)
    return {
        "id": t.id,
        "user_profile_id": t.user_profile_id,
        "profile": {
            "real_name": profile["real_name"] if profile else None,
            "email": profile["email"] if profile else None,
        },
        "recruitment_id": t.recruitment_id,
        "recruitment": {
            "id": t.recruitment.id,
            "name": t.recruitment.name,
            "plan_id": t.recruitment.plan_id,
        },
        "stage": t.stage.value,
        "assigned_to": t.assigned_to,
        "source": t.source,
        "created_at": t.created_at.isoformat(),
        "updated_at": t.updated_at.isoformat(),
    }


def get_stage_counts(db: Session) -> list[dict]:
    from sqlalchemy import func

    rows = (
        db.query(Talent.stage, func.count(Talent.id))
        .group_by(Talent.stage)
        .all()
    )
    return [{"stage": stage.value, "count": count} for stage, count in rows]
