import time
import hmac
import hashlib
import base64
import urllib.parse
import logging
import requests

def _send_with_retry(name, send_func):
    """通用重试逻辑的装饰器"""
    for i in range(3): # 总共尝试3次
        try:
            send_func()
            return # 成功则直接返回
        except requests.exceptions.RequestException as e:
            logging.warning(f"请求 {name} Webhook 时出错 (第 {i+1} 次尝试): {e}")
            if i < 2:
                time.sleep(2) # 等待2秒后重试
    logging.error(f"发送到 {name} 失败: 3次尝试后依然失败。")

def send_to_dingtalk(webhook_url, secret, formatted_message):
    """Sends a message to a DingTalk webhook."""
    def do_send():
        payload = {"msgtype": "markdown", "markdown": {"title": "Telegram 新消息", "text": formatted_message}}
        headers = {'Content-Type': 'application/json'}
        
        current_webhook_url = webhook_url
        if secret:
            timestamp = str(round(time.time() * 1000))
            secret_enc = secret.encode('utf-8')
            string_to_sign = f'{timestamp}\n{secret}'
            string_to_sign_enc = string_to_sign.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            current_webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

        response = requests.post(current_webhook_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status() # 如果请求失败则抛出异常
        result = response.json()
        if result.get("errcode") == 0:
            logging.info("消息成功发送到钉钉。")
        else:
            logging.error(f"发送到钉钉失败: {result.get('errmsg')}")
    
    _send_with_retry("钉钉", do_send)

def send_to_feishu(webhook_url, formatted_message):
    """Sends a message to a Feishu webhook."""
    def do_send():
        payload = {"msg_type": "text", "content": {"text": formatted_message.replace("**", "")}}
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("StatusCode") == 0 or result.get("code") == 0:
            logging.info("消息成功发送到飞书。")
        else:
            logging.error(f"发送到飞书失败: {result.get('msg') or result.get('message')}")

    _send_with_retry("飞书", do_send)

def send_to_slack(webhook_url, formatted_message):
    """Sends a message to a Slack webhook."""
    def do_send():
        slack_message = formatted_message.replace('**', '*')
        payload = {"text": slack_message}
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        if response.status_code == 200 and response.text == "ok":
            logging.info("消息成功发送到 Slack。")
        else:
            logging.error(f"发送到 Slack 失败: {response.text}")

    _send_with_retry("Slack", do_send)
