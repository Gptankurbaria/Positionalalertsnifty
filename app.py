import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data_engine import fetch_market_data, fetch_nifty50_data
from indicators import calculate_atr, weekly_structure, vix_percentile, vix_regime_5y, calculate_iv_hv_metrics
from regime_engine import classify_regime
from risk_engine import risk_model
from event_engine import weekly_event_risk, classify_weekly_event_risk
from breadth_engine import calculate_breadth_metrics
from momentum_engine import calculate_momentum_score
from volatility_engine import calculate_volatility_expansion_prob
from gap_engine import calculate_gap_probability
from fii_dii_engine import update_fii_dii
import streamlit.components.v1 as components

# Auto-refresh the dashboard every 24 hours (86400000 ms) automatically so it doesn't go stale
def auto_refresh(interval_ms=86400000):
    components.html(
        f"""
        <script>
            setTimeout(function() {{
                window.parent.location.reload();
            }}, {interval_ms});
        </script>
        """,
        height=0, width=0
    )


# Page Configuration
st.set_page_config(
    page_title="StratEdge | Institutional Option Desk",
    page_icon="💸",
    layout="wide",
)

# Caching Data
@st.cache_data(ttl=3600)
def get_cached_market_data_v2():
    return fetch_market_data()

@st.cache_data(ttl=3600)
def get_cached_nifty50_data_v2():
    return fetch_nifty50_data()

