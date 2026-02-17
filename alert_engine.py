import requests
import config

def build_institutional_alert(risk_data, event_data, score, action):
    """
    Constructs a professional Telegram alert message.
    """
    status_emoji = {"AGGRESSIVE": "🟢", "CONTROLLED": "🟡", "REDUCE": "🟠", "DEFENSIVE": "🔴"}.get(action, "⚪")
    
    # Header
    msg = f"{status_emoji} *STRATEDGE RISK ALERT | POSITIONAL*\n\n"
    msg += f"*Strategy Status:* {action}\n"
    msg += f"*Risk Score:* {score}/6\n\n"
    
    # Flags
    msg += "*Risk Flags:*\n"
    for k, v in risk_data.items():
        status = "❌ ACTIVE" if v else "✅ CLEAR"
        msg += f"• {k}: {status}\n"
    
    # Events
    msg += "\n*🗓 WEEKLY EVENT RISK*\n"
    msg += f"Assessment: {classify_event_level_text(event_data)}\n"
    
    this_week_events = event_data['this_week']
    if not this_week_events.empty:
        msg += "\n*Upcoming (This Week):*\n"
        for _, row in this_week_events.iterrows():
            date_str = row['date'].strftime('%b %d')
            impact = "🔴" if row['impact'] == "HIGH" else "🟡"
            msg += f"{impact} {date_str}: {row['event']}\n"
    
    msg += f"\n*Action Plan:* Based on current volatility regime and macro context, the system recommends a {action} posture for the upcoming week."
    
    return msg

def classify_event_level_text(event_data):
    from event_engine import classify_weekly_event_risk
    return classify_weekly_event_risk(event_data["high_this"], event_data["med_this"])

def send_telegram_alert(message, bot_token=None, chat_id=None):
    """
    Sends the message to Telegram using provided tokens or defaults from config.
    """
    token = bot_token or config.TELEGRAM_BOT_TOKEN
    chat = chat_id or config.TELEGRAM_CHAT_ID

    if token in ["YOUR_BOT_TOKEN_HERE", ""] or chat in ["YOUR_CHAT_ID_HERE", ""]:
        return False, "Telegram settings incomplete. Check settings or Streamlit Secrets."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "Success"
        else:
            return False, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)
