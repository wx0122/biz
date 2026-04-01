import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Booking, ServiceType, User

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")


def _gen_order_no():
    from datetime import datetime
    return "PZ" + datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:6].upper()


@bookings_bp.route("", methods=["POST"])
def create_booking():
    data = request.get_json()

    # Get or create user by openid (from header or body)
    openid = request.headers.get("X-Openid", data.get("openid", "guest"))
    user = User.query.filter_by(openid=openid).first()
    if not user:
        user = User(openid=openid, name=data.get("patient_name", ""), phone=data.get("phone", ""))
        db.session.add(user)
        db.session.flush()

    svc = db.session.get(ServiceType, int(data["service_type_id"]))
    price = svc.price if svc else 0

    booking = Booking(
        order_no=_gen_order_no(),
        user_id=user.id,
        hospital_id=int(data["hospital_id"]),
        service_type_id=int(data["service_type_id"]),
        date=data["date"],
        time=data["time"],
        patient_name=data["patient_name"],
        patient_age=data.get("patient_age", ""),
        phone=data["phone"],
        description=data.get("description", ""),
        total_price=price,
        status="pending",
    )
    db.session.add(booking)
    db.session.commit()

    return jsonify({
        "message": "Booking created",
        "order_no": booking.order_no,
        "total_price": booking.total_price,
        "booking": booking.to_dict(),
    }), 201


@bookings_bp.route("", methods=["GET"])
def list_bookings():
    openid = request.headers.get("X-Openid", "")
    if not openid:
        return jsonify({"items": [], "total": 0})

    user = User.query.filter_by(openid=openid).first()
    if not user:
        return jsonify({"items": [], "total": 0})

    bookings = Booking.query.filter_by(user_id=user.id).order_by(
        Booking.created_at.desc()
    ).all()
    return jsonify({
        "items": [b.to_dict() for b in bookings],
        "total": len(bookings),
    })


@bookings_bp.route("/<int:booking_id>", methods=["GET"])
def get_booking(booking_id):
    b = db.session.get(Booking, booking_id)
    if not b:
        return jsonify({"error": "Not found"}), 404
    return jsonify(b.to_dict())


@bookings_bp.route("/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    b = db.session.get(Booking, booking_id)
    if not b:
        return jsonify({"error": "Not found"}), 404
    if b.status not in ("pending", "paid"):
        return jsonify({"error": "Cannot cancel this booking"}), 400
    b.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "Cancelled", "booking": b.to_dict()})
