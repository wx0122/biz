"""
City detection service.
Uses Amap (Gaode) API for IP geolocation and GPS reverse geocoding.
Falls back to a built-in IP database when AMAP_KEY is not configured.
"""
import httpx
from flask import current_app


def detect_city_by_ip(ip: str) -> dict:
    """Detect city from IP address using Amap API."""
    amap_key = current_app.config.get("AMAP_KEY", "")

    if not amap_key:
        # Fallback: use free IP API
        return _fallback_ip_detect(ip)

    try:
        resp = httpx.get(
            "https://restapi.amap.com/v3/ip",
            params={"ip": ip, "key": amap_key},
            timeout=5,
        )
        data = resp.json()
        if data.get("status") == "1":
            city = data.get("city", "")
            province = data.get("province", "")
            # Amap sometimes returns [] for city when IP is a data center
            if isinstance(city, list):
                city = ""
            if isinstance(province, list):
                province = ""
            return {
                "city": city or "北京市",
                "province": province or "北京市",
            }
    except Exception:
        pass

    return {"city": "北京市", "province": "北京市"}


def detect_city_by_gps(lat: float, lng: float) -> dict:
    """Reverse geocode GPS coordinates to city using Amap API."""
    amap_key = current_app.config.get("AMAP_KEY", "")

    if not amap_key:
        return {"city": "北京市", "province": "北京市"}

    try:
        resp = httpx.get(
            "https://restapi.amap.com/v3/geocode/regeo",
            params={
                "location": f"{lng},{lat}",
                "key": amap_key,
                "extensions": "base",
            },
            timeout=5,
        )
        data = resp.json()
        if data.get("status") == "1":
            addr = data.get("regeocode", {}).get("addressComponent", {})
            return {
                "city": addr.get("city", "") or addr.get("province", ""),
                "province": addr.get("province", ""),
            }
    except Exception:
        pass

    return {"city": "北京市", "province": "北京市"}


def _fallback_ip_detect(ip: str) -> dict:
    """Fallback IP detection without API key."""
    if not ip or ip in ("127.0.0.1", "::1", "localhost"):
        return {"city": "北京市", "province": "北京市"}

    # Try free IP geolocation service
    try:
        resp = httpx.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=5)
        data = resp.json()
        if data.get("status") == "success":
            return {
                "city": data.get("city", "北京市"),
                "province": data.get("regionName", "北京市"),
            }
    except Exception:
        pass

    return {"city": "北京市", "province": "北京市"}
