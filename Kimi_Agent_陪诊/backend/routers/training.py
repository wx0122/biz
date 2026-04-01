import uuid
from flask import Blueprint, request, jsonify
from database import db
from models import TrainingCourse, TrainingRegistration, User

training_bp = Blueprint("training", __name__, url_prefix="/api/training")


def _gen_order_no():
    from datetime import datetime
    return "PX" + datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:6].upper()


@training_bp.route("/courses", methods=["GET"])
def list_courses():
    courses = TrainingCourse.query.filter_by(is_active=True).all()
    return jsonify({"items": [c.to_dict() for c in courses]})


@training_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    openid = request.headers.get("X-Openid", data.get("openid", "guest"))
    user = User.query.filter_by(openid=openid).first()
    if not user:
        user = User(openid=openid, name=data.get("name", ""), phone=data.get("phone", ""))
        db.session.add(user)
        db.session.flush()

    course = db.session.get(TrainingCourse, int(data["course_id"]))
    if not course:
        return jsonify({"error": "Course not found"}), 404

    reg = TrainingRegistration(
        order_no=_gen_order_no(),
        user_id=user.id,
        course_id=course.id,
        name=data["name"],
        phone=data["phone"],
        remark=data.get("remark", ""),
        total_price=course.price,
        status="pending",
    )
    db.session.add(reg)
    db.session.commit()

    return jsonify({
        "message": "Registration created",
        "order_no": reg.order_no,
        "total_price": reg.total_price,
        "registration": reg.to_dict(),
    }), 201


@training_bp.route("/registrations", methods=["GET"])
def list_registrations():
    openid = request.headers.get("X-Openid", "")
    if not openid:
        return jsonify({"items": [], "total": 0})

    user = User.query.filter_by(openid=openid).first()
    if not user:
        return jsonify({"items": [], "total": 0})

    regs = TrainingRegistration.query.filter_by(user_id=user.id).order_by(
        TrainingRegistration.created_at.desc()
    ).all()
    return jsonify({
        "items": [r.to_dict() for r in regs],
        "total": len(regs),
    })
