import httpx
from django.conf import settings
from django.core.cache import cache
import time
import base64
import json

CARAPI_BASE_URL = "https://carapi.app/api"
TOKEN_CACHE_KEY = "carapi_jwt_token"


def _get_token_expiry(token: str) -> int:
    """Decode JWT payload and return expiry timestamp."""
    try:
        payload = token.split('.')[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = json.loads(base64.b64decode(payload))
        return decoded.get('exp', 0)
    except Exception:
        return 0


def get_auth_token() -> str:
    # Check cache first
    token = cache.get(TOKEN_CACHE_KEY)
    if token:
        print("Using cached token.")
        return token

    # Fetch new token
    with httpx.Client(timeout=15) as client:
        response = client.post(
            f"{CARAPI_BASE_URL}/auth/login",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "api_token": settings.CAR_API_TOKEN,
                "api_secret": settings.CAR_API_SECRET,
            },
        )
        if response.status_code != 200:
            print(f"Auth Error: {response.status_code} - {response.text}")
            response.raise_for_status()

        token = response.text.strip()
        print("Fetched new token from API.")

        # Cache token until 60 seconds before expiry
        exp = _get_token_expiry(token)
        if exp:
            ttl = max(exp - int(time.time()) - 60, 60)
            cache.set(TOKEN_CACHE_KEY, token, timeout=ttl)
            print(f"Token cached for {ttl} seconds.")

        return token


def get_specs_by_ymm(year: str, make: str, model: str, trim: str = None) -> dict:
    token = get_auth_token()
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    params = {"year": year, "make": make, "model": model, "verbose": "yes"}
    if trim:
        params["trim"] = trim

    with httpx.Client(timeout=15) as client:
        response = client.get(f"{CARAPI_BASE_URL}/trims/v2", headers=headers, params=params)
        print(f"YMM Response: {response.text}")
        response.raise_for_status()
        data = response.json()
        total = data.get("collection", {}).get("total", 0)
        if total == 0:
            return {"success": False, "message": f"No results found for {year} {make} {model}."}
        return {"success": True, "data": data["data"], "total": total}


def get_specs_by_vin(vin: str) -> dict:
    token = get_auth_token()
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    with httpx.Client(timeout=15) as client:
        response = client.get(f"{CARAPI_BASE_URL}/vin/{vin}", headers=headers)
        print(f"VIN Response: {response.text}")
        response.raise_for_status()
        data = response.json()
        if data:
            return {"success": True, "data": data}
        return {"success": False, "message": "VIN not found."}