import sys
import os
import json

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from fii_dii_engine import update_fii_dii
    print("Running manual FII/DII sync...")
    result = update_fii_dii(force=True)
    print("\nSync Result:")
    print(json.dumps({
        "last_update_date": result.get("last_update_date"),
        "latest_fii_net": result.get("latest_fii_net"),
        "latest_dii_net": result.get("latest_dii_net"),
        "regime": result.get("flow_regime")
    }, indent=4))
except Exception as e:
    print(f"Error during sync: {e}")
    import traceback
    traceback.print_exc()
