"""
Strategic Credit Risk Intelligence Terminal
Indian Commercial Banks — Financial Ratio Analysis & Data Analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re, io

# ═══════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="Credit Risk Intelligence | Indian Banks",
    page_icon="📊", layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════
# UTILITY: hex → rgba  (FIXES fillcolor bug)
# ═══════════════════════════════════════════
def hex_rgba(hex_color: str, alpha: float = 0.07) -> str:
    """Convert '#rrggbb' to 'rgba(r,g,b,alpha)' — Plotly-safe transparency."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ═══════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0}
.stApp{
    background:linear-gradient(135deg,#080c16 0%,#0e1428 45%,#120e2a 75%,#080c16 100%);
    background-attachment:fixed; font-family:'Inter',sans-serif; color:#c8d4e8;
}
.stApp::before{
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background-image:linear-gradient(rgba(110,90,220,.032) 1px,transparent 1px),
                     linear-gradient(90deg,rgba(110,90,220,.032) 1px,transparent 1px);
    background-size:54px 54px;
}
.block-container{padding:.8rem 1.8rem 2rem !important; max-width:100% !important; position:relative; z-index:1}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#070a15,#0c1022) !important; border-right:1px solid rgba(130,85,240,.16) !important}
[data-testid="stSidebar"] *{font-family:'Inter',sans-serif !important}
[data-testid="stSidebar"] label{color:#6e82a0 !important; font-size:11.5px !important}
[data-testid="stSidebar"] p{color:#6e82a0 !important; font-size:11px !important}
[data-testid="stSidebar"] h3{color:#dde6f5 !important; font-size:13px !important}
.hero{text-align:center; padding:22px 0 14px}
.hero-badge{display:inline-block; font-family:'JetBrains Mono',monospace; font-size:9px;
    letter-spacing:3px; text-transform:uppercase; color:#a78bfa;
    border:1px solid rgba(167,139,250,.28); background:rgba(167,139,250,.06);
    padding:4px 14px; border-radius:20px; margin-bottom:12px; white-space:nowrap}
.hero-title{font-size:clamp(14px,2.2vw,36px); font-weight:700; letter-spacing:-.8px;
    line-height:1.15; color:#ecf0ff; margin-bottom:5px}
.hero-title span{background:linear-gradient(120deg,#a78bfa 0%,#60a5fa 55%,#a78bfa 100%);
    background-size:200%; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation:shimmer 5s linear infinite}
@keyframes shimmer{to{background-position:200% center}}
.hero-sub{font-size:11.5px; color:#3f5270; letter-spacing:1.5px; text-transform:uppercase}
.hero-line{width:44px; height:2px; margin:12px auto 0; border-radius:2px;
    background:linear-gradient(90deg,#a78bfa,#60a5fa)}
.hero-credit{font-size:10px; color:#2a3a55; margin-top:6px; font-family:'JetBrains Mono',monospace; letter-spacing:1px}
.statusbar{display:flex; align-items:center; flex-wrap:wrap; gap:8px;
    background:rgba(255,255,255,.022); border:1px solid rgba(255,255,255,.055);
    border-radius:8px; padding:6px 14px; margin:6px 0 18px;
    font-family:'JetBrains Mono',monospace; font-size:9.5px; color:#3f5270}
.statusbar b{color:#b8c8e0}
.live-dot{display:inline-block; width:6px; height:6px; border-radius:50%;
    background:#34d399; margin-right:5px; vertical-align:middle;
    animation:blink 2s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.sec-div{font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:3px;
    text-transform:uppercase; color:#a78bfa; margin:24px 0 11px;
    display:flex; align-items:center; gap:10px}
.sec-div::after{content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(167,139,250,.28),transparent)}
.kpi-card{background:rgba(255,255,255,.022); border:1px solid rgba(255,255,255,.065);
    border-radius:12px; padding:16px 14px; position:relative; overflow:hidden;
    transition:transform .2s,border-color .2s}
.kpi-card::before{content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:var(--ac,linear-gradient(90deg,#a78bfa,#60a5fa))}
.kpi-card:hover{transform:translateY(-2px); border-color:rgba(167,139,250,.24)}
.kpi-lbl{font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:1.5px;
    text-transform:uppercase; color:#3f5270; margin-bottom:7px}
.kpi-val{font-size:25px; font-weight:700; color:#ecf0ff; line-height:1;
    margin-bottom:5px; font-variant-numeric:tabular-nums}
.kpi-meta{font-size:10.5px; color:#3f5270; margin-top:3px}
.badge{display:inline-block; padding:2px 8px; border-radius:4px; font-size:9.5px; font-weight:600; margin-top:4px; letter-spacing:.2px}
.bg{background:rgba(52,211,153,.11); color:#6ee7b7; border:1px solid rgba(52,211,153,.22)}
.br{background:rgba(248,113,113,.11); color:#fca5a5; border:1px solid rgba(248,113,113,.22)}
.by{background:rgba(251,191,36,.11); color:#fde68a; border:1px solid rgba(251,191,36,.22)}
.bb{background:rgba(167,139,250,.11); color:#c4b5fd; border:1px solid rgba(167,139,250,.22)}
.ch-wrap{background:rgba(255,255,255,.016); border:1px solid rgba(255,255,255,.05); border-radius:11px; padding:3px}
.sc-tbl{width:100%; border-collapse:collapse; font-size:12px}
.sc-tbl th{font-family:'JetBrains Mono',monospace; font-size:8.5px; letter-spacing:1.8px;
    text-transform:uppercase; color:#3f5270; padding:8px 11px;
    border-bottom:1px solid rgba(255,255,255,.055); text-align:left; white-space:nowrap}
.sc-tbl td{padding:9px 11px; border-bottom:1px solid rgba(255,255,255,.04); vertical-align:middle}
.sc-tbl tr:hover td{background:rgba(167,139,250,.04)}
.rnk{display:inline-flex; align-items:center; justify-content:center; width:19px; height:19px;
    border-radius:4px; background:rgba(255,255,255,.045); color:#6e82a0; font-size:9.5px; font-weight:700}
.sbar-bg{height:3px; background:rgba(255,255,255,.06); border-radius:2px; margin-top:4px; max-width:80px}
.sbar-fill{height:3px; border-radius:2px}
.t1p{background:rgba(52,211,153,.09); color:#6ee7b7; border:1px solid rgba(52,211,153,.2); padding:2px 8px; border-radius:5px; font-size:9.5px; font-weight:600}
.t2p{background:rgba(167,139,250,.09); color:#c4b5fd; border:1px solid rgba(167,139,250,.2); padding:2px 8px; border-radius:5px; font-size:9.5px; font-weight:600}
.t3p{background:rgba(248,113,113,.09); color:#fca5a5; border:1px solid rgba(248,113,113,.2); padding:2px 8px; border-radius:5px; font-size:9.5px; font-weight:600}
.mono{font-family:'JetBrains Mono',monospace; font-size:11px}
.ig{display:grid; grid-template-columns:1fr 1fr; gap:11px}
.ic{background:rgba(255,255,255,.018); border:1px solid rgba(255,255,255,.05); border-radius:10px; padding:15px 17px}
.ic .il{font-family:'JetBrains Mono',monospace; font-size:8.5px; letter-spacing:2px; text-transform:uppercase; color:#a78bfa; margin-bottom:5px}
.ic .it{font-size:13px; font-weight:600; color:#ecf0ff; margin-bottom:5px}
.ic .ib{font-size:12px; color:#6e82a0; line-height:1.75}
.ic .ib b{color:#b8c8e0}
.ic .ib .ok{color:#6ee7b7; font-weight:600}
.ic .ib .wn{color:#fca5a5; font-weight:600}
.written-analysis{background:rgba(96,165,250,.05); border:1px solid rgba(96,165,250,.16);
    border-radius:10px; padding:16px 18px; margin-top:4px; font-size:13px; color:#8fa8c8; line-height:1.8}
.written-analysis h4{color:#a78bfa; font-size:12px; letter-spacing:2px; text-transform:uppercase;
    font-family:'JetBrains Mono',monospace; margin-bottom:10px}
.written-analysis p{margin-bottom:9px}
.written-analysis p:last-child{margin-bottom:0}
.written-analysis b{color:#c8d4e8}
.pdf-info{background:rgba(167,139,250,.06); border:1px solid rgba(167,139,250,.2);
    border-radius:9px; padding:12px 15px; font-size:12px; color:#c4b5fd; line-height:1.8; margin-top:8px}
.offline-screen{min-height:56vh; display:flex; flex-direction:column; align-items:center;
    justify-content:center; text-align:center; padding:40px}
.offline-screen .oi{font-size:48px; margin-bottom:16px}
.offline-screen .oh{font-size:18px; font-weight:700; color:#2a3a55; margin-bottom:8px}
.offline-screen .op{font-size:12.5px; color:#3f5270; max-width:460px; line-height:1.85}
.offline-screen .oc{font-family:'JetBrains Mono',monospace; font-size:10px;
    background:rgba(255,255,255,.022); border:1px solid rgba(255,255,255,.055);
    border-radius:7px; padding:11px 15px; margin-top:14px; color:#6e82a0; text-align:left; line-height:2}
.stButton > button{background:linear-gradient(135deg,#7c3aed,#2563eb) !important;
    color:#fff !important; border:none !important; border-radius:8px !important;
    font-family:'Inter',sans-serif !important; font-weight:600 !important;
    font-size:12.5px !important; transition:opacity .2s,transform .2s !important}
.stButton > button:hover{opacity:.86 !important; transform:translateY(-1px) !important}
.stExpander{border:1px solid rgba(255,255,255,.055) !important; border-radius:9px !important; background:rgba(255,255,255,.01) !important}
hr{border-color:rgba(255,255,255,.055) !important}
div[data-testid="stFileUploader"] section{border-color:rgba(130,85,240,.22) !important}
[data-testid="stExpanderToggleIcon"] svg{display:none}
[data-testid="stExpanderToggleIcon"]::after{content:'▾'; color:#a78bfa; font-size:14px}
/* Hide the "keyboard_double_arrow_left" text — show only a clean arrow icon */
[data-testid="stBaseButton-header"] span{font-size:0 !important; width:0; overflow:hidden}
[data-testid="stBaseButton-header"] svg{display:none !important}
[data-testid="stBaseButton-header"]{position:relative; min-width:28px; min-height:28px}
[data-testid="stBaseButton-header"]::after{
    content:'‹'; position:absolute; top:50%; left:50%;
    transform:translate(-50%,-50%);
    font-size:22px; color:#a78bfa; font-weight:300; line-height:1; pointer-events:none}
button[data-testid="stBaseButton-header"]:hover::after{color:#c4b5fd}
div[data-testid="stSidebarHeader"] button span{font-size:0 !important}
div[data-testid="stSidebarHeader"] button svg{display:none !important}
div[data-testid="stSidebarHeader"] button::after{
    content:'‹'; font-size:20px; color:#a78bfa; font-weight:300}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# COLOUR CONSTANTS
# ═══════════════════════════════════════════
BANK_COLORS = {
    "SBI":   "#60a5fa", "HDFC":  "#a78bfa", "ICICI": "#34d399",
    "AXIS":  "#fbbf24", "PNB":   "#f87171", "BOB":   "#f472b6",
}
FALLBACK = ["#60a5fa","#a78bfa","#34d399","#fbbf24","#f87171","#f472b6","#818cf8","#fb923c"]
TIER_COLORS = {
    "🥇 Tier-1 (Prime)":  "#34d399",
    "⚖️ Tier-2 (Stable)": "#a78bfa",
    "🚨 Tier-3 (Watch)":  "#f87171",
}

# ═══════════════════════════════════════════
# PLOTLY BASE (no xaxis/yaxis inside)
# ═══════════════════════════════════════════
BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#6e82a0", size=11),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10.5, color="#6e82a0"),
                orientation="h", y=-0.22, x=.5, xanchor="center"),
    hoverlabel=dict(bgcolor="#111827", bordercolor="rgba(167,139,250,.35)",
                    font=dict(family="JetBrains Mono, monospace", size=11, color="#e2eaf8")),
    title_font=dict(size=12.5, color="#6e82a0"),
    margin=dict(l=6, r=6, t=38, b=6),
)
AX_X       = dict(showgrid=False, zeroline=False, tickfont=dict(size=10.5), linecolor="rgba(255,255,255,.04)")
AX_Y       = dict(gridcolor="rgba(255,255,255,.032)", zeroline=False, tickfont=dict(size=10.5))
AX_Y_CLEAN = dict(showgrid=False, zeroline=False, tickfont=dict(size=10.5))

def apply_layout(fig, extra: dict):
    fig.update_layout(**{**BASE, **extra})

def bcolor(bank, idx=0):
    for k, v in BANK_COLORS.items():
        if k.lower() in str(bank).lower():
            return v
    return FALLBACK[idx % len(FALLBACK)]

# ═══════════════════════════════════════════
# BUILT-IN VERIFIED DATA
# ═══════════════════════════════════════════
BUILTIN = pd.DataFrame({
    "Bank": (["SBI"]*5+["HDFC"]*5+["ICICI"]*5+["AXIS"]*5+["PNB"]*5+["BOB"]*5),
    "Year": ["FY 2020-21","FY 2021-22","FY 2022-23","FY 2023-24","FY 2024-25"]*6,
    "Net NPA (%)":  [1.50,1.02,0.67,0.57,0.47, 0.40,0.32,0.27,0.33,0.40,
                     1.14,0.76,0.48,0.42,0.40, 1.05,0.73,0.39,0.31,0.30,
                     5.73,4.80,2.72,0.73,0.40, 3.09,1.72,0.89,0.68,0.45],
    "ROA (%)":      [0.45,0.64,0.91,0.99,1.06, 1.78,1.79,1.79,1.68,1.72,
                     1.32,1.65,2.01,2.18,2.23, 0.66,1.11,0.73,1.68,1.72,
                     0.16,0.26,0.17,0.53,0.91, 0.07,0.60,1.01,1.16,1.23],
    "CAR (%)":      [13.74,13.83,14.68,14.28,14.25, 18.80,18.90,19.30,18.80,19.60,
                     19.12,19.16,18.34,16.33,16.60, 19.12,18.54,17.64,16.63,16.55,
                     14.32,14.50,15.50,15.97,17.01, 14.99,15.68,16.24,16.31,17.19],
    "CASA Ratio (%)": [46.13,45.28,43.80,41.11,34.39, 46.10,48.20,44.40,38.20,35.30,
                       46.30,48.70,45.80,42.20,41.80, 45.00,45.00,47.00,43.00,40.50,
                       45.50,47.40,43.00,41.44,37.95, 42.87,44.24,42.25,41.15,37.82],
    "PCR (%)":      [87.75,90.20,91.91,75.02,76.50, 70.00,73.00,76.00,74.00,67.86,
                     77.70,79.20,82.80,80.30,81.00, 72.00,75.00,81.00,79.00,78.50,
                     80.14,81.60,86.90,95.39,96.82, 81.80,88.71,92.43,93.30,94.75],
    "Credit-Deposit Ratio (%)": [66.54,67.48,72.32,75.34,77.35, 84.85,87.79,84.98,104.42,96.50,
                                  78.68,80.69,86.35,83.83,83.32, 88.18,86.12,89.27,90.31,89.83,
                                  66.83,68.50,69.05,71.79,71.28, 73.04,74.30,78.17,78.60,78.97],
    "Debt-Equity Ratio": [1.64,1.52,1.51,1.58,1.28, 0.67,0.79,0.74,1.52,1.32,
                          0.62,0.63,0.59,0.55,0.53, 1.41,1.61,1.49,1.28,1.18,
                          0.49,0.46,0.55,0.52,0.47, 1.21,1.67,1.22,1.12,0.97],
})

# ═══════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════
def smart_normalize(df):
    df = df.copy()
    for col, thr in [("Net NPA (%)",0.10),("CAR (%)",2.0),("CASA Ratio (%)",2.0),("PCR (%)",2.0)]:
        if col in df.columns:
            df[col] = df.groupby("Bank")[col].transform(
                lambda g, t=thr: g*100 if g.median() < t else g)
    return df

def score_bank(row, p, appetite, extras):
    w = {"Conservative":3,"Balanced":2,"Aggressive":1}[appetite]
    s = 0
    if row.get("Net NPA (%)", 999) <= p["npa"]: s += w
    if row.get("ROA (%)",       0) >= p["roa"]: s += 2
    if row.get("CAR (%)",       0) >= p["car"]: s += 2
    for key, col, hi in extras:
        v = row.get(col)
        if v is not None and pd.notna(v):
            s += 1 if (v >= p[key] if hi else v <= p[key]) else 0
    return s

def max_score(appetite, extras):
    return {"Conservative":3,"Balanced":2,"Aggressive":1}[appetite] + 4 + len(extras)

def tier_of(score, ms):
    r = score/ms if ms else 0
    if r >= 0.80: return "🥇 Tier-1 (Prime)"
    if r >= 0.55: return "⚖️ Tier-2 (Stable)"
    return "🚨 Tier-3 (Watch)"

def tier_pill(t):
    if "1" in t: return '<span class="t1p">Prime</span>'
    if "2" in t: return '<span class="t2p">Stable</span>'
    return '<span class="t3p">Watch</span>'

def colored_val(v, tgt, hi=True):
    ok = v >= tgt if hi else v <= tgt
    c  = "#6ee7b7" if ok else "#fca5a5"
    return f'<span class="mono" style="color:{c}">{v:.2f}%</span>'

def load_excel(f):
    try:
        df = pd.read_excel(f, sheet_name="Ratio Analysis")
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"❌ Cannot read sheet **'Ratio Analysis'**: {e}"); st.stop()
    req = {"Bank","Year","Net NPA (%)","ROA (%)","CAR (%)"}
    miss = req - set(df.columns)
    if miss:
        st.error(f"❌ Missing columns: **{', '.join(sorted(miss))}**"); st.stop()
    for c in ["Net NPA (%)","ROA (%)","CAR (%)","CASA Ratio (%)","PCR (%)",
              "Credit-Deposit Ratio (%)","Debt-Equity Ratio"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Net NPA (%)","ROA (%)","CAR (%)"]).copy()
    df["Year"] = df["Year"].astype(str).str.strip()
    if df.empty:
        st.error("❌ No valid rows after removing blanks."); st.stop()
    return smart_normalize(df)

# ═══════════════════════════════════════════
# PDF EXTRACTOR — comprehensive + calculation
# ═══════════════════════════════════════════
def _grab(patterns, text, fix_decimal=False):
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if m:
            try:
                v = float(str(m.group(1)).replace(",","").strip())
                if fix_decimal and 0 < v < 0.1: v *= 100
                return round(v, 4)
            except Exception:
                pass
    return None

def _bank_name(text):
    BANKS = [("state bank of india","SBI"),("sbi","SBI"),
             ("hdfc bank","HDFC"),("hdfc","HDFC"),
             ("icici bank","ICICI"),("icici","ICICI"),
             ("axis bank","AXIS"),
             ("punjab national bank","PNB"),("pnb","PNB"),
             ("bank of baroda","BOB"),("kotak mahindra","Kotak"),
             ("indusind","IndusInd"),("yes bank","Yes Bank"),
             ("canara bank","Canara"),("union bank","Union Bank"),
             ("indian bank","Indian Bank"),("bank of india","Bank of India")]
    t = text[:5000].lower()
    for pat, name in BANKS:
        if pat in t: return name
    return "Unknown Bank"

def _fy(text):
    for pat in [r"annual report\s+(\d{4}[-–]\d{2,4})",
                r"fy\s*(\d{4}[-–]\d{2,4})",
                r"31\s*(?:st\s*)?march[\s,]+(\d{4})",
                r"march\s+31[,\s]+(\d{4})",
                r"year ended.*?march.*?(\d{4})"]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            yr = re.sub(r"[-–](\d{2})$", lambda x: f"-{2000+int(x.group(1))}", str(m.group(1)))
            return yr if yr.upper().startswith("FY") else f"FY {yr}"
    m = re.search(r"march\s+(\d{4})", text, re.IGNORECASE)
    if m:
        y = int(m.group(1)); return f"FY {y-1}-{y}"
    return "FY Unknown"

def _extract_ratios_from_text(text):
    """Extract ratios directly stated in the report."""
    r = {}

    # Net NPA — many formats: ratio %, table style, decimal
    npa = _grab([
        r"net\s+npa\s*(?:ratio|%|\(%\))?\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%",
        r"net\s+npa\s*\(%\)\s+([0-9]+\.?[0-9]*)",
        r"net\s+n\.?p\.?a\.?\s*[:\-\s]*([0-9]+\.?[0-9]*)\s*%",
        r"nnpa\s*[:\-%\s]+([0-9]+\.?[0-9]*)\s*%?",
        r"net\s+npa.*?(\d+\.\d+)\s*%",
    ], text, fix_decimal=True)
    if npa is not None: r["Net NPA (%)"] = npa

    # ROA
    roa = _grab([
        r"return\s+on\s+(?:average\s+)?assets?\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%",
        r"\broa\b\s*\(%\)?\s*[:\-]?\s*([0-9]+\.?[0-9]*)",
        r"return\s+on\s+assets?\s*\(%\)\s+([0-9]+\.?[0-9]*)",
        r"return\s+on\s+average\s+assets\s*[:\-\s]+([0-9]+\.?[0-9]*)",
    ], text)
    if roa is not None: r["ROA (%)"] = roa*100 if roa < 0.05 else roa

    # CAR / CRAR — comprehensive patterns for all Indian bank annual report formats
    car = _grab([
        r"capital\s+adequacy\s+ratio\s*(?:\(basel\s+[iii3]+\))?\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%",
        r"c\.?r\.?a\.?r\.?\s*(?:\(basel\s+[iii3]+\))?\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%",
        r"total\s+c\.?r\.?a\.?r\.?\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%",
        r"\bcar\b\s*\(%\)?\s*[:\-]?\s*([0-9]+\.?[0-9]*)",
        r"capital\s+adequacy\s+ratio\s*\(%\)\s+([0-9]+\.?[0-9]*)",
        r"overall\s+crar\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%?",
        r"capital\s+adequacy\s+ratio\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s",
        r"total\s+capital\s+(?:adequacy\s+)?ratio\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%",
        r"crar\s*\(%\)\s+([0-9]+\.?[0-9]*)",
    ], text)
    if car is not None: r["CAR (%)"] = car*100 if car < 1.0 else car

    casa = _grab([
        r"casa\s+ratio\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%",
        r"casa\s*\(%\)\s+([0-9]+\.?[0-9]*)",
        r"casa\s+ratio\s*\(%\)\s+([0-9]+\.?[0-9]*)",
        r"current\s+&?\s*savings?\s+(?:account\s+)?ratio.*?([0-9]+\.?[0-9]*)\s*%",
    ], text)
    if casa is not None: r["CASA Ratio (%)"] = casa*100 if casa < 1.0 else casa

    # PCR
    pcr = _grab([
        r"provision\s+coverage\s+ratio\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%",
        r"\bpcr\b\s*\(%\)?\s*[:\-]?\s*([0-9]+\.?[0-9]*)",
        r"provision\s+coverage\s+ratio\s*\(%\)\s+([0-9]+\.?[0-9]*)",
        r"provisioning\s+coverage.*?([0-9]+\.?[0-9]*)\s*%",
    ], text)
    if pcr is not None: r["PCR (%)"] = pcr*100 if pcr < 1.0 else pcr

    # Credit-Deposit Ratio
    cdr = _grab([
        r"credit[\s\-]deposit\s+ratio\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%",
        r"\bcdr\b\s*[:\-]?\s*([0-9]+\.?[0-9]*)\s*%",
        r"advances?\s+to\s+deposits?\s+ratio.*?([0-9]+\.?[0-9]*)\s*%",
    ], text)
    if cdr is not None: r["Credit-Deposit Ratio (%)"] = cdr

    return r

def _calc_from_balance_sheet(text):
    """
    Calculate financial ratios from raw balance sheet figures.
    Covers: ROA, CDR, D/E, CASA%, PCR%, Net NPA%
    Used when ratios are not directly stated in the report.
    """
    def g(pats):
        for pat in pats:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                try:
                    v = float(str(m.group(1)).replace(",",""))
                    return v if v > 0 else None
                except Exception:
                    pass
        return None

    assets    = g([r"total assets[^\d\n]{0,35}([0-9,]{5,})",
                   r"balance sheet (?:total|size)[^\d\n]{0,25}([0-9,]{5,})"])
    profit    = g([r"net profit (?:after tax|for the year|pat)[^\d\n]{0,25}([0-9,]{3,})",
                   r"profit after tax[^\d\n]{0,25}([0-9,]{3,})",
                   r"net profit[^\d\n]{0,20}([0-9,]{3,})"])
    deposits  = g([r"total deposits[^\d\n]{0,25}([0-9,]{5,})",
                   r"aggregate deposits[^\d\n]{0,25}([0-9,]{5,})"])
    advances  = g([r"net advances[^\d\n]{0,25}([0-9,]{5,})",
                   r"net loans and advances[^\d\n]{0,25}([0-9,]{5,})",
                   r"total advances[^\d\n]{0,25}([0-9,]{5,})"])
    equity    = g([r"shareholders(?:'|.s?) (?:funds?|equity)[^\d\n]{0,25}([0-9,]{4,})",
                   r"net worth[^\d\n]{0,25}([0-9,]{4,})",
                   r"total equity[^\d\n]{0,25}([0-9,]{4,})"])
    curr_dep  = g([r"current (?:account )?deposits?[^\d\n]{0,25}([0-9,]{3,})"])
    sav_dep   = g([r"savings? (?:bank )?deposits?[^\d\n]{0,25}([0-9,]{3,})",
                   r"savings deposits?[^\d\n]{0,20}([0-9,]{3,})"])
    gross_npa = g([r"gross n\.?p\.?a\.?[^\d\n]{0,25}([0-9,]{3,})",
                   r"gross non.performing assets?[^\d\n]{0,25}([0-9,]{3,})"])
    net_npa_a = g([r"net n\.?p\.?a\.? (?!ratio|%)[^\d\n]{0,25}([0-9,]{3,})"])
    provisions= g([r"provisions? (?:and contingencies?|for npa|against npa)[^\d\n]{0,25}([0-9,]{3,})",
                   r"npa provisions?[^\d\n]{0,20}([0-9,]{3,})"])

    calc = {}

    if assets and profit and assets > 0:
        calc["ROA (%)"] = round(profit / assets * 100, 4)

    if advances and deposits and deposits > 0:
        calc["Credit-Deposit Ratio (%)"] = round(advances / deposits * 100, 4)

    if assets and equity and equity > 0:
        calc["Debt-Equity Ratio"] = round((assets - equity) / equity, 4)

    if curr_dep and sav_dep and deposits and deposits > 0:
        casa = (curr_dep + sav_dep) / deposits * 100
        if 5 <= casa <= 90:
            calc["CASA Ratio (%)"] = round(casa, 4)

    if provisions and gross_npa and gross_npa > 0:
        pcr = provisions / gross_npa * 100
        if 30 <= pcr <= 100:
            calc["PCR (%)"] = round(pcr, 4)

    if net_npa_a and advances and advances > 0:
        nnpa = net_npa_a / advances * 100
        if 0 < nnpa < 30:
            calc["Net NPA (%)"] = round(nnpa, 4)

    return calc

def extract_pdf(pdf_bytes):
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            total = len(pdf.pages)
            # Smart sampling: read first 20 + last 30 pages (balance sheet is usually at end)
            # This covers ~90% of ratio data at 3-5x speed
            first = list(range(min(20, total)))
            last  = list(range(max(0, total-30), total))
            pages_to_read = sorted(set(first + last))
            for idx in pages_to_read:
                t = pdf.pages[idx].extract_text()
                if t:
                    text += t + "\n"
    except Exception:
        return {}
    if not text.strip():
        return {}

    result = {"bank": _bank_name(text), "year": _fy(text)}

    # Step 1: Try to extract stated ratios
    ratios = _extract_ratios_from_text(text)
    result.update(ratios)

    # Step 2: Fill missing values by calculating from balance sheet
    calc = _calc_from_balance_sheet(text)
    for k, v in calc.items():
        if k not in result:    # only fill if not already found
            result[k] = v

    return result

def process_pdfs(files):
    rows = []
    n_files = len(files)
    progress   = st.progress(0.0, text="Starting PDF extraction…")
    status_box = st.empty()
    for i, f in enumerate(files):
        pct_start = i / n_files
        pct_done  = (i + 1) / n_files
        pct_int   = int(pct_start * 100)
        progress.progress(pct_start, text=f"{pct_int}% — Reading: {f.name}")
        status_box.markdown(
            f'<div style="font-family:JetBrains Mono,monospace;font-size:10.5px;'
            f'color:#6e82a0;padding:4px 0;">'
            f'📄 File {i+1}/{n_files} &nbsp;·&nbsp; '
            f'<span style="color:#a78bfa">{f.name}</span></div>',
            unsafe_allow_html=True,
        )
        data = extract_pdf(f.read())
        progress.progress(pct_done, text=f"{int(pct_done*100)}% — Done: {f.name}")
        if not data:
            st.warning(f"⚠ **{f.name}**: No text extracted. Likely a scanned/image PDF.")
            continue
        bank = data.pop("bank", "Unknown")
        year = data.pop("year", "FY Unknown")
        if not data:
            st.warning(f"⚠ **{f.name}** ({bank}, {year}): No financial ratios detected.")
            continue
        rows.append({"Bank": bank, "Year": year, **data})
    progress.progress(1.0, text="100% — Extraction complete ✓")
    import time; time.sleep(0.4)
    progress.empty()
    status_box.empty()

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).sort_values(["Bank","Year"]).reset_index(drop=True)
    # Ensure numeric
    for c in ["Net NPA (%)","ROA (%)","CAR (%)","CASA Ratio (%)","PCR (%)","Credit-Deposit Ratio (%)","Debt-Equity Ratio"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# ═══════════════════════════════════════════
# CHART BUILDERS
# ═══════════════════════════════════════════
def line_chart(df, ycol, title, thr=None, thr_lbl="", thr_color="#f87171"):
    fig = go.Figure()
    for i, bk in enumerate(df["Bank"].unique()):
        sub = df[df["Bank"]==bk].sort_values("Year")
        bc  = bcolor(bk, i)
        fig.add_trace(go.Scatter(
            x=sub["Year"], y=sub[ycol], name=bk, mode="lines+markers",
            line=dict(color=bc, width=2.3),
            marker=dict(size=6.5, color=bc, line=dict(color="#080c16", width=1.5)),
            hovertemplate=f"<b>{bk}</b><br>%{{x}}<br>{ycol}: %{{y:.2f}}<extra></extra>",
        ))
    if thr is not None:
        fig.add_hline(y=thr, line_dash="dot", line_color=thr_color, line_width=1.4,
                      annotation=dict(text=f" {thr_lbl}", font=dict(color=thr_color, size=10), x=0))
    apply_layout(fig, {"title": title, "height": 295, "xaxis": AX_X, "yaxis": AX_Y,
                        "margin": dict(l=6, r=6, t=40, b=55),
                        "legend": dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#6e82a0"),
                                       orientation="h", y=-0.30, x=.5, xanchor="center")})
    return fig

def bar_chart(df, xcol, ycol, title, thr=None, thr_lbl="", good_above=True, thr_color="#f87171"):
    banks = df[xcol].tolist()
    clrs = []
    for i, v in enumerate(df[ycol]):
        if thr is not None:
            clrs.append("#34d399" if (v >= thr if good_above else v <= thr) else "#f87171")
        else:
            clrs.append(bcolor(str(banks[i]), i))
    fig = go.Figure(go.Bar(
        x=df[xcol], y=df[ycol],
        marker=dict(color=clrs, line=dict(color="rgba(0,0,0,0)")),
        text=[f"{v:.2f}" for v in df[ycol]], textposition="outside",
        textfont=dict(size=10, color="#6e82a0"),
        hovertemplate=f"<b>%{{x}}</b><br>{ycol}: %{{y:.2f}}<extra></extra>",
    ))
    if thr is not None:
        fig.add_hline(y=thr, line_dash="dot", line_color=thr_color, line_width=1.4,
                      annotation=dict(text=f" {thr_lbl}", font=dict(color=thr_color, size=10), x=0))
    ymax = df[ycol].max()
    apply_layout(fig, {"title": title, "height": 295, "showlegend": False, "xaxis": AX_X,
                        "yaxis": {**AX_Y, "range": [0, ymax*1.25] if not np.isnan(ymax) else None}})
    return fig

def hbar_chart(df, ycol, xcol, title, thr=None, good_below=True, thr_color="#f87171"):
    clrs = ["#34d399" if (v <= thr if good_below else v >= thr) else "#f87171"
            for v in df[xcol]] if thr is not None else [bcolor(b, i) for i, b in enumerate(df[ycol])]
    fig = go.Figure(go.Bar(
        x=df[xcol], y=df[ycol], orientation="h",
        marker=dict(color=clrs, line=dict(color="rgba(0,0,0,0)")),
        text=[f"{v:.2f}%" for v in df[xcol]], textposition="outside",
        textfont=dict(size=10, color="#6e82a0"),
        hovertemplate=f"<b>%{{y}}</b><br>{xcol}: %{{x:.2f}}<extra></extra>",
    ))
    if thr is not None:
        fig.add_vline(x=thr, line_dash="dot", line_color=thr_color, line_width=1.4)
    apply_layout(fig, {"title": title, "height": 295, "showlegend": False,
                        "xaxis": {**AX_X, "range": [0, max(df[xcol])*1.35]},
                        "yaxis": AX_Y_CLEAN,
                        "margin": dict(l=6, r=60, t=40, b=8)})
    return fig

def donut_chart(labels, values, colors, title):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors, line=dict(color="#080c16", width=3)),
        textinfo="percent+label", textfont=dict(size=11, color="#c8d4e8"),
        pull=[0.03]*len(labels),
        hovertemplate="<b>%{label}</b><br>%{value} bank(s) · %{percent}<extra></extra>",
    ))
    total = sum(values)
    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:10px'>Banks</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(color="#ecf0ff", size=15),
    )
    apply_layout(fig, {"title": title, "showlegend": False, "height": 290,
                        "margin": dict(l=8, r=8, t=38, b=8)})
    return fig

def scatter_chart(lat, p, ms, latest_fy):
    fig = go.Figure()
    nm   = lat["Net NPA (%)"].max()
    rm   = lat["ROA (%)"].max()
    nmax = max(nm*1.35, p["npa"]*3, 0.5)
    rmax = max(rm*1.35, p["roa"]*3, 0.5)
    fig.add_shape(type="rect", x0=0, x1=p["npa"], y0=p["roa"], y1=rmax,
                  fillcolor="rgba(52,211,153,.04)", line_color="rgba(0,0,0,0)")
    fig.add_shape(type="rect", x0=p["npa"], x1=nmax, y0=0, y1=p["roa"],
                  fillcolor="rgba(248,113,113,.04)", line_color="rgba(0,0,0,0)")
    for i, (_, row) in enumerate(lat.iterrows()):
        bc  = bcolor(row["Bank"], i)
        car_val = row.get("CAR (%)", 15)
        car_val = 15 if (car_val is None or (isinstance(car_val, float) and np.isnan(car_val))) else float(car_val)
        sz  = max(car_val * 2.5, 12)
        npa_v = row["Net NPA (%)"] if pd.notna(row.get("Net NPA (%)")) else 0
        roa_v = row["ROA (%)"]     if pd.notna(row.get("ROA (%)"))     else 0
        car_disp = f"{car_val:.2f}%" if car_val != 15 or "CAR (%)" in row else "N/A"
        fig.add_trace(go.Scatter(
            x=[npa_v], y=[roa_v],
            mode="markers+text", name=row["Bank"],
            marker=dict(size=sz, color=bc, opacity=.82, line=dict(color="#080c16", width=2)),
            text=[row["Bank"]], textposition="top center",
            textfont=dict(size=9.5, color="#6e82a0"), showlegend=False,
            hovertemplate=(f"<b>{row['Bank']}</b><br>"
                           f"Net NPA: {npa_v:.2f}%<br>"
                           f"ROA: {roa_v:.2f}%<br>"
                           f"CAR: {car_disp}<br>"
                           f"Score: {row['Score']}/{ms}<extra></extra>"),
        ))
    fig.add_vline(x=p["npa"], line_dash="dot", line_color="rgba(248,113,113,.4)", line_width=1.2)
    fig.add_hline(y=p["roa"], line_dash="dot", line_color="rgba(167,139,250,.4)", line_width=1.2)
    apply_layout(fig, {
        "title": f"Risk-Return Matrix · NPA vs ROA — bubble = CAR · {latest_fy}",
        "height": 320, "xaxis": {**AX_X, "title": "Net NPA (%)"},
        "yaxis": {**AX_Y, "title": "ROA (%)"},
    })
    return fig

def radar_chart(lat, latest_fy):
    cfg = [("Net NPA (%)","NPA Quality",False),("ROA (%)","Profitability",True),("CAR (%)","Capital",True)]
    if "CASA Ratio (%)" in lat.columns: cfg.append(("CASA Ratio (%)","CASA",True))
    if "PCR (%)"        in lat.columns: cfg.append(("PCR (%)","Prov. Cover.",True))
    labels=[c[1] for c in cfg]; keys=[c[0] for c in cfg]; hi=[c[2] for c in cfg]

    def norm(series, higher):
        mn,mx = series.min(),series.max()
        rng = mx-mn if mx!=mn else 1
        s = (series-mn)/rng*100
        return 100-s if not higher else s

    fig = go.Figure()
    for i,(_, row) in enumerate(lat.iterrows()):
        vals = [norm(lat[k],h)[row.name] for k,h in zip(keys,hi)]
        bc   = bcolor(row["Bank"],i)
        fig.add_trace(go.Scatterpolar(
            r=vals+[vals[0]], theta=labels+[labels[0]],
            fill="toself", name=row["Bank"],
            line=dict(color=bc, width=2),
            fillcolor=hex_rgba(bc, 0.09),   # FIXED: proper rgba instead of hex+2chars
            hovertemplate=f"<b>{row['Bank']}</b><br>%{{theta}}: %{{r:.0f}}/100<extra></extra>",
        ))
    layout = {**BASE,
              "title": f"Performance Radar · {latest_fy}  (100 = best in cohort)",
              "height": 380,
              "legend": dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10.5, color="#6e82a0"),
                             orientation="h", y=-0.08, x=.5, xanchor="center"),
              "polar": dict(
                  bgcolor="rgba(0,0,0,0)",
                  radialaxis=dict(visible=True, range=[0,100], gridcolor="rgba(255,255,255,.04)",
                                  linecolor="rgba(255,255,255,.04)",
                                  tickfont=dict(size=8, color="#2e3f57"), tickvals=[25,50,75,100]),
                  angularaxis=dict(gridcolor="rgba(255,255,255,.06)", linecolor="rgba(255,255,255,.06)",
                                   tickfont=dict(size=10.5, color="#6e82a0")),
              )}
    fig.update_layout(**layout)
    return fig

def heatmap_chart(df, ms):
    pivot = df.pivot_table(index="Bank", columns="Year", values="Score", aggfunc="mean")
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale=[[0,"#1b0535"],[.3,"#5b21b6"],[.6,"#1d4ed8"],[1,"#a78bfa"]],
        zmin=0, zmax=ms,
        text=pivot.values, texttemplate="%{text:.1f}",
        textfont=dict(size=12, color="#e8ecff"),
        hovertemplate="<b>%{y}</b> · %{x}<br>Score: %{z:.1f}/"+str(ms)+"<extra></extra>",
    ))
    apply_layout(fig, {"title": f"Risk Score Heatmap — All Years  (max {ms})",
                        "height": 220+32*len(pivot.index),
                        "xaxis": {**AX_X, "title": "Financial Year"},
                        "yaxis": AX_Y_CLEAN,
                        "margin": dict(l=6,r=6,t=38,b=6)})
    return fig

# ═══════════════════════════════════════════
# ROA AREA CHART (separate to avoid fillcolor issue)
# ═══════════════════════════════════════════
def roa_area_chart(df, roa_tgt):
    fig = go.Figure()
    for i, bk in enumerate(df["Bank"].unique()):
        sub = df[df["Bank"]==bk].sort_values("Year")
        bc  = bcolor(bk, i)
        fig.add_trace(go.Scatter(
            x=sub["Year"], y=sub["ROA (%)"], name=bk, mode="lines+markers",
            line=dict(color=bc, width=2.3),
            marker=dict(size=6.5, color=bc, line=dict(color="#080c16", width=1.5)),
            fill="tozeroy",
            fillcolor=hex_rgba(bc, 0.07),   # FIXED: proper rgba
            hovertemplate=f"<b>{bk}</b><br>%{{x}}<br>ROA: %{{y:.2f}}%<extra></extra>",
        ))
    fig.add_hline(y=roa_tgt, line_dash="dot", line_color="#a78bfa", line_width=1.4,
                  annotation=dict(text=f" Target {roa_tgt}%", font=dict(color="#a78bfa", size=10), x=0))
    apply_layout(fig, {"title": "Return on Assets (%) — All Banks",
                        "height": 295, "xaxis": AX_X, "yaxis": AX_Y,
                        "margin": dict(l=6, r=6, t=40, b=55),
                        "legend": dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#6e82a0"),
                                       orientation="h", y=-0.30, x=.5, xanchor="center")})
    return fig

# ═══════════════════════════════════════════
# ANALYSIS TEXT
# ═══════════════════════════════════════════
def build_analysis(df, lat, srt, p, appetite, ms, latest_fy):
    top  = srt.iloc[0]
    n    = len(srt)
    t1   = srt[srt["Tier"]=="🥇 Tier-1 (Prime)"]["Bank"].tolist()
    t3   = srt[srt["Tier"]=="🚨 Tier-3 (Watch)"]["Bank"].tolist()
    avg_npa = lat["Net NPA (%)"].mean()
    avg_roa = lat["ROA (%)"].mean()
    avg_car = lat["CAR (%)"].mean()

    best_bk, best_d = None, None
    for bk in df["Bank"].unique():
        sub = df[df["Bank"]==bk].sort_values("Year")
        if len(sub) >= 2:
            d = sub["Net NPA (%)"].iloc[0] - sub["Net NPA (%)"].iloc[-1]
            if best_d is None or d > best_d: best_bk, best_d = bk, d

    # Safe stat helpers — handle all-NaN columns gracefully
    def safe_stat_bank(col, func):
        sub = lat[lat[col].notna()]
        if sub.empty: return "N/A"
        idx = getattr(sub[col], func)()
        return sub.loc[idx, "Bank"]

    worst_npa = safe_stat_bank("Net NPA (%)", "idxmax")
    best_roa  = safe_stat_bank("ROA (%)",     "idxmax")
    worst_car = safe_stat_bank("CAR (%)",     "idxmin")
    npa_ok  = (not np.isnan(avg_npa)) and avg_npa <= p["npa"]
    car_ok  = (not np.isnan(avg_car)) and avg_car >= p["car"]

    cards = [
        {"n":"01 · Strategic Leader",
         "t": f"{top['Bank']} — Top Performer · {latest_fy}",
         "b": (f"Under the <b>{appetite}</b> model, <b>{top['Bank']}</b> leads with score <b>{top['Score']}/{ms}</b>. "
               f"Net NPA: <b>{'N/A' if pd.isna(top.get('Net NPA (%)')) else f"{top['Net NPA (%)']:.2f}%"}</b>, "
               f"ROA: <b>{'N/A' if pd.isna(top.get('ROA (%)')) else f"{top['ROA (%)']:.2f}%"}</b>, "
               f"CAR: <b>{'N/A' if pd.isna(top.get('CAR (%)')) else f"{top['CAR (%)']:.2f}%"}</b>. "
               f"Demonstrates strong asset quality and capital adequacy.")},
        {"n":"02 · Tier Classification",
         "t": f"Prime: {len(t1)} · Stable: {n-len(t1)-len(t3)} · Watch: {len(t3)}",
         "b": (f"<b class='ok'>Prime entities:</b> {', '.join(t1) or 'None'} — all benchmarks met. "
               + (f"<b class='wn'>Watch list:</b> {', '.join(t3)} — one or more pillars breach thresholds. "
                  if t3 else "No watch-listed banks under current parameters. ")
               + f"Prime rate: <b>{len(t1)/n*100:.0f}%</b> of cohort.")},
        {"n":"03 · Asset Quality Trend",
         "t": f"Sector NPA {avg_npa:.2f}% — {'Within' if npa_ok else 'Above'} Tolerance",
         "b": (f"Sector NPA is <b>{'<span class=ok>within</span>' if npa_ok else '<span class=wn>above</span>'}</b> "
               f"the {p['npa']}% limit. "
               + (f"<b>{best_bk}</b> shows the strongest improvement: NPA reduced by <b>{best_d:.2f} pp</b> "
                  f"over the study period. " if best_bk else "")
               + f"<b class='wn'>{worst_npa}</b> has the highest NPA at "
               f"<b>{lat.loc[lat['Bank']==worst_npa,'Net NPA (%)'].values[0]:.2f}%</b>.")},
        {"n":"04 · Capital & Profitability",
         "t": f"{'Mean CAR ' + f"{avg_car:.2f}%" if not np.isnan(avg_car) else 'CAR N/A'} · Best ROA: {best_roa}",
         "b": (f"{'Mean CAR <b>' + ('<span class=ok>exceeds</span>' if car_ok else '<span class=wn>below</span>') + '</b> the Basel III floor of ' + str(p["car"]) + '%.' if not np.isnan(avg_car) else 'CAR data not available in this report.'} "
               f"{'<b>' + str(best_roa) + '</b> leads ROA at <b>' + f"{lat.loc[lat['Bank']==best_roa,'ROA (%)'].values[0]:.2f}%" + '</b>.' if best_roa != 'N/A' and not lat[lat['Bank']==best_roa]['ROA (%)'].isna().all() else ''} "
               f"{'<b class=wn>' + str(worst_car) + '</b> has the lowest CAR: <b>' + f"{lat.loc[lat['Bank']==worst_car,'CAR (%)'].values[0]:.2f}%" + '</b>.' if worst_car != 'N/A' and not lat[lat['Bank']==worst_car]['CAR (%)'].isna().all() else ''}")},
    ]

    # Written paragraph analysis
    trend_dir = "improving" if (df.groupby("Year")["Net NPA (%)"].mean().is_monotonic_decreasing) else "mixed"
    written = f"""
<h4>Written Analysis</h4>
<p>The credit risk assessment of the selected Indian commercial banks for <b>{latest_fy}</b> under
the <b>{appetite}</b> risk appetite model reveals a <b>sector average Net NPA of {'N/A' if np.isnan(avg_npa) else f"{avg_npa:.2f}%"}</b>,
which is {'within' if npa_ok else 'above'} the prescribed tolerance of {p['npa']}%.
The asset quality trend across the study period appears <b>{trend_dir}</b>,
reflecting the impact of RBI's regulatory measures and post-pandemic credit normalisation.</p>

<p><b>{top['Bank']}</b> emerges as the strategic leader with a model score of {top['Score']}/{ms},
demonstrating well-balanced performance across NPA, ROA, and CAR metrics.
{'Private sector banks (ICICI, HDFC, Axis) generally outperform public sector counterparts on profitability, consistent with the findings of Brahmaiah (2022) who documented persistent PSB–PVB performance gaps.' if n > 3 else ''}</p>

<p>Capital adequacy {'remains broadly adequate at a sector mean of <b>' + f"{avg_car:.2f}%" + '</b>, ' + ('comfortably exceeding' if car_ok else 'marginally below') + ' the Basel III minimum.' if not np.isnan(avg_car) else 'data was not extractable from the uploaded report for the CAR metric.'}.
{'The declining CASA ratio trend warrants monitoring as it signals a gradual rise in the cost of deposits, which may compress net interest margins in the medium term.' if 'CASA Ratio (%)' in lat.columns else ''}
{f'PNB and BOB have demonstrated significant NPA recovery velocity, consistent with the balance-sheet rehabilitation observed post the asset quality review cycle.' if all(b in df["Bank"].values for b in ["PNB","BOB"]) else ''}</p>

<p><b>Strategic Recommendations:</b>
{'Banks in the Tier-3 Watch category should prioritise provision top-ups, strengthen credit appraisal frameworks, and explore one-time settlement schemes for legacy NPAs. ' if t3 else 'All banks are within acceptable parameters. '}
The sector should focus on CASA mobilisation through digital channels to maintain low-cost funding bases, and maintain capital buffers well above the regulatory minimum to support future credit growth aligned with India's economic expansion trajectory.</p>
"""

    return cards, written

# ═══════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-badge"></div>
  <div class="hero-title">Strategic <span>Credit Risk</span> Intelligence</div>
  <div class="hero-sub">Financial Ratio Analysis &amp; Data Analytics</div>
  <div class="hero-line"></div>
  <div class="hero-credit">Developed by: Apsara Mitra &nbsp</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="background:rgba(167,139,250,.07);border:1px solid rgba(167,139,250,.18);
      border-radius:9px;padding:12px 15px;margin-bottom:14px;text-align:center;">
      <div style="font-size:14px;font-weight:700;color:#ecf0ff;margin-bottom:2px;">📊 Risk Terminal</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:8.5px;color:#3f5270;letter-spacing:1px;">CREDIT ANALYTICS · INDIAN BANKS</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Input Mode")
    # FIXED: non-empty label with label_visibility='collapsed'
    mode = st.radio(
        "Select input mode",
        ["📊 Built-in Dataset", "📁 Upload Excel", "📄 Upload PDF Reports"],
        index=0, label_visibility="collapsed",
    )

    excel_file = None
    pdf_files  = None
    if mode == "📁 Upload Excel":
        excel_file = st.file_uploader("Excel (.xlsx)", type=["xlsx"])
        st.caption("Sheet: 'Ratio Analysis' | Required: Bank, Year, Net NPA (%), ROA (%), CAR (%)")
    elif mode == "📄 Upload PDF Reports":
        pdf_files = st.file_uploader(
            "Annual Report PDFs (one or more)", type=["pdf"],
            accept_multiple_files=True,
        )
        st.markdown("""<div class="pdf-info">
          Upload digital annual reports (text-based PDFs).<br>
          Ratios are <b>auto-extracted</b> and <b>calculated</b> from balance sheet data.<br>
          Bank name &amp; financial year are detected automatically.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Benchmark Thresholds")
    npa  = st.slider("Net NPA Tolerance (%)",   0.0,  6.0,  1.0, 0.1)
    roa  = st.slider("Target ROA (%)",           0.0,  3.0,  1.2, 0.1)
    car  = st.slider("Min CAR — Basel III (%)", 10.0, 22.0, 15.0, 0.5)
    cdr  = st.slider("Max CDR (%)",             50.0,110.0, 80.0, 1.0)
    casa = st.slider("Min CASA Ratio (%)",      25.0, 55.0, 38.0, 1.0)
    pcr  = st.slider("Min PCR (%)",             50.0,100.0, 70.0, 1.0)
    de   = st.slider("Max D/E Ratio",            2.0, 20.0, 12.0, 0.5)

    st.markdown("---")
    st.markdown("### Risk Appetite")
    # FIXED: non-empty label
    appetite = st.select_slider(
        "Risk Appetite Model",
        options=["Conservative", "Balanced", "Aggressive"],
        value="Balanced",
        label_visibility="collapsed",
    )
    aw = {"Conservative":"NPA weight = 3 (strict asset quality focus)",
          "Balanced":     "NPA weight = 2 (balanced across all pillars)",
          "Aggressive":   "NPA weight = 1 (growth over asset quality)"}
    st.caption(aw[appetite])

    st.markdown("---")
    load_btn = st.button("⚡ Load / Refresh Data", type="primary", width='stretch')
    st.caption("Sliders update all charts instantly — no reload needed.")

params = dict(npa=npa, roa=roa, car=car, cdr=cdr, casa=casa, pcr=pcr, de=de)

# ═══════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════
if load_btn or "df_loaded" not in st.session_state:
    with st.spinner("Loading data…"):
        if mode == "📊 Built-in Dataset":
            st.session_state["df_loaded"]  = BUILTIN.copy()
            st.session_state["src_label"]  = "Built-in · 6 Banks · FY 2020-21 to FY 2024-25"
        elif mode == "📁 Upload Excel":
            if not excel_file:
                st.error("Please upload an Excel file via the sidebar."); st.stop()
            st.session_state["df_loaded"]  = load_excel(excel_file)
            st.session_state["src_label"]  = f"Excel · {excel_file.name}"
        else:
            if not pdf_files:
                st.error("Please upload at least one PDF."); st.stop()
            df_pdf = process_pdfs(pdf_files)
            if df_pdf.empty:
                st.error("No financial data extracted. Ensure PDFs are text-based (not scanned images). "
                         "Switch to Excel mode for guaranteed accuracy."); st.stop()
            # Show what was extracted
            ext_cols = [c for c in ["Net NPA (%)","ROA (%)","CAR (%)","CASA Ratio (%)","PCR (%)","Credit-Deposit Ratio (%)","Debt-Equity Ratio"] if c in df_pdf.columns]
            found    = [c for c in ext_cols if df_pdf[c].notna().any()]
            missing  = [c for c in ["Net NPA (%)","ROA (%)","CAR (%)"] if c not in found]
            if missing:
                st.warning(f"⚠ Could not extract: **{', '.join(missing)}**. "
                           "These are required for scoring. The report may use non-standard formatting.")
                for mc in missing: df_pdf[mc] = np.nan
            st.success(f"✅ Extracted {len(df_pdf)} record(s) from {len(pdf_files)} PDF(s). "
                       f"Columns found: {', '.join(df_pdf.columns.tolist())}")
            st.session_state["df_loaded"]  = df_pdf
            st.session_state["src_label"]  = f"PDF · {len(pdf_files)} report(s)"

if "df_loaded" not in st.session_state:
    st.markdown("""
    <div class="offline-screen">
      <div class="oi">📡</div>
      <div class="oh">Terminal Offline</div>
      <div class="op">Select an input mode and click <b>Load / Refresh Data</b> to begin.</div>
      <div class="oc">
        MODE 1 · Built-in — 6 banks, FY2021–FY2025, no upload needed<br>
        MODE 2 · Excel    — Ratio Analysis sheet, any number of banks<br>
        MODE 3 · PDF      — Annual report PDFs, all ratios auto-extracted &amp; calculated
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

df_main   = st.session_state["df_loaded"]
src_label = st.session_state["src_label"]

# ═══════════════════════════════════════════
# SCORE COMPUTATION (live — every slider change)
# ═══════════════════════════════════════════
EXTRAS = []
if "Credit-Deposit Ratio (%)" in df_main.columns: EXTRAS.append(("cdr","Credit-Deposit Ratio (%)",False))
if "Debt-Equity Ratio"        in df_main.columns: EXTRAS.append(("de","Debt-Equity Ratio",False))
if "CASA Ratio (%)"           in df_main.columns: EXTRAS.append(("casa","CASA Ratio (%)",True))
if "PCR (%)"                  in df_main.columns: EXTRAS.append(("pcr","PCR (%)",True))

df   = df_main.copy()
ms   = max_score(appetite, EXTRAS)
df["Score"] = df.apply(lambda r: score_bank(r, params, appetite, EXTRAS), axis=1)
df["Tier"]  = df["Score"].apply(lambda s: tier_of(s, ms))

latest_fy = df["Year"].max()
lat  = df[df["Year"]==latest_fy].copy()
srt  = lat.sort_values("Score", ascending=False).reset_index(drop=True)
n    = len(srt)
years = sorted(df["Year"].unique().tolist())
t1c  = (srt["Tier"]=="🥇 Tier-1 (Prime)").sum()
t2c  = (srt["Tier"]=="⚖️ Tier-2 (Stable)").sum()
t3c  = (srt["Tier"]=="🚨 Tier-3 (Watch)").sum()
top  = srt.iloc[0]
avg_npa = lat["Net NPA (%)"].mean()
avg_roa = lat["ROA (%)"].mean()
avg_car = lat["CAR (%)"].mean()

# ═══════════════════════════════════════════
# STATUS BAR
# ═══════════════════════════════════════════
st.markdown(f"""
<div class="statusbar">
  <span><span class="live-dot"></span><b>LIVE</b> · {src_label}</span>
  <span>Latest: <b>{latest_fy}</b></span>
  <span>Banks: <b>{n}</b> · Periods: <b>{len(years)}</b></span>
  <span>Max score: <b>{ms}</b> · <b>{appetite}</b></span>
  <span style="color:#6ee7b7">■ Prime:{t1c}</span>
  <span style="color:#a78bfa">■ Stable:{t2c}</span>
  <span style="color:#f87171">■ Watch:{t3c}</span>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 01 — KPI CARDS
# ═══════════════════════════════════════════
st.markdown('<div class="sec-div">01 — Key Performance Indicators</div>', unsafe_allow_html=True)

def kpi(lbl, val, badge, bcls, meta, ac="#a78bfa"):
    return f"""<div class="kpi-card" style="--ac:{ac}">
      <div class="kpi-lbl">{lbl}</div>
      <div class="kpi-val">{val}</div>
      <span class="badge {bcls}">{badge}</span>
      <div class="kpi-meta">{meta}</div>
    </div>"""

k1,k2,k3,k4,k5 = st.columns(5)
for col, html in zip([k1,k2,k3,k4,k5], [
    kpi("Strategic Leader", top["Bank"], f"Score {top['Score']}/{ms}", "bb",
        f"{appetite} · {top['Tier'].split('(')[1].rstrip(')')}", "#a78bfa"),
    kpi("Sector Net NPA", f"{avg_npa:.2f}%",
        "✓ Within limit" if avg_npa<=npa else "✗ Exceeds limit",
        "bg" if avg_npa<=npa else "br",
        f"Limit {npa}% · {latest_fy}", "#60a5fa"),
    kpi("Sector ROA", f"{avg_roa:.2f}%",
        "✓ On target" if avg_roa>=roa else "✗ Below target",
        "bg" if avg_roa>=roa else "by",
        f"Target {roa}% · {latest_fy}", "#34d399"),
    kpi("Sector CAR", "N/A" if np.isnan(avg_car) else f"{avg_car:.2f}%",
        "N/A" if np.isnan(avg_car) else ("✓ Adequate" if avg_car>=car else "✗ Below floor"),
        "bb" if np.isnan(avg_car) else ("bg" if avg_car>=car else "br"),
        f"Basel III floor {car}%", "#fbbf24"),
    kpi("Prime Banks", f"{t1c}/{n}",
        f"{t1c/n*100:.0f}% prime-rated" if n else "—",
        "bg" if n and t1c/n>=.5 else "by",
        f"Tier-1 count · {latest_fy}", "#34d399"),
]):
    col.markdown(html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 02 — ASSET QUALITY
# ═══════════════════════════════════════════
st.markdown('<div class="sec-div">02 — Asset Quality</div>', unsafe_allow_html=True)
c1, c2 = st.columns([3, 2])
with c1:
    st.markdown('<div class="ch-wrap">', unsafe_allow_html=True)
    npa_df = df[df["Net NPA (%)"].notna()]
    st.plotly_chart(line_chart(npa_df, "Net NPA (%)", "Net NPA (%) — Longitudinal Trend",
                               npa, f"Limit {npa}%", "#f87171"),
                    width='stretch', config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    npa_rank = lat[lat["Net NPA (%)"].notna()].sort_values("Net NPA (%)")
    st.markdown('<div class="ch-wrap">', unsafe_allow_html=True)
    if not npa_rank.empty:
        st.plotly_chart(hbar_chart(npa_rank, "Bank", "Net NPA (%)",
                                   f"NPA Ranking · {latest_fy}", npa, True, "#f87171"),
                        width='stretch', config={"displayModeBar": False})
    else:
        st.info("Net NPA data not available.")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 03 — PROFITABILITY & CAPITAL
# ═══════════════════════════════════════════
st.markdown('<div class="sec-div">03 — Profitability &amp; Capital Adequacy</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)
with c3:
    st.markdown('<div class="ch-wrap">', unsafe_allow_html=True)
    # FIXED: use dedicated roa_area_chart with proper hex_rgba
    roa_df = df[df["ROA (%)"].notna()]
    st.plotly_chart(roa_area_chart(roa_df, roa),
                    width='stretch', config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
with c4:
    car_data = lat[lat["CAR (%)"].notna()].sort_values("CAR (%)", ascending=False)
    st.markdown('<div class="ch-wrap">', unsafe_allow_html=True)
    if not car_data.empty:
        st.plotly_chart(bar_chart(car_data, "Bank", "CAR (%)", f"Capital Adequacy · {latest_fy}",
                                  car, f"Floor {car}%", True, "#f87171"),
                        width='stretch', config={"displayModeBar": False})
    else:
        st.info("CAR data not available in uploaded PDFs. Upload Excel or use Built-in Dataset for full analysis.")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 04 — SCATTER + DONUT
# ═══════════════════════════════════════════
st.markdown('<div class="sec-div">04 — Risk-Return Matrix &amp; Tier Distribution</div>', unsafe_allow_html=True)
c5, c6 = st.columns([3, 2])
with c5:
    scatter_data = srt[srt["Net NPA (%)"].notna() & srt["ROA (%)"].notna()]
    st.markdown('<div class="ch-wrap">', unsafe_allow_html=True)
    if not scatter_data.empty:
        st.plotly_chart(scatter_chart(scatter_data, params, ms, latest_fy),
                        width='stretch', config={"displayModeBar": False})
    else:
        st.info("Insufficient data for risk-return matrix.")
    st.markdown('</div>', unsafe_allow_html=True)
with c6:
    tc = srt["Tier"].value_counts().reset_index()
    tc.columns = ["Tier","Count"]
    st.markdown('<div class="ch-wrap">', unsafe_allow_html=True)
    st.plotly_chart(donut_chart(tc["Tier"].tolist(), tc["Count"].tolist(),
                                [TIER_COLORS.get(t,"#8493a8") for t in tc["Tier"]],
                                f"Tier Distribution · {latest_fy}"),
                    width='stretch', config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 05 — RADAR
# ═══════════════════════════════════════════
if n >= 2:
    st.markdown('<div class="sec-div">05 — Comparative Performance Radar</div>', unsafe_allow_html=True)
    radar_data = srt[srt[["Net NPA (%)","ROA (%)","CAR (%)"]].notna().any(axis=1)]
    if len(radar_data) >= 2:
        st.markdown('<div class="ch-wrap">', unsafe_allow_html=True)
        st.plotly_chart(radar_chart(radar_data, latest_fy),
                        width='stretch', config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 06 — HEATMAP
# ═══════════════════════════════════════════
if len(years) >= 2 and n >= 2:
    st.markdown('<div class="sec-div">06 — Score Heatmap · All Years</div>', unsafe_allow_html=True)
    heat_df = df[df["Score"].notna()]
    if not heat_df.empty and heat_df["Score"].sum() > 0:
        st.markdown('<div class="ch-wrap">', unsafe_allow_html=True)
        st.plotly_chart(heatmap_chart(heat_df, ms),
                        width='stretch', config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 07 — EXTENDED METRICS
# ═══════════════════════════════════════════
ext_show = [c for c in ["CASA Ratio (%)","PCR (%)","Credit-Deposit Ratio (%)"] if c in df.columns]
if ext_show:
    st.markdown('<div class="sec-div">07 — Extended Metrics</div>', unsafe_allow_html=True)
    THR_MAP = {
        "CASA Ratio (%)":           (casa, True,  "#a78bfa", f"Min CASA {casa}%"),
        "PCR (%)":                  (pcr,  True,  "#60a5fa", f"Min PCR {pcr}%"),
        "Credit-Deposit Ratio (%)": (cdr,  False, "#f87171", f"Max CDR {cdr}%"),
    }
    ecols = st.columns(min(len(ext_show), 3))
    for col_w, col_name in zip(ecols, ext_show):
        sub = lat[["Bank", col_name]].dropna()
        if sub.empty: continue
        thr_v, good_a, thr_c, lbl = THR_MAP.get(col_name, (None, True, "#a78bfa",""))
        sub = sub.sort_values(col_name, ascending=not good_a)
        clrs = [bcolor(b, i) for i, b in enumerate(sub["Bank"])]
        fig_e = go.Figure(go.Bar(
            x=sub["Bank"], y=sub[col_name],
            marker=dict(color=clrs, line=dict(color="rgba(0,0,0,0)")),
            text=[f"{v:.1f}" for v in sub[col_name]], textposition="outside",
            textfont=dict(size=10, color="#6e82a0"),
            hovertemplate=f"<b>%{{x}}</b><br>{col_name}: %{{y:.2f}}<extra></extra>",
        ))
        if thr_v is not None:
            fig_e.add_hline(y=thr_v, line_dash="dot", line_color=thr_c, line_width=1.4,
                            annotation=dict(text=f" {lbl}", font=dict(color=thr_c, size=10), x=0))
        apply_layout(fig_e, {"title": f"{col_name} · {latest_fy}", "height": 265,
                              "showlegend": False, "xaxis": AX_X, "yaxis": AX_Y})
        col_w.markdown('<div class="ch-wrap">', unsafe_allow_html=True)
        col_w.plotly_chart(fig_e, width='stretch', config={"displayModeBar": False})
        col_w.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 08 — SCORECARD TABLE
# ═══════════════════════════════════════════
st.markdown('<div class="sec-div">08 — Bank Scorecard · Latest Financial Year</div>', unsafe_allow_html=True)
opt_cols = [c for c in ["CASA Ratio (%)","PCR (%)"] if c in srt.columns]
tbl = """<div style="overflow-x:auto;background:rgba(255,255,255,.013);
  border:1px solid rgba(255,255,255,.05);border-radius:10px;padding:3px;">
<table class="sc-tbl"><thead><tr>
  <th>Rank</th><th>Bank</th><th>Net NPA (%)</th><th>ROA (%)</th><th>CAR (%)</th>"""
for oc in opt_cols: tbl += f"<th>{oc}</th>"
tbl += "<th>Score</th><th>Tier</th></tr></thead><tbody>"
for i, row in srt.iterrows():
    bc  = bcolor(row["Bank"], i)
    pct = row["Score"]/ms*100
    bar_c = "#34d399" if pct>=80 else "#a78bfa" if pct>=55 else "#f87171"
    tbl += f"""<tr>
      <td><span class="rnk">{i+1}</span></td>
      <td><span style="display:inline-block;width:7px;height:7px;border-radius:50%;
        background:{bc};margin-right:7px;vertical-align:middle;"></span>
        <b style="color:#ecf0ff">{row['Bank']}</b></td>
      <td>{colored_val(row['Net NPA (%)'], npa, False)}</td>
      <td>{colored_val(row['ROA (%)'],     roa, True)}</td>
      <td>{colored_val(row['CAR (%)'],     car, True)}</td>"""
    for oc in opt_cols:
        v = row.get(oc, float("nan"))
        tbl += f"<td><span class='mono'>{v:.1f}%</span></td>" if pd.notna(v) else "<td>—</td>"
    tbl += f"""<td>
      <span class="mono">{row['Score']}/{ms}</span>
      <div class="sbar-bg"><div class="sbar-fill" style="width:{pct:.0f}%;background:{bar_c}"></div></div>
      </td><td>{tier_pill(row['Tier'])}</td></tr>"""
tbl += "</tbody></table></div>"
st.markdown(tbl, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 09 — ANALYST BRIEFING + WRITTEN ANALYSIS
# ═══════════════════════════════════════════
st.markdown('<div class="sec-div">09 — Analyst Briefing &amp; Written Analysis</div>', unsafe_allow_html=True)
cards, written = build_analysis(df, lat, srt, params, appetite, ms, latest_fy)

card_html = "".join(f"""<div class="ic">
  <div class="il">{c['n']}</div>
  <div class="it">{c['t']}</div>
  <div class="ib">{c['b']}</div>
</div>""" for c in cards)
st.markdown(f'<div class="ig">{card_html}</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f'<div class="written-analysis">{written}</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 10 — EXPORT
# ═══════════════════════════════════════════
st.markdown('<div class="sec-div">10 — Full Dataset &amp; Export</div>', unsafe_allow_html=True)
with st.expander("View &amp; Download Full Dataset"):
    show  = ["Bank","Year","Net NPA (%)","ROA (%)","CAR (%)"] + \
            [c for c in ["CASA Ratio (%)","PCR (%)","Credit-Deposit Ratio (%)","Debt-Equity Ratio"] if c in df.columns] + \
            ["Score","Tier"]
    disp  = df[[c for c in show if c in df.columns]].sort_values(["Year","Score"],ascending=[False,False]).reset_index(drop=True)
    fmt   = {c:"{:.2f}%" for c in ["Net NPA (%)","ROA (%)","CAR (%)","CASA Ratio (%)","PCR (%)","Credit-Deposit Ratio (%)"] if c in disp.columns}
    if "Debt-Equity Ratio" in disp.columns: fmt["Debt-Equity Ratio"] = "{:.2f}"

    def _sty(col):
        if col.name=="Net NPA (%)": return ["color:#6ee7b7" if v<=npa else "color:#fca5a5" for v in col]
        if col.name=="ROA (%)":     return ["color:#6ee7b7" if v>=roa else "color:#fde68a" for v in col]
        if col.name=="CAR (%)":     return ["color:#6ee7b7" if v>=car else "color:#fca5a5" for v in col]
        if col.name=="Score":       return ["color:#6ee7b7" if v/ms>=.80 else "color:#c4b5fd" if v/ms>=.55 else "color:#fca5a5" for v in col]
        return [""]*len(col)

    st.dataframe(disp.style.apply(_sty, axis=0).format(fmt), width='stretch', height=380)
    cl, cr = st.columns(2)
    cl.download_button("⬇ Full Dataset (CSV)", disp.to_csv(index=False).encode(),
                       f"credit_risk_{latest_fy}.csv", "text/csv", width='stretch')
    cr.download_button("⬇ Scorecard (CSV)",
                       srt[["Bank","Net NPA (%)","ROA (%)","CAR (%)","Score","Tier"]].to_csv(index=False).encode(),
                       f"scorecard_{latest_fy}.csv", "text/csv", width='stretch')

# Footer
st.markdown("""
<div style="text-align:center;padding:14px 0 5px;border-top:1px solid rgba(255,255,255,.04);margin-top:12px;">
  <span style="font-family:'JetBrains Mono',monospace;font-size:8.5px;color:#1e2d42;letter-spacing:2px;">
    STRATEGIC CREDIT RISK INTELLIGENCE TERMINAL · INDIAN COMMERCIAL BANKS<br>
    DEVELOPED BY: APSARA MITRA 
  </span>
</div>""", unsafe_allow_html=True)