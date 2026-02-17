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

# Page Configuration
st.set_page_config(
    page_title="StratEdge | Institutional Option Desk",
    page_icon="💸",
    layout="wide",
)

# Caching Data
@st.cache_data(ttl=3600)
def get_cached_market_data():
    return fetch_market_data()

@st.cache_data(ttl=3600)
def get_cached_nifty50_data():
    return fetch_nifty50_data()

# Custom CSS for Minimalist Institutional Look
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; font-family: 'Inter', sans-serif; }
    div[data-testid="stMetric"] { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; }
    div[data-testid="stMetricValue"] > div { font-size: 1.6rem !important; font-weight: 700 !important; }
    h1, h2, h3 { color: #0f172a !important; font-weight: 700 !important; margin-top: 10px !important; }
    .status-box { padding: 12px; border-radius: 6px; margin-bottom: 10px; border: 1px solid #e2e8f0; }
    .interpretation { font-size: 0.85rem; color: #64748b; font-style: italic; margin-bottom: 5px; }
    .heat-cell { padding: 10px; border-radius: 4px; text-align: center; font-weight: 600; color: white; display: flex; flex-direction: column; }
    .heat-label { font-size: 0.7rem; opacity: 0.9; text-transform: uppercase; margin-bottom: 2px; }
    .heat-value { font-size: 1.1rem; }
    hr { margin: 1.5rem 0 !important; opacity: 0.1; }
    </style>
    """, unsafe_allow_html=True)

st.title("💸 Option Selling Intelligence Desk")
st.markdown("---")

# Data Loading
with st.spinner("Analyzing Volatility Regimes..."):
    try:
        data = get_cached_market_data()
        nifty50_data = get_cached_nifty50_data()
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

# 🎯 FINAL DEPLOYMENT PANEL (At Top)
st.markdown("<div style='text-align: center; margin-bottom: 25px;'>", unsafe_allow_html=True)
st.markdown("### 🎯 Recommended Option Selling Structure")

suit_colors = {"FAVORABLE": "#22c55e", "MODERATE": "#3b82f6", "CAUTION": "#f59e0b", "HIGH RISK": "#f97316", "UNFAVORABLE": "#ef4444"}
s_color = suit_colors.get(suitability, "#444")

st.markdown(f"""
    <div style="background: white; border: 2px solid {s_color}; padding: 30px; border-radius: 12px; display: inline-block; min-width: 60%; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <p style="margin: 0; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Strategy Recommendation</p>
        <h1 style="margin: 10px 0; color: {s_color}; font-size: 3.2rem; border: none; letter-spacing: -1px;">{action.upper()}</h1>
        <hr style="margin: 15px 0; background-color: {s_color}; opacity: 0.2;">
        <div style="display: flex; justify-content: space-around; align-items: center;">
            <div>
                <p style="margin: 0; color: #64748b; font-size: 0.85rem; font-weight: 600;">RISK SCORE</p>
                <h2 style="margin: 0; font-size: 2rem;">{score} / 10</h2>
            </div>
            <div>
                <p style="margin: 0; color: #64748b; font-size: 0.85rem; font-weight: 600;">SUGGESTED WIDTH</p>
                <h2 style="margin: 0; font-size: 2rem;">{strike_width}% OTM</h2>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

if risk_flags:
    reasons = ", ".join(risk_flags.keys())
    st.markdown(f"<p style='margin-top:15px; color:#64748b; font-size:0.9rem;'><b>Primary Constraints:</b> {reasons}</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# 1️⃣ TOP PANEL – MARKET SNAPSHOT
sn1, sn2, sn3, sn4 = st.columns(4)
with sn1:
    nifty_spot = data["NIFTY"]['Close'].iloc[-1]
    if isinstance(nifty_spot, pd.Series): nifty_spot = nifty_spot.iloc[0]
    n_prev = data["NIFTY"]['Close'].iloc[-2]
    if isinstance(n_prev, pd.Series): n_prev = n_prev.iloc[0]
    nifty_change = nifty_spot - n_prev
    st.metric("NIFTY SPOT", f"{round(float(nifty_spot), 1)}", f"{round(float(nifty_change), 1)}")
with sn2:
    atr_color = "normal" if atr_percent < 1.5 else "inverse"
    st.metric("ATR % (14D)", f"{round(atr_percent, 2)}%", delta_color=atr_color)
with sn3:
    vix_spot = data["INDIA_VIX"]['Close'].iloc[-1]
    if isinstance(vix_spot, pd.Series): vix_spot = vix_spot.iloc[0]
    st.metric("INDIA VIX", f"{round(float(vix_spot), 2)}")
with sn4:
    vix_color = "normal" if 40 <= vix_pct <= 65 else "inverse"
    st.metric("VIX PCT (1Y)", f"{vix_pct}%", delta_color=vix_color)

st.markdown("---")

# 2️⃣ REGIME & BREADTH SECTION
st.subheader("🛡️ Option Selling Environment")
r_col1, r_col2 = st.columns([2, 1])

with r_col1:
    regime_val = classify_regime(vix_z)
    m_state = momentum['state']
    s_state = "INTACT" if weekly_ok else "BROKEN"
    
    regime_colors = {"SUPPRESSED": "#22c55e", "NORMAL": "#3b82f6", "ELEVATED": "#f59e0b", "CRISIS": "#ef4444"}
    mom_colors = {"Strong Bullish": "#22c55e", "Bullish": "#86efac", "Neutral": "#94a3b8", "Weak": "#fbbf24", "Strong Bearish": "#ef4444"}
    struct_colors = {"INTACT": "#22c55e", "BROKEN": "#ef4444"}
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**VOL REGIME**")
        st.markdown(f"<div style='color:{regime_colors.get(regime_val)}; font-weight:bold; font-size:1.2rem;'>{regime_val}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='interpretation'>{'Stable volatility environment.' if regime_val in ['NORMAL', 'SUPPRESSED'] else 'Elevated volatility risk.'}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"**MOMENTUM**")
        st.markdown(f"<div style='color:{mom_colors.get(m_state)}; font-weight:bold; font-size:1.2rem;'>{m_state.upper()}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='interpretation'>{'Acceptable for selling.' if 'Bearish' not in m_state and 'Bullish' not in m_state else 'High directional energy.'}</div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"**STRUCTURE**")
        st.markdown(f"<div style='color:{struct_colors.get(s_state)}; font-weight:bold; font-size:1.2rem;'>{s_state}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='interpretation'>{'Trend support intact.' if s_state=='INTACT' else 'Trend breakdown risk.'}</div>", unsafe_allow_html=True)

with r_col2:
    st.markdown("**BREADTH STATUS**")
    b_col1, b_col2, b_col3 = st.columns(3)
    
    def get_b_color(val):
        if val >= 70: return "#166534"
        if val >= 40: return "#854d0e"
        return "#991b1b"

    with b_col1:
        v = round(breadth['pct_above_20'], 0)
        st.markdown(f"<div class='heat-cell' style='background:{get_b_color(v)}'><span class='heat-label'>>20D</span><span class='heat-value'>{int(v)}%</span></div>", unsafe_allow_html=True)
    with b_col2:
        v = round(breadth['pct_above_50'], 0)
        st.markdown(f"<div class='heat-cell' style='background:{get_b_color(v)}'><span class='heat-label'>>50D</span><span class='heat-value'>{int(v)}%</span></div>", unsafe_allow_html=True)
    with b_col3:
        v = breadth['ad_ratio']
        c = "#166534" if v > 1 else "#991b1b"
        st.markdown(f"<div class='heat-cell' style='background:{c}'><span class='heat-label'>ADR</span><span class='heat-value'>{v}</span></div>", unsafe_allow_html=True)

st.markdown("---")

# 3️⃣ PROBABILITY & FLOW SECTION
p_col1, p_col2 = st.columns([2, 1])

with p_col1:
    st.subheader("⛈️ Risk Probability Metrics")
    pc1, pc2, pc3 = st.columns(3)
    
    with pc1:
        prob = vol_expansion['probability']
        p_c = "#ef4444" if prob > 60 else "#f59e0b" if prob > 40 else "#22c55e"
        st.markdown(f"**VOL EXPANSION**")
        st.markdown(f"<h3 style='color:{p_c}; margin:0;'>{prob}%</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='interpretation'>{'Elevated ATR expansion risk.' if prob > 60 else 'Stable forward ATR expected.'}</div>", unsafe_allow_html=True)
    
    with pc2:
        prob = gap_risk['gap_probability']
        p_c = "#ef4444" if prob > 45 else "#f59e0b" if prob > 30 else "#22c55e"
        st.markdown(f"**GAP RISK**")
        st.markdown(f"<h3 style='color:{p_c}; margin:0;'>{prob}%</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='interpretation'>Overnight tail risk: {gap_risk['bias']} bias.</div>", unsafe_allow_html=True)
    
    with pc3:
        p_c = "#ef4444" if event_level in ["HIGH", "EXTREME"] else "#f59e0b" if event_level == "MODERATE" else "#22c55e"
        st.markdown(f"**EVENT CLUSTER**")
        st.markdown(f"<h3 style='color:{p_c}; margin:0;'>{event_level}</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='interpretation'>Cluster of high impact news.</div>", unsafe_allow_html=True)

with p_col2:
    st.subheader("🏦 FII Flow Filter")
    st.markdown("<div class='interpretation'>Mock data for institutional pressure:</div>", unsafe_allow_html=True)
    st.markdown(f"**Flow Regime:** <span style='color:#f59e0b; font-weight:bold;'>NEUTRAL</span>", unsafe_allow_html=True)
    st.caption("FII 3D Net: -450 Cr | 10D Net: +1,200 Cr")

st.markdown("---")

# 8️⃣ OPTIONAL ADDITIONS (Expandable)
with st.expander("🔍 Detailed Model Analytics"):
    ex_col1, ex_col2 = st.columns(2)
    with ex_col1:
        st.markdown("**Historical Volatility Context**")
        st.write(f"Realized Vol (20D): {iv_hv['current_hv']}%")
        st.write(f"IV-HV Spread: {iv_hv['iv_hv_spread']}% ({iv_hv['environment']})")
    with ex_col2:
        st.markdown("**Gap Study Details**")
        st.write(f"Historical Regime: {gap_risk['reasoning']}")
        st.write(f"Bias: {gap_risk['bias']}")

# Alert Dispatch
if st.button("🚀 DISPATCH INSTITUTIONAL ALERT", use_container_width=True):
    from alert_engine import send_telegram_alert
    msg = f"🛡️ STRATEDGE DECISION: {action.upper()}\nRisk Score: {score}/10 | Width: {strike_width}% OTM\nSuitability: {suitability}"
    success, info = send_telegram_alert(msg)
    if success: st.success("Alert Dispatched.")
    else: st.error(f"Failed: {info}")

# Footer
st.caption("StratEdge Institutional | Decision-Focused Positional Intelligence | Data via Yahoo Finance")
