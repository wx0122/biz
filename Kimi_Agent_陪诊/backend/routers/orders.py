from flask import Blueprint, request, jsonify
from models import Booking, TrainingRegistration, User

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@orders_bp.route("", methods=["GET"])
def list_orders():
    """Unified order list: bookings + training registrations."""
    openid = request.headers.get("X-Openid", "")
    order_type = request.args.get("type", "all")  # all / booking / training

    if not openid:
        return jsonify({"items": []})

    user = User.query.filter_by(openid=openid).first()
    if not user:
        return jsonify({"items": []})

    items = []

    if order_type in ("all", "booking"):
        bookings = Booking.query.filter_by(user_id=user.id).order_by(
            Booking.created_at.desc()
        ).all()
        for b in bookings:
            d = b.to_dict()
            d["type"] = "booking"
            items.append(d)

    if order_type in ("all", "training"):
        regs = TrainingRegistration.query.filter_by(user_id=user.id).order_by(
            TrainingRegistration.created_at.desc()
        ).all()
        for r in regs:
            d = r.to_dict()
            d["type"] = "training"
            items.append(d)

    # Sort by created_at descending
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return jsonify({"items": items})
