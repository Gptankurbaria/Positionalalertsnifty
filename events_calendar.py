from datetime import date, timedelta

def get_upcoming_events():
    """
    Mock function to return upcoming economic events.
    In a production system, this would fetch from an economic calendar API.
    """
    today = date.today()
    
    events = [
        {"date": today, "event": "RBI Policy Meet", "impact": "HIGH"},
        {"date": today + timedelta(days=2), "event": "US CPI Data", "impact": "HIGH"},
        {"date": today + timedelta(days=3), "event": "India Industrial Production", "impact": "MEDIUM"},
        {"date": today + timedelta(days=7), "event": "US Fed Minutes", "impact": "HIGH"},
        {"date": today + timedelta(days=8), "event": "Unemployment Claims", "impact": "MEDIUM"},
        {"date": today + timedelta(days=10), "event": "Trade Balance", "impact": "MEDIUM"},
    ]
    
    return events
