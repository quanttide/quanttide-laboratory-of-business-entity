import httpx
from app.config import Settings

settings = Settings()


def get_org_position_by_name(name: str) -> dict | None:
    org_url = getattr(settings, "org_api_url", "http://127.0.0.1:8001")
    try:
        r = httpx.get(f"{org_url}/positions", params={"q": name}, timeout=5)
        r.raise_for_status()
        positions = r.json()
        for p in positions:
            if p["name"] == name:
                return p
        return None
    except Exception:
        return None


def get_org_position_by_id(position_id: int) -> dict | None:
    org_url = getattr(settings, "org_api_url", "http://127.0.0.1:8001")
    try:
        r = httpx.get(f"{org_url}/positions/{position_id}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None
