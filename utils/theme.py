"""OLA-branded visual theme and page header."""
from pathlib import Path
import base64
import html
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "images/Ola-Cabs-Logo.png"

def apply_theme() -> None:
    st.markdown("""
    <style>
      :root { --ola-ink:#151515; --ola-lime:#D7DF23; --ola-green:#86A800; --ola-mist:#F5F7E9; }
      .stApp { background-color:#FBFCF1; background-image:repeating-linear-gradient(135deg,rgba(125,148,0,.035) 0px,rgba(125,148,0,.035) 1px,transparent 1px,transparent 12px),linear-gradient(180deg,#FBFCEB 0%,#FFFFFF 420px); background-attachment:fixed; color:var(--ola-ink); }
      [data-testid="stHeader"] { background:rgba(255,255,255,0); }
      [data-testid="stSidebar"] { background:linear-gradient(180deg,#191A16 0%,#25271F 100%); border-right:1px solid #36392D; }
      [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { color:#F5F6EE; }
      [data-testid="stSidebar"] p,[data-testid="stSidebar"] label { color:#E5E8D8; }
      [data-testid="stSidebar"] > div:first-child { padding-top:0; }
      [data-testid="stSidebar"] [data-testid="stSidebarContent"],
      [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding-top:0!important; }
      [data-testid="stSidebar"] [data-testid="stSidebarHeader"] { height:0; min-height:0; padding:0; }
      .ola-sidebar-logo { display:inline-block; width:150px; padding:9px 12px; margin:0 0 .25rem; border-radius:12px; background:#F7F8EE; box-sizing:border-box; }
      .ola-sidebar-logo img { display:block; width:100%; height:auto; object-fit:contain; }
      .ola-side-brand { color:#F5F6EE; font-weight:850; letter-spacing:.12em; line-height:1.15; font-size:.88rem; margin:.15rem 0 .8rem; }
      .ola-side-brand span { color:#C1C7AD; font-weight:500; letter-spacing:.02em; font-size:.75rem; }
      .ola-nav-section { color:#BBC48C; font-size:.66rem; font-weight:850; letter-spacing:.14em; margin:.6rem 0 .2rem; }
      .ola-sidebar-divider { height:1px; width:100%; background:linear-gradient(90deg,rgba(215,223,35,.85),rgba(215,223,35,.12)); margin:.8rem 0 1rem; }
      [data-testid="stSidebar"] [data-testid="stButton"] { margin-bottom:-.42rem; }
      [data-testid="stSidebar"] [data-testid="stButton"] button { min-height:2.35rem; text-align:left; padding:.4rem .75rem; font-weight:650; border-radius:10px; }
      [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] { background:rgba(255,255,255,.055); border-color:#484B40; color:#F1F3E9; }
      [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover { background:#34372C; border-color:#AAB675; color:#fff; }
      [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] { background:#D7DF23; border-color:#BBC51A; color:#171717; box-shadow:0 2px 8px rgba(70,80,0,.12); }
      [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"],
      [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] p,
      [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] span { color:#171717!important; }
      .ola-context-title { color:#BBC48C; font-size:.65rem; font-weight:850; letter-spacing:.13em; margin-top:.45rem; }
      [data-testid="stSidebar"] [data-testid="stMetric"] { background:#2B2E24; border:1px solid #45483B; border-top:3px solid #D7DF23; padding:8px 11px; border-radius:10px; margin:.3rem 0; }
      [data-testid="stSidebar"] [data-testid="stMetricLabel"] { color:#C4C9B6; }
      [data-testid="stSidebar"] [data-testid="stMetricValue"] { color:#F7F8F2; }
      [data-testid="stSidebar"] [data-testid="stMetricValue"] { font-size:1.22rem; }
      [data-testid="stSidebar"] [data-testid="stMetricLabel"] { font-size:.72rem; }
      h1,h2,h3 { color:#171717; letter-spacing:-.025em; }
      [data-testid="stMetric"] { background:#fff; border:1px solid #E8EACF; border-top:4px solid #D7DF23; padding:15px 17px; border-radius:14px; box-shadow:0 3px 14px rgba(27,35,0,.045); }
      [data-testid="stMetricLabel"] { color:#62664C; }
      [data-testid="stMetricValue"] { color:#151515; }
      [data-testid="stVerticalBlockBorderWrapper"] { border-color:#E8EACF; border-radius:16px; background:rgba(255,255,255,.90); box-shadow:0 4px 18px rgba(27,35,0,.035); }
      .ola-header-shell { position:relative; overflow:hidden; display:flex; align-items:center; gap:1.35rem; min-height:154px; padding:1.5rem 2rem; margin:.55rem 0 1.25rem; border:1px solid rgba(142,157,0,.3); border-radius:22px; background:linear-gradient(112deg,rgba(231,237,127,.82),rgba(255,255,255,.80) 54%,rgba(246,248,219,.84)); box-shadow:0 14px 40px rgba(74,83,0,.10),inset 0 1px rgba(255,255,255,.9); backdrop-filter:blur(16px); }
      .ola-header-shell:before { content:''; position:absolute; width:320px; height:320px; right:-70px; top:-185px; border-radius:50%; background:radial-gradient(circle,rgba(215,223,35,.40),rgba(215,223,35,0) 70%); pointer-events:none; }
      .ola-header-shell:after { content:''; position:absolute; left:0; top:20px; bottom:20px; width:5px; border-radius:0 6px 6px 0; background:linear-gradient(180deg,#d7df23,#839900); }
      .ola-header-logo { width:126px; max-height:88px; object-fit:contain; position:relative; z-index:1; }
      .ola-header-copy { position:relative; z-index:1; }
      .ola-page-title { margin:.23rem 0 .2rem; font-size:2.45rem; line-height:1.08; font-weight:820; letter-spacing:-.045em; color:#171717; }
      .ola-page-subtitle { margin:.38rem 0 0; color:#60634e; font-size:1rem; }
      .ola-chart-title { font-size:1.03rem; font-weight:730; color:#25271D; padding:.1rem 0 .65rem; }
      .ola-key-insight { margin:.45rem 0 .1rem; padding:.65rem .8rem; border-left:3px solid #849900; border-radius:0 9px 9px 0; background:linear-gradient(90deg,rgba(215,223,35,.13),rgba(245,247,233,.62)); color:#454936; font-size:.84rem; line-height:1.5; }
      .ola-key-insight span { display:block; margin-bottom:.2rem; color:#718600; font-size:.62rem; font-weight:850; letter-spacing:.12em; }
      [data-testid="stVerticalBlockBorderWrapper"]:has(.ola-chart-title) { background:linear-gradient(150deg,rgba(255,255,255,.98),rgba(248,250,230,.82)); border-color:#E2E6C4; box-shadow:0 9px 28px rgba(43,52,0,.07); }
      [data-testid="stPlotlyChart"] { border-radius:12px; overflow:hidden; }
      .ola-kicker { color:#788D00; text-transform:uppercase; letter-spacing:.14em; font-size:.72rem; font-weight:800; }
      div.stButton > button, div.stDownloadButton > button { border-radius:10px; border:1px solid #D7DF23; background:#D7DF23; color:#161616; font-weight:700; }
      div.stButton > button:hover, div.stDownloadButton > button:hover { border-color:#B6C21B; background:#C7D01D; color:#111; }
      div[data-baseweb="select"] > div { border-radius:10px; }
      .stAlert { border-radius:12px; }
      footer { visibility:hidden; }
    </style>
    """, unsafe_allow_html=True)

def render_brand_header(page_title: str) -> None:
    logo=""
    if LOGO.exists():
        encoded=base64.b64encode(LOGO.read_bytes()).decode("ascii")
        logo=f"<img class='ola-header-logo' src='data:image/png;base64,{encoded}' alt='OLA logo'>"
    st.markdown(
        f"<section class='ola-header-shell'>{logo}<div class='ola-header-copy'>"
        f"<div class='ola-kicker'>OLA RIDE INSIGHTS · MOBILITY INTELLIGENCE</div>"
        f"<div class='ola-page-title'>{html.escape(page_title)}</div>"
        "<div class='ola-page-subtitle'>Bookings · supply · customer experience</div>"
        "</div></section>", unsafe_allow_html=True
    )
