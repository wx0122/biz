"""
WeChat Pay (JSAPI) integration.

In production, replace the mock implementation with real WeChat Pay API calls.
Docs: https://pay.weixin.qq.com/doc/v3/merchant/4012791858

Required env vars:
  WECHAT_APP_ID, WECHAT_MCH_ID, WECHAT_API_KEY, WECHAT_NOTIFY_URL
"""
import hashlib
import time
from flask import current_app


def create_wechat_order(payment_no: str, amount: float, description: str, openid: str) -> str:
    """
    Create a WeChat JSAPI pay order and return the pay parameters (as JSON string).

    In production flow:
      1. Call POST https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi
      2. Get prepay_id from response
      3. Sign and return JSAPI pay parameters for frontend wx.requestPayment()
    """
    app_id = current_app.config.get("WECHAT_APP_ID", "")
    mch_id = current_app.config.get("WECHAT_MCH_ID", "")
    api_key = current_app.config.get("WECHAT_API_KEY", "")
    notify_url = current_app.config.get("WECHAT_NOTIFY_URL", "")

    if not all([app_id, mch_id, api_key]):
        # Dev mode: return mock pay URL
        return f"mock://wechat-pay/{payment_no}?amount={amount}"

    # --- Production implementation placeholder ---
    # import httpx
    # import json
    #
    # body = {
    #     "appid": app_id,
    #     "mchid": mch_id,
    #     "description": description,
    #     "out_trade_no": payment_no,
    #     "notify_url": notify_url,
    #     "amount": {
    #         "total": int(amount * 100),  # cents
    #         "currency": "CNY",
    #     },
    #     "payer": {"openid": openid},
    # }
    #
    # resp = httpx.post(
    #     "https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi",
    #     json=body,
    #     headers=_build_auth_header(body),
    # )
    # prepay_id = resp.json().get("prepay_id", "")
    #
    # # Build JSAPI pay params
    # timestamp = str(int(time.time()))
    # nonce = uuid.uuid4().hex
    # package = f"prepay_id={prepay_id}"
    # sign_str = f"{app_id}\n{timestamp}\n{nonce}\n{package}\n"
    # pay_sign = _rsa_sign(sign_str)
    #
    # return json.dumps({
    #     "timeStamp": timestamp,
    #     "nonceStr": nonce,
    #     "package": package,
    #     "signType": "RSA",
    #     "paySign": pay_sign,
    # })

    return f"mock://wechat-pay/{payment_no}?amount={amount}"


def verify_wechat_callback(headers: dict, body: str) -> bool:
    """
    Verify WeChat Pay callback signature.
    In production: verify using WeChat platform certificate + RSA.
    """
    # Placeholder - always returns True in dev
    return True
