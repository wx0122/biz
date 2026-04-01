from datetime import datetime, timezone
from database import db


class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)
    display_name = db.Column(db.String(50), default="")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "is_active": self.is_active,
        }


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(100), unique=True, index=True)
    name = db.Column(db.String(50), default="")
    phone = db.Column(db.String(20), default="")
    avatar = db.Column(db.String(500), default="")
    city = db.Column(db.String(50), default="")
    province = db.Column(db.String(50), default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    bookings = db.relationship("Booking", back_populates="user", lazy="dynamic")
    training_registrations = db.relationship("TrainingRegistration", back_populates="user", lazy="dynamic")
    payments = db.relationship("Payment", back_populates="user", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "openid": self.openid,
            "name": self.name,
            "phone": self.phone,
            "avatar": self.avatar,
            "city": self.city,
            "province": self.province,
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "booking_count": self.bookings.count(),
            "training_count": self.training_registrations.count(),
        }


class Hospital(db.Model):
    __tablename__ = "hospitals"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20), default="")
    address = db.Column(db.String(200), default="")
    city = db.Column(db.String(50), default="")
    province = db.Column(db.String(50), default="")
    latitude = db.Column(db.Float, default=0)
    longitude = db.Column(db.Float, default=0)
    image = db.Column(db.String(500), default="")
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "level": self.level,
            "address": self.address,
            "city": self.city,
            "image": self.image,
            "distance": "",
        }


class Escort(db.Model):
    __tablename__ = "escorts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(500), default="")
    rating = db.Column(db.Float, default=5.0)
    service_count = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(200), default="")
    city = db.Column(db.String(50), default="")
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "avatar": self.avatar,
            "rating": self.rating,
            "serviceCount": self.service_count,
            "tags": [t.strip() for t in self.tags.split(",") if t.strip()],
            "city": self.city,
        }


class ServiceType(db.Model):
    __tablename__ = "service_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), default="")
    price = db.Column(db.Float, nullable=False)
    icon = db.Column(db.String(50), default="")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "icon": self.icon,
        }


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(30), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospitals.id"))
    service_type_id = db.Column(db.Integer, db.ForeignKey("service_types.id"))
    escort_id = db.Column(db.Integer, db.ForeignKey("escorts.id"), nullable=True)
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))
    patient_name = db.Column(db.String(50))
    patient_age = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="pending")
    total_price = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="bookings")
    hospital = db.relationship("Hospital")
    service_type = db.relationship("ServiceType")
    escort = db.relationship("Escort")

    def to_dict(self):
        return {
            "id": self.id,
            "order_no": self.order_no,
            "hospital_name": self.hospital.name if self.hospital else "",
            "service_name": self.service_type.name if self.service_type else "",
            "escort_name": self.escort.name if self.escort else "",
            "date": self.date,
            "time": self.time,
            "patient_name": self.patient_name,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else "",
        }


class TrainingCourse(db.Model):
    __tablename__ = "training_courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), default="")
    duration = db.Column(db.String(20), default="")
    price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "price": self.price,
        }


class TrainingRegistration(db.Model):
    __tablename__ = "training_registrations"
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(30), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("training_courses.id"))
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    remark = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="pending")
    total_price = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="training_registrations")
    course = db.relationship("TrainingCourse")

    def to_dict(self):
        return {
            "id": self.id,
            "order_no": self.order_no,
            "course_name": self.course.name if self.course else "",
            "name": self.name,
            "phone": self.phone,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else "",
        }


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    payment_no = db.Column(db.String(40), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    order_type = db.Column(db.String(20))       # booking / training
    order_id = db.Column(db.Integer)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(20))           # wechat / alipay
    status = db.Column(db.String(20), default="pending")
    trade_no = db.Column(db.String(64), default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    paid_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="payments")

    def to_dict(self):
        return {
            "id": self.id,
            "payment_no": self.payment_no,
            "order_type": self.order_type,
            "order_id": self.order_id,
            "amount": self.amount,
            "method": self.method,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "paid_at": self.paid_at.isoformat() if self.paid_at else "",
        }


class City(db.Model):
    __tablename__ = "cities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(50), default="")
    code = db.Column(db.String(10), default="")
    is_hot = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "province": self.province,
            "code": self.code,
            "is_hot": self.is_hot,
        }
