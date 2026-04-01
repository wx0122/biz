from flask import Blueprint, request, jsonify
from database import db
from models import Escort

escorts_bp = Blueprint("escorts", __name__, url_prefix="/api/escorts")


@escorts_bp.route("", methods=["GET"])
def list_escorts():
    city = request.args.get("city", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Escort.query.filter_by(is_active=True)
    if city:
        query = query.filter_by(city=city)

    pag = query.order_by(Escort.rating.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "items": [e.to_dict() for e in pag.items],
        "total": pag.total,
    })


@escorts_bp.route("/<int:escort_id>", methods=["GET"])
def get_escort(escort_id):
    e = db.session.get(Escort, escort_id)
    if not e or not e.is_active:
        return jsonify({"error": "Not found"}), 404
    return jsonify(e.to_dict())
