import json
from pathlib import Path
from datetime import datetime
from src.config import DATA_DIR

REVIEW_FILE = DATA_DIR / ".review.json"


def load_domains():
    domains = []
    if not DATA_DIR.exists():
        return domains
    for d in sorted(DATA_DIR.iterdir()):
        if d.is_dir() and (d / "domain.json").exists():
            with open(d / "domain.json") as f:
                info = json.load(f)
            with open(d / "ontologies.json") as f:
                ont = json.load(f)
            with open(d / "instances.json") as f:
                inst = json.load(f)
            with open(d / "relations.json") as f:
                rel = json.load(f)
            domains.append({
                "dir": d.name,
                "info": info,
                "ontologies": ont["ontologies"],
                "instances": inst["instances"],
                "relations": rel["relations"],
            })
    return domains


def load_reviews():
    if REVIEW_FILE.exists():
        with open(REVIEW_FILE) as f:
            return json.load(f)
    return {}


def save_reviews(reviews):
    REVIEW_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REVIEW_FILE, "w") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)


def get_review_status(reviews, key):
    r = reviews.get(key, {})
    return r.get("status", "待评审"), r.get("comment", "")


def set_review_status(reviews, key, status, comment=""):
    reviews[key] = {"status": status, "comment": comment, "updated": datetime.now().isoformat()}