# Custom CSS for Minimalist Institutional Look (Compact 1-Screen)
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; color: #0f172a; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; max-width: 95% !important; }
    
    div[data-testid="stMetric"] { background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    div[data-testid="stMetricValue"] > div { font-size: 1.4rem !important; font-weight: 700 !important; }
    
    h1, h2, h3, h4 { color: #0f172a !important; font-weight: 700 !important; margin-bottom: 10px !important; }
    
    .compact-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); margin-bottom: 12px; }
    .strategy-value { font-size: 2.2rem; font-weight: 800; line-height: 1; margin: 0; }
    .stat-label { font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
    .stat-value { font-size: 1.3rem; font-weight: 800; color: #0f172a; margin: 0; line-height: 1.1; }
    .interpretation { font-size: 0.8rem; color: #64748b; font-style: italic; margin-top: 5px; line-height: 1.2; }
    
    .heat-cell { padding: 8px; border-radius: 4px; text-align: center; font-weight: 600; color: white; display: flex; flex-direction: column; }
    .heat-label { font-size: 0.65rem; opacity: 0.9; text-transform: uppercase; margin-bottom: 2px; }
    .heat-value { font-size: 1rem; }
    hr { margin: 15px 0 !important; opacity: 0.1; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h3 style='margin-top:0;'>💸 Option Selling Intelligence Desk</h3>", unsafe_allow_html=True)

# Data Loading
with st.spinner("Analyzing Volatility Regimes..."):
    try:
        data = get_cached_market_data_v2()
        nifty50_data = get_cached_nifty50_data_v2()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.stop()

# computation
atr_percent = calculate_atr(data["NIFTY"])
weekly_ok = weekly_structure(data["NIFTY"])
vix_z = vix_regime_5y(data["INDIA_VIX"])
iv_hv = calculate_iv_hv_metrics(data["NIFTY"], data["INDIA_VIX"])
vix_pct = iv_hv['iv_percentile']

# Institutional Layers
breadth = calculate_breadth_metrics(nifty50_data)
momentum = calculate_momentum_score(data["NIFTY"])
vol_expansion = calculate_volatility_expansion_prob(data["NIFTY"], data["INDIA_VIX"])
gap_risk = calculate_gap_probability(data["NIFTY"], data["INDIA_VIX"])
event_data = weekly_event_risk()
event_level = classify_weekly_event_risk(event_data["high_this"], event_data["med_this"])
fii_dii_data = update_fii_dii()

# Risk Model
risk_flags, risk_rationales, score, action, suitability = risk_model(
    data, atr_percent, weekly_ok, vix_pct, vix_z,
    breadth_metrics=breadth,
    momentum_metrics=momentum,
    vol_expansion_metrics=vol_expansion,
    gap_metrics=gap_risk
)

# Deployment Strike Logic
strike_width = round(atr_percent * 1.5, 1) # Rule of thumb for weekly carry

# Styling lookups
suit_colors = {"FAVORABLE": "#22c55e", "MODERATE": "#3b82f6", "CAUTION": "#f59e0b", "HIGH RISK": "#f97316", "UNFAVORABLE": "#ef4444"}
regime_colors = {"SUPPRESSED": "#22c55e", "NORMAL": "#3b82f6", "ELEVATED": "#f59e0b", "CRISIS": "#ef4444"}
mom_colors = {"Strong Bullish": "#22c55e", "Bullish": "#86efac", "Neutral": "#94a3b8", "Weak": "#fbbf24", "Strong Bearish": "#ef4444"}
struct_colors = {"INTACT": "#22c55e", "BROKEN": "#ef4444"}

s_color = suit_colors.get(suitability, "#444")
reasons = " | ".join(risk_flags.keys()) if risk_flags else "None"

# === LAYOUT START ===
# 1. Market Snapshot (Full Width)
sn1, sn2, sn3, sn4 = st.columns(4)
nifty_spot = data["NIFTY"]['Close'].iloc[-1]
n_prev = data["NIFTY"]['Close'].iloc[-2]
nifty_spot = nifty_spot.iloc[0] if isinstance(nifty_spot, pd.Series) else nifty_spot
n_prev = n_prev.iloc[0] if isinstance(n_prev, pd.Series) else n_prev
nifty_change = nifty_spot - n_prev
vix_spot = data["INDIA_VIX"]['Close'].iloc[-1]
vix_spot = vix_spot.iloc[0] if isinstance(vix_spot, pd.Series) else vix_spot

sn1.metric("NIFTY", f"{round(float(nifty_spot), 1)}", f"{round(float(nifty_change), 1)}")
sn2.metric("ATR % (14D)", f"{round(atr_percent, 2)}%", delta_color="normal" if atr_percent < 1.5 else "inverse")
sn3.metric("INDIA VIX", f"{round(float(vix_spot), 2)}")
sn4.metric("VIX PCT (1Y)", f"{vix_pct}%", delta_color="normal" if 40 <= vix_pct <= 65 else "inverse")

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# 2. Strategy Recommendation (Full Width, Compact)
st.markdown(f"""
    <div class="compact-card" style="border-left: 6px solid {s_color}; padding: 16px 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 2;">
                <p class="strategy-value" style="color: {s_color}; font-size: 2rem;">{action.upper()}</p>
                <div class="interpretation" style="margin-top: 4px; font-weight: 500;">Constraints: <span style="color:#ef4444;">{reasons}</span></div>
            </div>
            <div style="flex: 1; text-align: center; border-left: 1px solid #e2e8f0;">
                <p class="stat-label">RISK SCORE</p>
                <p class="stat-value">{score} / 10</p>
            </div>
            <div style="flex: 1; text-align: center; border-left: 1px solid #e2e8f0;">
                <p class="stat-label">SUGGESTED WIDTH</p>
                <p class="stat-value">{strike_width}% OTM</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# 3. Environment Overview Row (4 columns)
env1, env2, env3, env4 = st.columns(4)

regime_val = classify_regime(vix_z)
m_state = momentum['state']
s_state = "INTACT" if weekly_ok else "BROKEN"

with env1:
    st.markdown(f"""
    <div class="compact-card" style="height: 100px;">
        <div class="stat-label">VOL REGIME</div>
        <div class="stat-value" style="color:{regime_colors.get(regime_val)}; margin-top:2px;">{regime_val}</div>
        <div class="interpretation" style="margin-top:4px;">{'Stable vol.' if regime_val in ['NORMAL', 'SUPPRESSED'] else 'Elevated vol risk.'}</div>
    </div>
    """, unsafe_allow_html=True)

with env2:
    st.markdown(f"""
    <div class="compact-card" style="height: 100px;">
        <div class="stat-label">MOMENTUM</div>
        <div class="stat-value" style="color:{mom_colors.get(m_state)}; margin-top:2px;">{m_state.upper()}</div>
        <div class="interpretation" style="margin-top:4px;">{'Acceptable' if 'Bearish' not in m_state and 'Bullish' not in m_state else 'High directional energy'}</div>
    </div>
    """, unsafe_allow_html=True)

with env3:
    st.markdown(f"""
    <div class="compact-card" style="height: 100px;">
        <div class="stat-label">STRUCTURE</div>
        <div class="stat-value" style="color:{struct_colors.get(s_state)}; margin-top:2px;">{s_state}</div>
        <div class="interpretation" style="margin-top:4px;">{'Trend intact.' if s_state=='INTACT' else 'Trend breakdown risk.'}</div>
    </div>
    """, unsafe_allow_html=True)

with env4:
    v20 = round(breadth['pct_above_20'], 0)
    v50 = round(breadth['pct_above_50'], 0)
    adr = breadth['ad_ratio']
    def get_b_color(val): return "#166534" if val >= 70 else "#854d0e" if val >= 40 else "#991b1b"
    adr_col = "#166534" if adr > 1 else "#991b1b"
    st.markdown(f"""
    <div class="compact-card" style="height: 100px; padding: 12px;">
        <div class="stat-label" style="margin-bottom: 2px;">BREADTH STATUS</div>
        <div style="display: flex; gap: 4px; margin-top: 4px;">
            <div class="heat-cell" style="flex:1; background:{get_b_color(v20)}; padding:4px;"><span class="heat-label" style="font-size:0.6rem;">>20D</span><span class="heat-value" style="font-size:0.85rem;">{int(v20)}%</span></div>
            <div class="heat-cell" style="flex:1; background:{get_b_color(v50)}; padding:4px;"><span class="heat-label" style="font-size:0.6rem;">>50D</span><span class="heat-value" style="font-size:0.85rem;">{int(v50)}%</span></div>
            <div class="heat-cell" style="flex:1; background:{adr_col}; padding:4px;"><span class="heat-label" style="font-size:0.6rem;">ADR</span><span class="heat-value" style="font-size:0.85rem;">{adr}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 4. Risk & Institutional Flow Row (4 columns)
rc1, rc2, rc3, rc4 = st.columns(4)

with rc1:
    prob = vol_expansion['probability']
    p_c = "#ef4444" if prob > 60 else "#f59e0b" if prob > 40 else "#22c55e"
    st.markdown(f"""
    <div class="compact-card" style="height: 100px;">
        <div class="stat-label">VOL EXPANSION</div>
        <div class="stat-value" style="color:{p_c}; margin-top:2px;">{prob}%</div>
        <div class="interpretation" style="margin-top:4px;">{'Elevated expansion risk.' if prob > 60 else 'Stable forward ATR.'}</div>
    </div>
    """, unsafe_allow_html=True)
    
with rc2:
    prob = gap_risk['gap_probability']
    p_c = "#ef4444" if prob > 45 else "#f59e0b" if prob > 30 else "#22c55e"
    st.markdown(f"""
    <div class="compact-card" style="height: 100px;">
        <div class="stat-label">GAP RISK</div>
        <div class="stat-value" style="color:{p_c}; margin-top:2px;">{prob}%</div>
        <div class="interpretation" style="margin-top:4px;">Tail risk: {gap_risk['bias']} bias.</div>
    </div>
    """, unsafe_allow_html=True)
    
with rc3:
    p_c = "#ef4444" if event_level in ["HIGH", "EXTREME"] else "#f59e0b" if event_level == "MODERATE" else "#22c55e"
    st.markdown(f"""
    <div class="compact-card" style="height: 100px;">
        <div class="stat-label">EVENT CLUSTER</div>
        <div class="stat-value" style="color:{p_c}; margin-top:2px;">{event_level}</div>
        <div class="interpretation" style="margin-top:4px;">Cluster of high impact news.</div>
    </div>
    """, unsafe_allow_html=True)

with rc4:
    flow_regime = fii_dii_data.get("flow_regime", "NEUTRAL")
    f_3d = fii_dii_data.get("fii_3d_net", -450)
    d_3d = fii_dii_data.get("dii_3d_net", 720)
    f_10d = fii_dii_data.get("fii_10d_net", 1200)
    d_10d = fii_dii_data.get("dii_10d_net", 2050)
    
    flow_col = "#ef4444" if flow_regime == "BEARISH" else "#22c55e" if flow_regime == "BULLISH" else "#f59e0b"
    
    st.markdown(f"""
    <div class="compact-card" style="height: 100px;">
        <div class="stat-label">INST FLOW FILTER</div>
        <div class="stat-value" style="color:{flow_col}; margin-top:2px;">{flow_regime}</div>
        <div class="interpretation" style="margin-top:2px; font-size: 0.70rem;">
            <b>3D</b>: FII {f_3d:+.0f} | DII {d_3d:+.0f}<br>
            <b>10D</b>: FII {f_10d:+.0f} | DII {d_10d:+.0f}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)

# 5. Actions & Details Bottom Row
ac1, ac2 = st.columns([7, 3])

with ac1:
    with st.expander("🔍 Detailed Model Analytics"):
        st.write(f"Realized Vol (20D): {iv_hv['current_hv']}% | IV-HV Spread: {iv_hv['iv_hv_spread']}% ({iv_hv['environment']})")
        st.write(f"Gap Regime: {gap_risk['reasoning']} | Base Bias: {gap_risk['bias']}")

with ac2:
    if st.button("🚀 DISPATCH ALERTS", use_container_width=True):
        from alert_engine import send_telegram_alert
        msg = f"🛡️ STRATEDGE DECISION: {action.upper()}\nRisk Score: {score}/10 | Width: {strike_width}% OTM\nSuitability: {suitability}"
        success, info = send_telegram_alert(msg)
        if success: st.success("Alert Dispatched.")
        else: st.error(f"Failed: {info}")
    
    if st.button("🔄 REFRESH FII/DII", use_container_width=True):
        update_fii_dii(force=True)
        st.toast("FII/DII Data Updated!")
        st.rerun()


auto_refresh(86400000) # 24 hours
st.caption("StratEdge Institutional | Data via Yahoo Finance")

