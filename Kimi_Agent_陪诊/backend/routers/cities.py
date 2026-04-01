from flask import Blueprint, request, jsonify
from database import db
from models import City
from services.city_service import detect_city_by_ip

cities_bp = Blueprint("cities", __name__, url_prefix="/api/cities")


@cities_bp.route("", methods=["GET"])
def list_cities():
    """List all available cities, hot cities first."""
    cities = City.query.order_by(City.is_hot.desc(), City.name).all()
    return jsonify({
        "items": [c.to_dict() for c in cities],
        "hot": [c.to_dict() for c in cities if c.is_hot],
    })


@cities_bp.route("/detect", methods=["GET"])
def detect():
    """Auto-detect user's city by IP address."""
    # Get client IP
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()

    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)

    if lat and lng:
        # GPS-based detection (more accurate)
        from services.city_service import detect_city_by_gps
        result = detect_city_by_gps(lat, lng)
        result["detected_by"] = "gps"
    else:
        # IP-based detection (fallback)
        result = detect_city_by_ip(ip)
        result["detected_by"] = "ip"

    return jsonify(result)


@cities_bp.route("/search", methods=["GET"])
def search():
    """Search cities by name."""
    q = request.args.get("q", "")
    if not q:
        return jsonify({"items": []})

    cities = City.query.filter(
        db.or_(City.name.contains(q), City.province.contains(q))
    ).limit(20).all()
    return jsonify({"items": [c.to_dict() for c in cities]})
