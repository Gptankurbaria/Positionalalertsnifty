from datetime import date, timedelta
from events_calendar import get_upcoming_events
import pandas as pd

def weekly_event_risk():
    """
    Calculates the count of High and Medium impact events for the current and next week.
    """
    today = date.today()
    events = get_upcoming_events()

    if not events:
        return {
            "this_week": pd.DataFrame(),
            "next_week": pd.DataFrame(),
            "high_this": 0, "med_this": 0,
            "high_next": 0, "med_next": 0
        }

    df = pd.DataFrame(events)

    df["date"] = pd.to_datetime(df["date"])
    # Using ISO calendar for consistent week numbering
    df["week"] = df["date"].dt.isocalendar().week
    df["year"] = df["date"].dt.isocalendar().year

    # Current week info
    current_week = pd.Timestamp(today).isocalendar().week
    current_year = pd.Timestamp(today).isocalendar().year

    # Filter upcoming only
    df = df[df["date"] >= pd.Timestamp(today)]

    # Current week events
    this_week = df[
        (df["week"] == current_week) &
        (df["year"] == current_year)
    ]

    # Next week events
    # Handle year rollover logic implicitly via increment or better yet:
    next_week_date = today + timedelta(days=7)
    next_week_num = pd.Timestamp(next_week_date).isocalendar().week
    next_week_year = pd.Timestamp(next_week_date).isocalendar().year
    
    next_week = df[
        (df["week"] == next_week_num) &
        (df["year"] == next_week_year)
    ]

    high_this = (this_week["impact"] == "HIGH").sum()
    med_this = (this_week["impact"] == "MEDIUM").sum()

    high_next = (next_week["impact"] == "HIGH").sum()
    med_next = (next_week["impact"] == "MEDIUM").sum()

    return {
        "this_week": this_week,
        "next_week": next_week,
        "high_this": int(high_this),
        "med_this": int(med_this),
        "high_next": int(high_next),
        "med_next": int(med_next)
    }

def classify_weekly_event_risk(high_count, med_count):
    """
    Classifies the weight of upcoming events.
    """
    score = high_count * 2 + med_count * 1

    if score == 0:
        return "LOW"
    elif score <= 2:
        return "MODERATE"
    elif score <= 4:
        return "HIGH"
    else:
        return "EXTREME"
