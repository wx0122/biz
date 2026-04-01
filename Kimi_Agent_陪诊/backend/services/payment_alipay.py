"""
Alipay integration.

In production, replace the mock implementation with real Alipay SDK calls.
Docs: https://opendocs.alipay.com/open/028r8t

Required env vars:
  ALIPAY_APP_ID, ALIPAY_PRIVATE_KEY, ALIPAY_PUBLIC_KEY, ALIPAY_NOTIFY_URL
"""
from flask import current_app


def create_alipay_order(payment_no: str, amount: float, subject: str) -> str:
    """
    Create an Alipay order and return the payment URL (for H5/mini-program).

    In production flow:
      1. Build alipay.trade.create or alipay.trade.wap.pay request
      2. Sign with RSA2
      3. Return form action URL or trade_no for SDK call
    """
    app_id = current_app.config.get("ALIPAY_APP_ID", "")
    private_key = current_app.config.get("ALIPAY_PRIVATE_KEY", "")
    notify_url = current_app.config.get("ALIPAY_NOTIFY_URL", "")

    if not all([app_id, private_key]):
        return f"mock://alipay/{payment_no}?amount={amount}"

    # --- Production implementation placeholder ---
    # from alipay import AliPay
    #
    # alipay_client = AliPay(
    #     appid=app_id,
    #     app_private_key_string=private_key,
    #     alipay_public_key_string=current_app.config["ALIPAY_PUBLIC_KEY"],
    #     sign_type="RSA2",
    # )
    #
    # result = alipay_client.api_alipay_trade_wap_pay(
    #     out_trade_no=payment_no,
    #     total_amount=str(amount),
    #     subject=subject,
    #     return_url="",
    #     notify_url=notify_url,
    # )
    #
    # return f"https://openapi.alipay.com/gateway.do?{result}"

    return f"mock://alipay/{payment_no}?amount={amount}"


def verify_alipay_callback(data: dict) -> bool:
    """
    Verify Alipay callback RSA2 signature.
    In production: use alipay SDK to verify.
    """
    return True
