from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from database import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        seconds=Config.JWT_ACCESS_TOKEN_EXPIRES
    )

    # Extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)

    # Register blueprints
    from routers.admin import admin_bp
    from routers.hospitals import hospitals_bp
    from routers.escorts import escorts_bp
    from routers.bookings import bookings_bp
    from routers.training import training_bp
    from routers.orders import orders_bp
    from routers.users import users_bp
    from routers.payments import payments_bp
    from routers.cities import cities_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(hospitals_bp)
    app.register_blueprint(escorts_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(cities_bp)

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=6007)
