import httpx
from app.config import Settings

settings = Settings()


def get_auth_url() -> str:
    return getattr(settings, "auth_api_url", "http://127.0.0.1:8002")


def get_user_profile(user_profile_id: int) -> dict | None:
    try:
        r = httpx.get(f"{get_auth_url()}/user-profiles/{user_profile_id}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def find_user_profile_by_email(email: str) -> dict | None:
    try:
        r = httpx.get(f"{get_auth_url()}/user-profiles", params={"email": email}, timeout=5)
        r.raise_for_status()
        profiles = r.json()
        return profiles[0] if profiles else None
    except Exception:
        return None


def create_user_profile(data: dict) -> dict | None:
    try:
        r = httpx.post(f"{get_auth_url()}/user-profiles", json=data, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None
