import pandas as pd
import numpy as np
import ta

def calculate_atr(df):
    """
    Calculates the 14-day ATR as a percentage of the current price.
    """
    atr_series = ta.volatility.AverageTrueRange(
        high=df['High'], 
        low=df['Low'], 
        close=df['Close'], 
        window=14
    ).average_true_range()

    # Get the last valid value
    last_atr = atr_series.iloc[-1]
    last_close = df['Close'].iloc[-1]
    
    # Handle both Series and scalar (yfinance sometimes returns multi-index)
    if isinstance(last_atr, pd.Series):
        last_atr = last_atr.iloc[0]
    if isinstance(last_close, pd.Series):
        last_close = last_close.iloc[0]

    atr_percent = (last_atr / last_close) * 100
    return atr_percent


def weekly_structure(df):
    """
    Checks if the weekly trend is bullish (Price > 20W SMA > 50W SMA).
    """
    weekly = df.resample('W').last()

    weekly['20W'] = weekly['Close'].rolling(20).mean()
    weekly['50W'] = weekly['Close'].rolling(50).mean()

    # Get last values
    last_close = weekly['Close'].iloc[-1]
    last_20w = weekly['20W'].iloc[-1]
    last_50w = weekly['50W'].iloc[-1]

    # Handle Series
    if isinstance(last_close, pd.Series): last_close = last_close.iloc[0]
    if isinstance(last_20w, pd.Series): last_20w = last_20w.iloc[0]
    if isinstance(last_50w, pd.Series): last_50w = last_50w.iloc[0]

    condition = (
        last_close > last_20w and
        last_20w > last_50w
    )

    return condition


def calculate_iv_hv_metrics(nifty_df, vix_df):
    """
    Calculates IV (VIX) vs HV (Realized Vol) spread and IV Rank.
    """
    # 1. Realized Volatility (HV) - 20-day annualized
    n_close = nifty_df['Close']
    if isinstance(n_close, pd.DataFrame): n_close = n_close.iloc[:, 0]
    
    returns = n_close.pct_change()
    hv_20 = returns.rolling(window=20).std() * np.sqrt(252) * 100
    current_hv = hv_20.iloc[-1]
    
    # 2. Implied Volatility (IV) - VIX
    v_close = vix_df['Close']
    if isinstance(v_close, pd.DataFrame): v_close = v_close.iloc[:, 0]
    current_iv = v_close.iloc[-1]
    
    # 3. IV Rank & Percentile (1Y)
    vix_1y = v_close.tail(252)
    vix_min = vix_1y.min()
    vix_max = vix_1y.max()
    
    iv_rank = ((current_iv - vix_min) / (vix_max - vix_min)) * 100
    iv_percentile = ((vix_1y < current_iv).sum() / len(vix_1y)) * 100
    
    # 4. IV-HV Spread (Positive means vol is overpriced)
    spread = current_iv - current_hv
    
    return {
        "current_iv": round(current_iv, 2),
        "current_hv": round(current_hv, 2),
        "iv_rank": round(iv_rank, 1),
        "iv_percentile": round(iv_percentile, 1),
        "iv_hv_spread": round(spread, 2),
        "environment": "Overpriced" if spread > 2 else "Fair" if spread > -2 else "Underpriced"
    }

def vix_percentile(vix_df):
    """ Legacy helper, now redundant but kept for safety """
    v_close = vix_df['Close']
    if isinstance(v_close, pd.DataFrame): v_close = v_close.iloc[:, 0]
    last_1y = v_close.tail(252)
    current = last_1y.iloc[-1]
    return ((last_1y < current).sum() / len(last_1y)) * 100


def vix_regime_5y(vix_df):
    """
    Calculates the Z-score of the current VIX relative to its 5-year mean and std dev.
    """
    current = vix_df['Close'].iloc[-1]
    if isinstance(current, pd.Series):
        current = current.iloc[0]
        
    mean_5y = vix_df['Close'].mean()
    std_5y = vix_df['Close'].std()
    
    if isinstance(mean_5y, pd.Series): mean_5y = mean_5y.iloc[0]
    if isinstance(std_5y, pd.Series): std_5y = std_5y.iloc[0]

    z = (current - mean_5y) / std_5y

    return z
