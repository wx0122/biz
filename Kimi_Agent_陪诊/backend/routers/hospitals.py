from flask import Blueprint, request, jsonify
from database import db
from models import Hospital

hospitals_bp = Blueprint("hospitals", __name__, url_prefix="/api/hospitals")


@hospitals_bp.route("", methods=["GET"])
def list_hospitals():
    city = request.args.get("city", "")
    search = request.args.get("search", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Hospital.query.filter_by(is_active=True)
    if city:
        query = query.filter_by(city=city)
    if search:
        query = query.filter(
            db.or_(Hospital.name.contains(search), Hospital.address.contains(search))
        )

    pag = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [h.to_dict() for h in pag.items],
        "total": pag.total,
    })


@hospitals_bp.route("/<int:hospital_id>", methods=["GET"])
def get_hospital(hospital_id):
    h = db.session.get(Hospital, hospital_id)
    if not h or not h.is_active:
        return jsonify({"error": "Not found"}), 404
    return jsonify(h.to_dict())
