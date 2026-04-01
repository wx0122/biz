import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from database import db
from models import Payment, Booking, TrainingRegistration, User
from services.payment_wechat import create_wechat_order
from services.payment_alipay import create_alipay_order

payments_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


def _gen_payment_no():
    return "PAY" + datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:8].upper()


@payments_bp.route("/create", methods=["POST"])
def create_payment():
    """Create a payment for a booking or training order."""
    data = request.get_json()
    order_type = data.get("order_type")       # booking / training
    order_id = data.get("order_id")
    method = data.get("method")               # wechat / alipay

    if order_type not in ("booking", "training"):
        return jsonify({"error": "Invalid order_type"}), 400
    if method not in ("wechat", "alipay"):
        return jsonify({"error": "Invalid payment method"}), 400

    # Get order and amount
    if order_type == "booking":
        order = db.session.get(Booking, order_id)
    else:
        order = db.session.get(TrainingRegistration, order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    amount = order.total_price
    openid = request.headers.get("X-Openid", "")
    user = User.query.filter_by(openid=openid).first()

    payment = Payment(
        payment_no=_gen_payment_no(),
        user_id=user.id if user else None,
        order_type=order_type,
        order_id=order_id,
        amount=amount,
        method=method,
        status="pending",
    )
    db.session.add(payment)
    db.session.commit()

    # Call payment gateway
    pay_url = ""
    if method == "wechat":
        pay_url = create_wechat_order(
            payment_no=payment.payment_no,
            amount=amount,
            description=f"陪诊服务-{order.order_no}",
            openid=openid,
        )
    else:
        pay_url = create_alipay_order(
            payment_no=payment.payment_no,
            amount=amount,
            subject=f"陪诊服务-{order.order_no}",
        )

    return jsonify({
        "payment_no": payment.payment_no,
        "amount": amount,
        "method": method,
        "pay_url": pay_url,
        "status": "pending",
    })


@payments_bp.route("/wechat/notify", methods=["POST"])
def wechat_notify():
    """WeChat payment callback."""
    # In production: verify signature, parse XML/JSON body
    # For now: simulate the callback flow
    data = request.get_json() or {}
    payment_no = data.get("payment_no", "")
    trade_no = data.get("trade_no", "")

    payment = Payment.query.filter_by(payment_no=payment_no).first()
    if not payment:
        return jsonify({"return_code": "FAIL"}), 400

    payment.status = "paid"
    payment.trade_no = trade_no
    payment.paid_at = datetime.now(timezone.utc)

    # Update order status
    _mark_order_paid(payment)
    db.session.commit()

    return jsonify({"return_code": "SUCCESS"})


@payments_bp.route("/alipay/notify", methods=["POST"])
def alipay_notify():
    """Alipay payment callback."""
    # In production: verify RSA signature
    data = request.form.to_dict() if request.form else request.get_json() or {}
    payment_no = data.get("out_trade_no", data.get("payment_no", ""))
    trade_no = data.get("trade_no", "")

    payment = Payment.query.filter_by(payment_no=payment_no).first()
    if not payment:
        return "fail", 400

    payment.status = "paid"
    payment.trade_no = trade_no
    payment.paid_at = datetime.now(timezone.utc)

    _mark_order_paid(payment)
    db.session.commit()

    return "success"


@payments_bp.route("/status/<payment_no>", methods=["GET"])
def check_status(payment_no):
    """Check payment status (for frontend polling)."""
    payment = Payment.query.filter_by(payment_no=payment_no).first()
    if not payment:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "payment_no": payment.payment_no,
        "status": payment.status,
        "amount": payment.amount,
        "method": payment.method,
    })


def _mark_order_paid(payment):
    """Update the corresponding order status after payment success."""
    if payment.order_type == "booking":
        order = db.session.get(Booking, payment.order_id)
        if order:
            order.status = "paid"
    elif payment.order_type == "training":
        order = db.session.get(TrainingRegistration, payment.order_id)
        if order:
            order.status = "paid"
