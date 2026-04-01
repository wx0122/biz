import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "peizhen-dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///peizhen.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "peizhen-jwt-secret-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # 24 hours (seconds)

    # WeChat Pay (fill in production)
    WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
    WECHAT_MCH_ID = os.getenv("WECHAT_MCH_ID", "")
    WECHAT_API_KEY = os.getenv("WECHAT_API_KEY", "")
    WECHAT_NOTIFY_URL = os.getenv("WECHAT_NOTIFY_URL", "")

    # Alipay (fill in production)
    ALIPAY_APP_ID = os.getenv("ALIPAY_APP_ID", "")
    ALIPAY_PRIVATE_KEY = os.getenv("ALIPAY_PRIVATE_KEY", "")
    ALIPAY_PUBLIC_KEY = os.getenv("ALIPAY_PUBLIC_KEY", "")
    ALIPAY_NOTIFY_URL = os.getenv("ALIPAY_NOTIFY_URL", "")

    # Amap (Gaode) Web API for IP geolocation
    AMAP_KEY = os.getenv("AMAP_KEY", "")
