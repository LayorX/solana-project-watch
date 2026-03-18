import requests

def send_telegram_msg(token, chat_id, message):
    """傳送 Telegram 訊息。"""
    if not token or not chat_id:
        return False, "未設定 Bot Token 或 Chat ID"
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_json = response.json()
        if res_json.get("ok"):
            return True, "成功"
        else:
            return False, res_json.get("description", "未知錯誤")
    except Exception as e:
        return False, str(e)

def format_whale_alert(symbol, label, wallet, change, current_balance, price):
    """格式化推播訊息。"""
    icon = "🟢 增持" if change > 0 else "🔴 減持"
    usd_value = abs(change * price)
    
    msg = f"<b>🚨 {symbol} 巨鯨動向警報</b>\n\n"
    msg += f"<b>標籤：</b> {label}\n"
    msg += f"<b>動作：</b> {icon} {abs(change):,.2f} {symbol}\n"
    msg += f"<b>價值：</b> 約 ${usd_value:,.2f}\n"
    msg += f"<b>當前持倉：</b> {current_balance:,.2f} {symbol}\n\n"
    msg += f"<code>{wallet}</code>\n"
    msg += f"<a href='https://solscan.io/account/{wallet}'>查看 Solscan</a>"
    return msg
