import os
import json
import datetime
import requests

CACHE_FILE = "institutional_flow_cache.json"

def get_nse_fii_dii_daily():
    """Fetches the latest daily FII/DII data from NSE."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/reports/fii-dii",
        "Accept": "*/*"
    }
    s = requests.Session()
    s.headers.update(headers)
    try:
        s.get("https://www.nseindia.com", timeout=10)
        r = s.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=10)
        if r.status_code == 200:
            data = r.json()
            fii_net = 0
            dii_net = 0
            date_str = None
            
            for row in data:
                if row.get("category") == "FII/FPI":
                    fii_net = float(row.get("netValue", 0))
                    date_str = row.get("date")
                elif row.get("category") == "DII":
                    dii_net = float(row.get("netValue", 0))
                    # date_str is usually the same for both
                    if not date_str:
                        date_str = row.get("date")
            
            if date_str:
                return {"date": date_str, "fii_net": fii_net, "dii_net": dii_net}
    except Exception as e:
        print(f"Error fetching NSE FII/DII data: {e}")
        
    return None

def load_cache():
    """Loads cache or initializes it with seed data matching previous mock state."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
            
    # Default seed state (creates a mock history that sums perfectly to the requested mock aggregates)
    today_str = datetime.datetime.now().strftime("%d-%b-%Y")
    return {
        "last_update_date": "01-Jan-2000", # force update on first run
        "history": [
            # 10 days of history, we'll put the bulk of the net in the last 3 days
            # Mock targets: FII 3D = -450, DII 3D = +720
            # FII 10D = +1200, DII 10D = +2050
            # So Days 4-10 total: FII = +1650, DII = +1330
            {"date": "Day 10", "fii_net": 1650, "dii_net": 1330},
            {"date": "Day 9", "fii_net": 0, "dii_net": 0},
            {"date": "Day 8", "fii_net": 0, "dii_net": 0},
            {"date": "Day 7", "fii_net": 0, "dii_net": 0},
            {"date": "Day 6", "fii_net": 0, "dii_net": 0},
            {"date": "Day 5", "fii_net": 0, "dii_net": 0},
            {"date": "Day 4", "fii_net": 0, "dii_net": 0},
            {"date": "Day 3", "fii_net": -150, "dii_net": 240},
            {"date": "Day 2", "fii_net": -150, "dii_net": 240},
            {"date": "Day 1", "fii_net": -150, "dii_net": 240}
        ],
        "fii_3d_net": -450.0,
        "dii_3d_net": 720.0,
        "fii_10d_net": 1200.0,
        "dii_10d_net": 2050.0,
        "flow_regime": "NEUTRAL"
    }

def update_fii_dii():
    """Main function called by dashboard to ensure data is updated once per day."""
    cache = load_cache()
    today_str = datetime.datetime.now().strftime("%d-%b-%Y")
    
    # Check if already updated today
    if cache.get("last_update_date") == today_str:
        return cache
        
    latest_data = get_nse_fii_dii_daily()
    
    if latest_data:
        # Avoid duplicate date entries (e.g. tracking same day if today_str drift)
        if len(cache["history"]) > 0 and cache["history"][-1]["date"] == latest_data["date"]:
            cache["history"][-1] = latest_data # Update if it's the exact same NSE date
            cache["last_update_date"] = today_str # But mark script as having checked today
        else:
            cache["history"].append(latest_data)
            cache["last_update_date"] = today_str
            
        # Keep only the last 10 trading days
        cache["history"] = cache["history"][-10:]
        
        # Calculate Rolling Networks
        if len(cache["history"]) > 0:
            hist_10d = cache["history"]
            hist_3d = cache["history"][-3:]
            
            cache["fii_3d_net"] = sum(x["fii_net"] for x in hist_3d)
            cache["dii_3d_net"] = sum(x["dii_net"] for x in hist_3d)
            cache["fii_10d_net"] = sum(x["fii_net"] for x in hist_10d)
            cache["dii_10d_net"] = sum(x["dii_net"] for x in hist_10d)
            
            # Flow Regime Logic
            net_inst_flow = cache["fii_3d_net"] + cache["dii_3d_net"]
            
            if net_inst_flow > 1500:
                cache["flow_regime"] = "BULLISH"
            elif net_inst_flow < -1500:
                cache["flow_regime"] = "BEARISH"
            else:
                cache["flow_regime"] = "NEUTRAL"
                
        # Save cache
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=4)
            
    return cache
