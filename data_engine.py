import yfinance as yf
import pandas as pd

def fetch_market_data():
    """
    Fetches historical market data for key indices and VIX from Yahoo Finance.
    """
    symbols = {
        "NIFTY": "^NSEI",
        "INDIA_VIX": "^INDIAVIX",
        "SP500": "^GSPC",
        "NASDAQ": "^IXIC",
        "US_VIX": "^VIX"
    }

    data = {}

    for key, symbol in symbols.items():
        # Using 5y period for comprehensive regime analysis
        df = yf.download(symbol, period="6y", interval="1d", progress=False)
        df.dropna(inplace=True)
        
        if df.empty or len(df) < 20:
            raise ValueError(f"Data source returned insufficient data for {symbol} (likely API block). Please try again later.")
            
        # Flatten MultiIndex if present (yfinance v0.2.x behavior)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        data[key] = df

    return data

def fetch_nifty50_data():
    """
    Fetches daily data for all 50 Nifty stocks for the last 6 months.
    """
    from config import NIFTY50_SYMBOLS
    
    # Download 6 months of daily data for all constituents
    df = yf.download(NIFTY50_SYMBOLS, period="6mo", interval="1d", progress=False)
    
    if df.empty or len(df) < 20:
        raise ValueError("Data source returned insufficient Nifty 50 constituents data.")
        
    return df
