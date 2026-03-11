from data_engine import fetch_market_data
from indicators import calculate_atr

data = fetch_market_data()
df = data["NIFTY"]
print("NIFTY columns:", df.columns)
print("NIFTY High type:", type(df['High']))

try:
    atr = calculate_atr(df)
    print("ATR calculated:", atr)
except Exception as e:
    import traceback
    traceback.print_exc()
