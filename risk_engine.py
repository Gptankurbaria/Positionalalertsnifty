import pandas as pd
from event_engine import weekly_event_risk, classify_weekly_event_risk

def risk_model(data, atr_percent, weekly_ok, vix_pct, vix_z, 
               breadth_metrics=None, momentum_metrics=None, 
               vol_expansion_metrics=None, gap_metrics=None):
    """
    Institutional Decision Engine for Nifty Option Selling.
    Returns: risk_flags, risk_rationales, score (max 10), action, suitability
    """
    risk_flags = {}
    risk_rationales = {}
    score = 0

    # 1. Volatility Regime (VIX Percentile)
    # Ideal: 40-65. Extreme low (<20) or high (>80) are risky.
    if vix_pct < 20 or vix_pct > 80:
        risk_flags["VIX Regime"] = "Risk"
        score += 2
        risk_rationales["VIX Regime"] = "Underpriced vol or Panic Regime"

    # 2. Vol Expansion Probability
    if vol_expansion_metrics:
        prob = vol_expansion_metrics["probability"]
        if prob > 70:
            score += 3
            risk_flags["Vol Expansion"] = "Extreme"
        elif prob > 60:
            score += 2
            risk_flags["Vol Expansion"] = "High"

    # 3. Gap Probability
    if gap_metrics:
        prob = gap_metrics["gap_probability"]
        if prob > 45:
            score += 2
            risk_flags["Gap Risk"] = "High"
        elif prob > 30:
            score += 1
            risk_flags["Gap Risk"] = "Moderate"

    # 4. Momentum Shock (|Z| > 1.5)
    if momentum_metrics:
        z = abs(momentum_metrics["z_score"])
        if z > 1.5:
            score += 2
            risk_flags["Momentum"] = "Extreme"

    # 5. Breadth Filter
    if breadth_metrics:
        b20 = breadth_metrics["pct_above_20"]
        if b20 < 40:
            score += 2
            risk_flags["Breadth"] = "Weak"
        elif b20 < 60:
            score += 1
            risk_flags["Breadth"] = "Mixed"

    # 6. Weekly Structure
    if not weekly_ok:
        score += 1
        risk_flags["Structure"] = "Broken"

    # Final Decision Mapping (Scale 0-10)
    score = min(score, 10)
    
    if score <= 1:
        action = "Full Size Short Strangle"
        suitability = "FAVORABLE"
    elif score <= 3:
        action = "Reduced Size Strangle"
        suitability = "MODERATE"
    elif score <= 5:
        action = "Iron Condor Only"
        suitability = "CAUTION"
    elif score <= 7:
        action = "Hedge Required"
        suitability = "HIGH RISK"
    else:
        action = "Avoid New Positions"
        suitability = "UNFAVORABLE"

    return risk_flags, risk_rationales, score, action, suitability
