from sqlalchemy.orm import Session

from app.models.talent import Talent, TalentStatus
from app.services.auth_client import get_user_profile


def get_pipeline(db: Session) -> dict:
    stages = {}
    total = 0
    for status in TalentStatus:
        talents = (
            db.query(Talent)
            .filter(Talent.status == status)
            .order_by(Talent.updated_at.desc())
            .all()
        )
        stages[status.value] = [_talent_to_card(t) for t in talents]
        total += len(talents)

    need_attention = len(stages.get("exam_received", [])) + len(stages.get("evaluating", []))
    return {
        "stages": stages,
        "summary": {
            "total": total,
            "by_stage": {s.value: len(stages.get(s.value, [])) for s in TalentStatus},
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
            "org_position_id": t.recruitment.org_position_id,
            "org_position_name": t.recruitment.org_position_name,
        },
        "status": t.status.value,
        "assigned_to": t.assigned_to,
        "source": t.source,
        "created_at": t.created_at.isoformat(),
        "updated_at": t.updated_at.isoformat(),
    }


def get_status_counts(db: Session) -> list[dict]:
    from sqlalchemy import func

    rows = (
        db.query(Talent.status, func.count(Talent.id))
        .group_by(Talent.status)
        .all()
    )
    return [{"status": status.value, "count": count} for status, count in rows]
