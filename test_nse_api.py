import requests
import json

def test_nse_fii_dii():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/reports/fii-dii",
        "Accept": "*/*"
    }
    s = requests.Session()
    s.headers.update(headers)
    try:
        s.get("https://www.nseindia.com", timeout=10)
        r = s.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print("NSE API Response:")
            print(json.dumps(data, indent=4))
        else:
            print(f"Failed to fetch data: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nse_fii_dii()
