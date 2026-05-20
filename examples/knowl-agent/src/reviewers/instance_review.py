import json
from src.reviewers.ui import clear, header, bold, dim, ask_comment
from src.reviewers.data import load_reviews, get_review_status, set_review_status, save_reviews


FIELD_LABELS = {
    "authority": "职权", "responsibility": "职责", "rule": "规则",
    "principle": "原则", "identities": "身份", "stages": "阶段",
    "levels": "等级", "tracks": "通道", "requirements": "要求",
    "exclusions": "排除", "triggers": "触发条件", "description": "说明",
}

SHOWN_KEYS = {
    "id", "ontology", "subject", "source", "article",
    "authority", "responsibility", "rule", "principle",
    "identities", "stages", "levels", "tracks",
    "requirements", "exclusions", "triggers", "description",
    "risks", "controls", "rules", "prohibition",
    "handover_items", "succession_priority", "assessment_content",
    "risk_items", "violations", "_domain",
}


def run(domain):
    reviews = load_reviews()
    for inst in domain["instances"]:
        key = f"{domain['dir']}:instance:{inst['id']}"
        s, c = get_review_status(reviews, key)
        if s != "待评审":
            continue
        clear()
        header(f"实例评审 — {domain['dir']}")
        onto_label = next(
            (o.get("label", o["name"]) for o in domain["ontologies"] if o["id"] == inst.get("ontology")),
            inst.get("ontology", ""),
        )
        print(f"\n  本体：{onto_label}")
        print(f"  主题：{bold(inst.get('subject', ''))}")
        src = f"{inst.get('source', '')} {inst.get('article', '')}".strip()
        if src:
            print(f"  来源：{src}")

        for key_field in ["authority", "responsibility", "rule", "principle",
                          "identities", "stages", "levels", "tracks",
                          "requirements", "exclusions", "triggers", "description"]:
            val = inst.get(key_field)
            if val:
                label = FIELD_LABELS.get(key_field, key_field)
                print(f"\n  {bold(f'{label}：')}")
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            for sk, sv in item.items():
                                print(f"    · {sk}: {sv}")
                        else:
                            print(f"    · {item}")
                else:
                    print(f"    {val}")
                break

        other = {k: v for k, v in inst.items() if k not in SHOWN_KEYS}
        if other:
            print(f"\n  {bold('其他信息：')}")
            for k, v in other.items():
                if isinstance(v, list):
                    print(f"    {k}:")
                    for item in v[:5]:
                        print(f"      · {item}")
                elif isinstance(v, dict):
                    print(f"    {k}: {json.dumps(v, ensure_ascii=False)}")
                else:
                    print(f"    {k}: {v}")

        print(f"\n  {dim('---')}")
        act = input(f"  [a]通过  [s]需修改  [p]跳过  [q]退出评审: ").strip().lower()
        if act == "q":
            break
        elif act == "a":
            cmt = ask_comment()
            set_review_status(reviews, key, "通过", cmt)
            save_reviews(reviews)
        elif act == "s":
            cmt = input(f"  请说明问题: ").strip()
            set_review_status(reviews, key, "需修改", cmt)
            save_reviews(reviews)
