import schedule
import time
import datetime
from data_engine import fetch_market_data
from indicators import calculate_atr, weekly_structure, vix_percentile, vix_regime_5y
from risk_engine import risk_model
from event_engine import weekly_event_risk
from alert_engine import build_institutional_alert, send_telegram_alert
from config import MONDAY_ALERT_TIME

def run_weekly_job():
    print(f"[{datetime.datetime.now()}] Running Weekly Monday Risk Scan...")
    
    try:
        # 1. Fetch Data
        data = fetch_market_data()
        
        # 2. Calculate Indicators
        atr_percent = calculate_atr(data["NIFTY"])
        weekly_ok = weekly_structure(data["NIFTY"])
        vix_pct = vix_percentile(data["INDIA_VIX"])
        vix_z = vix_regime_5y(data["INDIA_VIX"])
        
        # 3. Get Risk Score
        risk_flags, risk_rationales, score, action = risk_model(
            data, atr_percent, weekly_ok, vix_pct, vix_z
        )
        
        # 4. Get Event Data
        event_data = weekly_event_risk()
        
        # 5. Build Alert
        alert_msg = build_institutional_alert(risk_flags, event_data, score, action)
        
        # 6. Send Alert
        success, info = send_telegram_alert(alert_msg)
        
        if success:
            print("Alert successfully sent to Telegram.")
        else:
            print(f"Failed to send alert: {info}")
            
    except Exception as e:
        print(f"Error in weekly job: {e}")

def start_scheduler():
    print(f"Scheduler started. Waiting for daily update at {MONDAY_ALERT_TIME}...")
    
    # Schedule the job for daily execution
    schedule.every().day.at(MONDAY_ALERT_TIME).do(run_weekly_job)
    
    # Also add a heartbeat or daily check if needed, but for now just the daily job
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # For testing: run once immediately if you want to verify
    # run_weekly_job()
    start_scheduler()
