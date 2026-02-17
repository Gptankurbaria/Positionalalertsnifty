import pandas as pd
import numpy as np

def calculate_gap_probability(nifty_df, vix_df):
    """
    Measures likelihood of >1% Monday gap based on historical study.
    """
    # 1. Prepare Data
    nifty = nifty_df[['Open', 'Close']].copy()
    
    # 2. Identify Mondays and Friday Closes
    # We want Monday Open and Friday Close
    # A simple way is to resample to business days and look for gaps between D and D-1
    # but specifically where D is Monday.
    
    nifty['day_of_week'] = nifty.index.dayofweek # Monday=0, Friday=4
    
    # Gap % = (Today Open - Prev Close) / Prev Close * 100
    nifty['prev_close'] = nifty['Close'].shift(1)
    nifty['gap_pct'] = (nifty['Open'] - nifty['prev_close']) / nifty['prev_close'] * 100
    
    # Filters only Mondays
    mondays = nifty[nifty['day_of_week'] == 0].copy()
    
    # Define Large Gap
    mondays['large_gap'] = mondays['gap_pct'].abs() > 1.0
    mondays['pos_gap'] = mondays['gap_pct'] > 1.0
    mondays['neg_gap'] = mondays['gap_pct'] < -1.0
    
    # Features for segmentation (Rolling VIX % and Mom Z as of previous day)
    # Ensure indices are timezone-neutral to avoid mismatches
    nifty.index = nifty.index.tz_localize(None)
    vix_df.index = vix_df.index.tz_localize(None)
    
    vix_close = vix_df['Close']
    if isinstance(vix_close, pd.DataFrame): vix_close = vix_close.iloc[:, 0]
    vix_pct = vix_close.rolling(window=252).apply(lambda x: (x < x.iloc[-1]).sum() / len(x) * 100)
    
    n_close = nifty['Close']
    ret_5d = (n_close / n_close.shift(5) - 1) * 100
    mom_z = (ret_5d - ret_5d.rolling(252).mean()) / ret_5d.rolling(252).std()
    
    # Create a features dataframe and shift by 1 to represent "Previous Day"
    features = pd.DataFrame({
        'vix_pct_fri': vix_pct,
        'mom_z_fri': mom_z
    }).shift(1)
    
    # Join features into the mondays slice using the index (Dates)
    # This is more robust than .loc and handles missing dates automatically
    mondays.index = mondays.index.tz_localize(None) # Match timezone
    mondays = mondays.join(features, how='left')
    
    # Bucketing
    mondays['vix_regime'] = pd.cut(mondays['vix_pct_fri'], bins=[0, 50, 100], labels=['Low VIX', 'High VIX'])
    mondays['mom_regime'] = pd.cut(mondays['mom_z_fri'], bins=[-np.inf, 0, np.inf], labels=['Bearish', 'Bullish'])
    
    # Combine for Regime segmentation
    # Drop NAs
    mondays.dropna(subset=['vix_regime', 'mom_regime'], inplace=True)
    
    # Prob Table
    prob_table = mondays.groupby(['vix_regime', 'mom_regime'], observed=True)['large_gap'].mean() * 100
    direction_table = mondays.groupby(['vix_regime', 'mom_regime'], observed=True)['gap_pct'].mean()
    
    # 3. Current Assessment
    current_vix_pct = vix_pct.iloc[-1]
    current_mom_z = mom_z.iloc[-1]
    
    curr_vix_r = 'Low VIX' if current_vix_pct <= 50 else 'High VIX'
    curr_mom_r = 'Bearish' if current_mom_z <= 0 else 'Bullish'
    
    try:
        gap_prob = prob_table.loc[(curr_vix_r, curr_mom_r)]
        avg_gap = direction_table.loc[(curr_vix_r, curr_mom_r)]
    except:
        gap_prob = mondays['large_gap'].mean() * 100
        avg_gap = mondays['gap_pct'].mean()
        
    bias = "Positive" if avg_gap > 0 else "Negative"
    
    return {
        "gap_probability": round(gap_prob, 1),
        "bias": bias,
        "reasoning": f"{curr_vix_r} + {curr_mom_r}",
        "color": "red" if gap_prob > 40 else "orange" if gap_prob > 20 else "green"
    }
