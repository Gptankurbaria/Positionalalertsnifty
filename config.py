import streamlit as st

# Helper to fetch config from Streamlit Secrets or local config.py
def get_config(key, default=""):
    # 1. Try Streamlit Secrets (Flat or Nested)
    try:
        # Check flat keys first
        if key in st.secrets:
            return st.secrets[key]
        
        # Check common nested patterns like secrets.telegram.bot_token
        for section in st.secrets:
            if isinstance(st.secrets[section], dict):
                if key.lower() in st.secrets[section]:
                    return st.secrets[section][key.lower()]
                if key.upper() in st.secrets[section]:
                    return st.secrets[section][key.upper()]
    except:
        pass
    
    # 2. Try environment variables
    import os
    env_val = os.getenv(key) or os.getenv(key.upper()) or os.getenv(key.lower())
    if env_val:
        return env_val

    # 3. Fallback to local config_local.py
    try:
        import config_local
        return getattr(config_local, key, default)
    except ImportError:
        return default

# Initial default values
TELEGRAM_BOT_TOKEN = get_config("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = get_config("CHAT_ID", "YOUR_CHAT_ID_HERE")
MONDAY_ALERT_TIME = get_config("MONDAY_ALERT_TIME", "09:15")

# NIFTY 50 Constituents (as of Feb 2024 approx)
NIFTY50_SYMBOLS = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BPCL.NS",
    "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
    "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS",
    "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS",
    "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS",
    "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS", "TATACONSUM.NS", "TECHM.NS",
    "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS", "SHRIRAMFIN.NS"
]
