import pandas as pd
import numpy as np
import ta

def calculate_volatility_expansion_prob(nifty_df, vix_df):
    """
    Estimates probability that ATR expands next 3 days.
    """
    # 1. Precompute Indicators for Backtest (5-6 Years)
    # Ensure indices are timezone-neutral to avoid mismatches
    nifty_df.index = nifty_df.index.tz_localize(None)
    vix_df.index = vix_df.index.tz_localize(None)
    
    nifty_close = nifty_df['Close']
    vix_close = vix_df['Close']
    
    if isinstance(nifty_close, pd.DataFrame): nifty_close = nifty_close.iloc[:, 0]
    if isinstance(vix_close, pd.DataFrame): vix_close = vix_close.iloc[:, 0]
    
    # ATR (14-day)
    atr = ta.volatility.AverageTrueRange(
        high=nifty_df['High'], 
        low=nifty_df['Low'], 
        close=nifty_df['Close'], 
        window=14
    ).average_true_range()
    
    # Target: 3-day forward ATR > Current ATR * 1.2
    future_atr_max = atr.shift(-3).rolling(window=3).max() # Max ATR in next 3 days
    expansion_occurred = (future_atr_max > atr * 1.2).astype(int)
    
    # Features: VIX Percentile (1Y rolling)
    # Correct way to get rolling percentile is complex, we'll use a simplification: 
    # Current price vs last 252 days min/max or just rolling rank
    vix_pct = vix_close.rolling(window=252).apply(lambda x: (x < x.iloc[-1]).sum() / len(x) * 100)
    
    # Feature: 5D Momentum Z (1Y rolling)
    ret_5d = (nifty_close / nifty_close.shift(5) - 1) * 100
    mean_5d = ret_5d.rolling(window=252).mean()
    std_5d = ret_5d.rolling(window=252).std()
    mom_z = (ret_5d - mean_5d) / std_5d
    
    # 2. Build Probability Table
    # Bucketing
    vix_bucket = pd.cut(vix_pct, bins=[0, 25, 50, 75, 100], labels=['Low', 'Mid-Low', 'Mid-High', 'High'])
    mom_bucket = pd.cut(mom_z, bins=[-np.inf, -1.5, -0.5, 0.5, 1.5, np.inf], labels=['Strong Bear', 'Weak', 'Neutral', 'Bullish', 'Strong Bull'])
    
    backtest_df = pd.DataFrame({
        'expansion': expansion_occurred,
        'vix_bucket': vix_bucket,
        'mom_bucket': mom_bucket
    }).dropna()
    
    prob_table = backtest_df.groupby(['vix_bucket', 'mom_bucket'], observed=True)['expansion'].mean() * 100
    
    # 3. Current Mapping
    current_vix_pct = vix_pct.iloc[-1]
    current_mom_z = mom_z.iloc[-1]
    
    # Determine buckets for today
    def get_vix_bucket(val):
        if val < 25: return 'Low'
        if val < 50: return 'Mid-Low'
        if val < 75: return 'Mid-High'
        return 'High'
    
    def get_mom_bucket(val):
        if val < -1.5: return 'Strong Bear'
        if val < -0.5: return 'Weak'
        if val < 0.5: return 'Neutral'
        if val < 1.5: return 'Bullish'
        return 'Strong Bull'
    
    c_vix_b = get_vix_bucket(current_vix_pct)
    c_mom_b = get_mom_bucket(current_mom_z)
    
    try:
        prob = prob_table.loc[(c_vix_b, c_mom_b)]
    except (KeyError, IndexError):
        prob = backtest_df['expansion'].mean() * 100 # Fallback to global mean
        
    return {
        "probability": round(prob, 1),
        "vix_pct": round(current_vix_pct, 1),
        "mom_z": round(current_mom_z, 2),
        "risk_level": "High Risk" if prob > 60 else "Moderate" if prob > 30 else "Low Risk",
        "color": "red" if prob > 60 else "orange" if prob > 30 else "green"
    }
