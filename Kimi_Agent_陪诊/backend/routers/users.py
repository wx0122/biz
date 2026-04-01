from flask import Blueprint, request, jsonify
from database import db
from models import User

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("/me", methods=["GET"])
def get_profile():
    openid = request.headers.get("X-Openid", "")
    if not openid:
        return jsonify({"error": "X-Openid header required"}), 400

    user = User.query.filter_by(openid=openid).first()
    if not user:
        # Auto-create user on first access
        user = User(openid=openid)
        db.session.add(user)
        db.session.commit()

    return jsonify(user.to_dict())


@users_bp.route("/me", methods=["PUT"])
def update_profile():
    openid = request.headers.get("X-Openid", "")
    if not openid:
        return jsonify({"error": "X-Openid header required"}), 400

    user = User.query.filter_by(openid=openid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    for field in ["name", "phone", "avatar", "city", "province"]:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return jsonify(user.to_dict())


@users_bp.route("/records", methods=["GET"])
def get_records():
    """Get user's full activity records (bookings + training)."""
    openid = request.headers.get("X-Openid", "")
    if not openid:
        return jsonify({"error": "X-Openid header required"}), 400

    user = User.query.filter_by(openid=openid).first()
    if not user:
        return jsonify({"bookings": [], "training": []})

    from models import Booking, TrainingRegistration

    bookings = Booking.query.filter_by(user_id=user.id).order_by(
        Booking.created_at.desc()
    ).all()
    training = TrainingRegistration.query.filter_by(user_id=user.id).order_by(
        TrainingRegistration.created_at.desc()
    ).all()

    return jsonify({
        "bookings": [b.to_dict() for b in bookings],
        "training": [t.to_dict() for t in training],
    })
