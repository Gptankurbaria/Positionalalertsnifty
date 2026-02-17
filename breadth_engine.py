import pandas as pd
import numpy as np

def calculate_breadth_metrics(nifty50_df):
    """
    Calculates % Above 20 DMA, % Above 50 DMA, and AD Ratio for Nifty 50 constituents.
    """
    # nifty50_df is a MultiIndex DataFrame with levels [Price, Symbol]
    # We care about 'Close'
    closes = nifty50_df['Close']
    
    # Fill NAs if any stock list changed recently
    closes = closes.ffill()
    
    # 1. % Above 20 DMA
    sma20 = closes.rolling(window=20).mean()
    above_20 = (closes.iloc[-1] > sma20.iloc[-1]).sum()
    pct_above_20 = (above_20 / len(closes.columns)) * 100
    
    # 2. % Above 50 DMA
    sma50 = closes.rolling(window=50).mean()
    above_50 = (closes.iloc[-1] > sma50.iloc[-1]).sum()
    pct_above_50 = (above_50 / len(closes.columns)) * 100
    
    # 3. Advance/Decline Ratio (Daily)
    # Today's return vs yesterday
    daily_returns = closes.pct_change()
    advances = (daily_returns.iloc[-1] > 0).sum()
    declines = (daily_returns.iloc[-1] < 0).sum()
    
    ad_ratio = advances / declines if declines > 0 else advances
    
    results = {
        "pct_above_20": pct_above_20,
        "pct_above_50": pct_above_50,
        "ad_ratio": round(ad_ratio, 2),
        "advances": advances,
        "declines": declines
    }
    
    # Interpretation
    for k in ["pct_above_20", "pct_above_50"]:
        val = results[k]
        if val >= 70:
            results[f"{k}_label"] = "Strong"
            results[f"{k}_color"] = "green"
        elif val >= 40:
            results[f"{k}_label"] = "Stable"
            results[f"{k}_color"] = "yellow"
        else:
            results[f"{k}_label"] = "Weak"
            results[f"{k}_color"] = "red"
            
    # AD Ratio interpretation
    if results["ad_ratio"] > 1.5:
        results["ad_ratio_label"] = "Expansion"
        results["ad_ratio_color"] = "green"
    elif results["ad_ratio"] >= 0.7:
        results["ad_ratio_label"] = "Neutral"
        results["ad_ratio_color"] = "yellow"
    else:
        results["ad_ratio_label"] = "Contraction"
        results["ad_ratio_color"] = "red"
        
    return results
