from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from database import db
from models import Admin, User, Booking, TrainingRegistration, Payment
from auth import verify_password, hash_password

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    admin = Admin.query.filter_by(username=username, is_active=True).first()
    if not admin or not verify_password(password, admin.hashed_password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_access_token(identity=str(admin.id))
    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "admin": admin.to_dict(),
    })


@admin_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    admin_id = int(get_jwt_identity())
    admin = db.session.get(Admin, admin_id)
    if not admin:
        return jsonify({"error": "Admin not found"}), 404
    return jsonify(admin.to_dict())


@admin_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    admin_id = int(get_jwt_identity())
    admin = db.session.get(Admin, admin_id)
    data = request.get_json()

    if not verify_password(data.get("old_password", ""), admin.hashed_password):
        return jsonify({"error": "Wrong current password"}), 400

    admin.hashed_password = hash_password(data["new_password"])
    db.session.commit()
    return jsonify({"message": "Password updated"})


# ── Dashboard stats ──────────────────────────────
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    return jsonify({
        "total_users": User.query.count(),
        "total_bookings": Booking.query.count(),
        "pending_bookings": Booking.query.filter_by(status="pending").count(),
        "total_training": TrainingRegistration.query.count(),
        "total_payments": Payment.query.filter_by(status="paid").count(),
        "total_revenue": db.session.query(
            db.func.coalesce(db.func.sum(Payment.amount), 0)
        ).filter(Payment.status == "paid").scalar(),
    })


# ── User management ──────────────────────────────
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    q = request.args.get("q", "")

    query = User.query
    if q:
        query = query.filter(
            db.or_(User.name.contains(q), User.phone.contains(q))
        )
    pag = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "items": [u.to_dict() for u in pag.items],
        "total": pag.total,
        "page": pag.page,
        "pages": pag.pages,
    })


# ── Booking management ───────────────────────────
@admin_bp.route("/bookings", methods=["GET"])
@jwt_required()
def list_bookings():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status", "")

    query = Booking.query
    if status:
        query = query.filter_by(status=status)
    pag = query.order_by(Booking.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "items": [b.to_dict() for b in pag.items],
        "total": pag.total,
        "page": pag.page,
        "pages": pag.pages,
    })


@admin_bp.route("/bookings/<int:booking_id>/status", methods=["PUT"])
@jwt_required()
def update_booking_status(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    data = request.get_json()
    booking.status = data["status"]
    if data.get("escort_id"):
        booking.escort_id = data["escort_id"]
    db.session.commit()
    return jsonify(booking.to_dict())


# ── Training management ──────────────────────────
@admin_bp.route("/training-registrations", methods=["GET"])
@jwt_required()
def list_training_registrations():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pag = TrainingRegistration.query.order_by(
        TrainingRegistration.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [t.to_dict() for t in pag.items],
        "total": pag.total,
        "page": pag.page,
        "pages": pag.pages,
    })


@admin_bp.route("/training-registrations/<int:reg_id>/status", methods=["PUT"])
@jwt_required()
def update_training_status(reg_id):
    reg = db.session.get(TrainingRegistration, reg_id)
    if not reg:
        return jsonify({"error": "Registration not found"}), 404
    data = request.get_json()
    reg.status = data["status"]
    db.session.commit()
    return jsonify(reg.to_dict())


# ── Payment management ───────────────────────────
@admin_bp.route("/payments", methods=["GET"])
@jwt_required()
def list_payments():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pag = Payment.query.order_by(
        Payment.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [p.to_dict() for p in pag.items],
        "total": pag.total,
        "page": pag.page,
        "pages": pag.pages,
    })


# ── Hospital CRUD (admin) ────────────────────────
@admin_bp.route("/hospitals", methods=["POST"])
@jwt_required()
def create_hospital():
    from models import Hospital
    data = request.get_json()
    h = Hospital(
        name=data["name"],
        level=data.get("level", ""),
        address=data.get("address", ""),
        city=data.get("city", ""),
        province=data.get("province", ""),
        latitude=data.get("latitude", 0),
        longitude=data.get("longitude", 0),
        image=data.get("image", ""),
    )
    db.session.add(h)
    db.session.commit()
    return jsonify(h.to_dict()), 201


@admin_bp.route("/hospitals/<int:hospital_id>", methods=["PUT"])
@jwt_required()
def update_hospital(hospital_id):
    from models import Hospital
    h = db.session.get(Hospital, hospital_id)
    if not h:
        return jsonify({"error": "Hospital not found"}), 404
    data = request.get_json()
    for field in ["name", "level", "address", "city", "province", "image", "latitude", "longitude"]:
        if field in data:
            setattr(h, field, data[field])
    db.session.commit()
    return jsonify(h.to_dict())


@admin_bp.route("/hospitals/<int:hospital_id>", methods=["DELETE"])
@jwt_required()
def delete_hospital(hospital_id):
    from models import Hospital
    h = db.session.get(Hospital, hospital_id)
    if not h:
        return jsonify({"error": "Hospital not found"}), 404
    h.is_active = False
    db.session.commit()
    return jsonify({"message": "Deleted"})


# ── Escort CRUD (admin) ──────────────────────────
@admin_bp.route("/escorts", methods=["POST"])
@jwt_required()
def create_escort():
    from models import Escort
    data = request.get_json()
    e = Escort(
        name=data["name"],
        avatar=data.get("avatar", ""),
        rating=data.get("rating", 5.0),
        service_count=data.get("service_count", 0),
        tags=data.get("tags", ""),
        city=data.get("city", ""),
    )
    db.session.add(e)
    db.session.commit()
    return jsonify(e.to_dict()), 201


@admin_bp.route("/escorts/<int:escort_id>", methods=["PUT"])
@jwt_required()
def update_escort(escort_id):
    from models import Escort
    e = db.session.get(Escort, escort_id)
    if not e:
        return jsonify({"error": "Escort not found"}), 404
    data = request.get_json()
    for field in ["name", "avatar", "rating", "service_count", "tags", "city"]:
        if field in data:
            setattr(e, field, data[field])
    db.session.commit()
    return jsonify(e.to_dict())
