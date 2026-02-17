import pandas as pd
import numpy as np

def calculate_momentum_score(nifty_df):
    """
    Calculates Rolling 5-Day Momentum Z-Score for Nifty 50.
    """
    # 5D Return = (Close_today / Close_5_days_ago - 1) * 100
    closes = nifty_df['Close']
    if isinstance(closes, pd.DataFrame):
        closes = closes.iloc[:, 0]
        
    ret_5d = (closes / closes.shift(5) - 1) * 100
    
    # Normalize using 1-year (252 days) rolling distribution
    rolling_mean_1y = ret_5d.rolling(window=252).mean()
    rolling_std_1y = ret_5d.rolling(window=252).std()
    
    current_ret = ret_5d.iloc[-1]
    current_mean = rolling_mean_1y.iloc[-1]
    current_std = rolling_std_1y.iloc[-1]
    
    z_score = (current_ret - current_mean) / current_std
    
    # Classification
    if z_score > 1.5:
        state = "Strong Bullish"
        color = "green"
    elif z_score > 0.5:
        state = "Bullish"
        color = "#90ee90" # Light green
    elif z_score > -0.5:
        state = "Neutral"
        color = "gray"
    elif z_score > -1.5:
        state = "Weak"
        color = "orange"
    else:
        state = "Strong Bearish"
        color = "red"
        
    return {
        "z_score": round(z_score, 2),
        "return_5d": round(current_ret, 2),
        "state": state,
        "color": color
    }
