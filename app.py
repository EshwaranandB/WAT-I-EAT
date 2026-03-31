import streamlit as st
from google import genai
from google.genai import types
import os
import json
import time
from dotenv import load_dotenv
from PIL import Image
import io
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="WAT-I-EAT - India's AI Food Companion",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- HIDE STREAMLIT CHROME & SET BASE TABS ---
st.markdown("""
    <style>
    #MainMenu, footer, .stDeployButton { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- LOAD ENV & CONFIG GEMINI ---
load_dotenv()
# Check local .env first, then Streamlit Secrets for cloud deployment
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.error("Google API Key not found. Please set GOOGLE_API_KEY in your .env file or Streamlit Secrets.")
    client = None

# --- NUCLEAR CSS OVERHAUL ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Sora:wght@300;400;600;700;800&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #080810 !important;
    color: #E8E8F0 !important;
}

/* ── STREAMLIT CHROME OVERRIDES ── */
#MainMenu, footer, .stDeployButton { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding: 0 2rem 4rem !important; max-width: 1200px !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080810; }
::-webkit-scrollbar-thumb { background: #7C3AED; border-radius: 2px; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0D0D18 !important;
    border-right: 1px solid rgba(124,58,237,0.15) !important;
}
[data-testid="stSidebar"] * { color: #C0C0D0 !important; }
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stTextInput > div > div > input,
[data-testid="stSidebar"] .stNumberInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: white !important;
}
[data-testid="stSidebar"] .stSlider > div > div > div {
    background: linear-gradient(90deg, #7C3AED, #DB2777) !important;
}

/* ── HERO ── */
.hero-wrapper {
    min-height: 92vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 6rem 0 4rem;
    position: relative;
    overflow: hidden;
}
.hero-wrapper::before {
    content: '';
    position: absolute;
    top: -200px; left: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(124,58,237,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-wrapper::after {
    content: '';
    position: absolute;
    bottom: -100px; right: -100px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(219,39,119,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(124,58,237,0.1);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 100px;
    padding: 6px 16px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #A78BFA;
    margin-bottom: 24px;
    width: fit-content;
}
.hero-dot {
    width: 6px; height: 6px;
    background: #A78BFA;
    border-radius: 50%;
    animation: p_pulse 2s infinite;
}
@keyframes p_pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}
/* Pulsing Demo Active dot class */
.pulse-green {
    display: inline-block;
    width: 8px; height: 8px;
    background: #10B981;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse-green-anim 1.5s infinite;
}
@keyframes pulse-green-anim {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.hero-title {
    font-family: 'Sora', sans-serif !important;
    font-size: clamp(3.2rem, 8vw, 6.5rem) !important;
    font-weight: 800 !important;
    line-height: 1.05 !important;
    letter-spacing: -0.03em !important;
    margin-bottom: 8px !important;
    background: linear-gradient(135deg, #FFFFFF 0%, #E0D7FF 40%, #F9A8D4 70%, #FCD34D 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
.hero-subtitle {
    font-size: clamp(1rem, 2.5vw, 1.4rem);
    color: #6B6B8A;
    font-weight: 400;
    margin-bottom: 40px;
    max-width: 600px;
    line-height: 1.6;
}
.hero-subtitle em {
    color: #A78BFA;
    font-style: normal;
    font-weight: 500;
}
.stat-strip {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 48px;
}
.stat-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 100px;
    font-size: 0.82rem;
    color: #9090B0;
    transition: all 0.3s ease;
}
.stat-chip:hover {
    border-color: rgba(124,58,237,0.3);
    color: #C0C0E0;
}
.stat-chip span { color: #A78BFA; font-weight: 600; }
.hero-scroll-hint {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.8rem;
    color: #3A3A5C;
    margin-top: 16px;
}
.scroll-line {
    width: 40px; height: 1px;
    background: linear-gradient(90deg, #7C3AED, transparent);
}

/* ── SECTION HEADERS ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7C3AED;
    margin-bottom: 8px;
}
.section-title {
    font-family: 'Sora', sans-serif;
    font-size: clamp(1.6rem, 3vw, 2.4rem);
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.section-desc {
    font-size: 1rem;
    color: #5A5A7A;
    max-width: 560px;
    line-height: 1.7;
    margin-bottom: 36px;
}
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, rgba(124,58,237,0.4), transparent);
    margin: 60px 0;
}

/* ── CARDS ── */
.card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 28px;
    transition: all 0.35s ease;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(124,58,237,0.06), rgba(219,39,119,0.03));
    opacity: 0;
    transition: opacity 0.35s ease;
    pointer-events: none;
}
.card:hover::before { opacity: 1; }
.card:hover {
    border-color: rgba(124,58,237,0.25);
    transform: translateY(-3px);
}
.card-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #7C3AED;
    margin-bottom: 12px;
}
.card-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 8px;
}
.card-body {
    font-size: 0.9rem;
    color: #8080A0;
    line-height: 1.7;
}

/* ── UPLOAD ZONE ── */
.upload-zone {
    border: 2px dashed rgba(124,58,237,0.3);
    border-radius: 24px;
    padding: 60px 40px;
    text-align: center;
    background: rgba(124,58,237,0.03);
    transition: all 0.3s ease;
    cursor: pointer;
}
.upload-zone:hover {
    border-color: rgba(124,58,237,0.6);
    background: rgba(124,58,237,0.06);
}
.upload-icon { font-size: 3rem; margin-bottom: 16px; }
.upload-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: white;
    margin-bottom: 8px;
}
.upload-desc { font-size: 0.9rem; color: #5A5A7A; }

/* ── SCORE RING ── */
.score-ring-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 24px;
}
.score-ring {
    width: 160px; height: 160px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    background: conic-gradient(
        var(--ring-color, #7C3AED) var(--ring-deg, 270deg),
        rgba(255,255,255,0.05) 0deg
    );
}
.score-ring::before {
    content: '';
    position: absolute;
    inset: 12px;
    border-radius: 50%;
    background: #0D0D18;
}
.score-ring-value {
    position: relative;
    z-index: 1;
    font-family: 'Sora', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: white;
}
.score-ring-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #8080A0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── MACRO BARS ── */
.macro-row {
    margin-bottom: 18px;
}
.macro-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.macro-name {
    font-size: 0.85rem;
    font-weight: 500;
    color: #C0C0D8;
}
.macro-amount {
    font-size: 0.8rem;
    color: #8080A0;
}
.macro-track {
    height: 6px;
    background: rgba(255,255,255,0.05);
    border-radius: 100px;
    overflow: hidden;
}
.macro-fill-green { 
    height: 100%; border-radius: 100px;
    background: linear-gradient(90deg, #059669, #34D399);
}
.macro-fill-amber {
    height: 100%; border-radius: 100px;
    background: linear-gradient(90deg, #D97706, #FBBF24);
}
.macro-fill-red {
    height: 100%; border-radius: 100px;
    background: linear-gradient(90deg, #DC2626, #F87171);
}

/* ── VERDICT TAGS ── */
.verdict-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 12px;
}
.verdict-good { background: rgba(5,150,105,0.15); color: #34D399; border: 1px solid rgba(5,150,105,0.25); }
.verdict-warn { background: rgba(217,119,6,0.15); color: #FBBF24; border: 1px solid rgba(217,119,6,0.25); }
.verdict-swap { background: rgba(124,58,237,0.15); color: #A78BFA; border: 1px solid rgba(124,58,237,0.25); }

/* ── DISH RANK CARDS ── */
.dish-card {
    padding: 18px 20px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
    margin-bottom: 10px;
    transition: all 0.2s ease;
}
.dish-card:hover { border-color: rgba(124,58,237,0.2); }
.dish-card.best { border-color: rgba(5,150,105,0.35); background: rgba(5,150,105,0.04); }
.dish-card.worst { border-color: rgba(220,38,38,0.25); background: rgba(220,38,38,0.03); }
.dish-name { font-weight: 600; font-size: 0.95rem; color: white; }
.dish-reason { font-size: 0.82rem; color: #9090B0; margin-top: 4px; line-height: 1.5; }

/* ── MOOD CARDS ── */
.mood-suggestion {
    padding: 20px;
    border-radius: 16px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 12px;
}
.mood-food-name { font-family: 'Sora', sans-serif; font-size: 1rem; font-weight: 600; color: white; margin-bottom: 4px; }
.mood-food-why { font-size: 0.85rem; color: #8080A0; line-height: 1.6; }

/* ── THALI CARDS ── */
.meal-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 14px;
    transition: all 0.3s ease;
}
.meal-card:hover { border-color: rgba(219,39,119,0.25); }
.meal-type {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #DB2777;
    margin-bottom: 6px;
}
.meal-name { font-family: 'Sora', sans-serif; font-size: 1.05rem; font-weight: 600; color: white; margin-bottom: 10px; }
.meal-meta { display: flex; gap: 16px; }
.meal-meta-item { font-size: 0.8rem; color: #8080A0; }
.meal-meta-item strong { color: #A0A0C0; }
.meal-why { font-size: 0.82rem; color: #505070; margin-top: 10px; line-height: 1.5; }

/* ── PERSONALITY BADGE ── */
.personality-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 12px 20px;
    background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(219,39,119,0.1));
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 16px;
    margin-bottom: 16px;
}
.personality-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #7C3AED; font-weight: 700; }
.personality-value { font-family: 'Sora', sans-serif; font-size: 1rem; font-weight: 600; color: white; }

/* ── HABIT CARD ── */
.habit-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.08), rgba(219,39,119,0.05));
    border: 1px solid rgba(124,58,237,0.15);
    border-radius: 20px;
    padding: 24px;
    margin-top: 16px;
}
.habit-header { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #7C3AED; font-weight: 700; margin-bottom: 10px; }
.habit-text { font-size: 1rem; color: #D0D0E8; line-height: 1.6; font-weight: 500; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #7C3AED, #DB2777) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.4) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 10px !important;
    color: #8080A0 !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7C3AED, #DB2777) !important;
    color: white !important;
}

/* ── SIDEBAR PROFILE HEADER ── */
.profile-header {
    background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(219,39,119,0.1));
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 20px;
    text-align: center;
}
.profile-avatar {
    width: 52px; height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7C3AED, #DB2777);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    margin: 0 auto 10px;
}
.profile-name {
    font-family: 'Sora', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: white;
}
.profile-goal {
    font-size: 0.75rem;
    color: #7C3AED;
    font-weight: 600;
}

/* ── POWERED BY BADGE ── */
.powered-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 100px;
    font-size: 0.75rem;
    color: #707090;
    margin: 4px;
}

/* ── FOOTER ── */
.footer {
    margin-top: 80px;
    padding: 48px 0 32px;
    border-top: 1px solid rgba(255,255,255,0.05);
    text-align: center;
}
.footer-logo {
    font-family: 'Sora', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7C3AED, #DB2777);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 12px;
}
.footer-tagline { font-size: 0.9rem; color: #3A3A5C; margin-bottom: 24px; }
.footer-copy { font-size: 0.75rem; color: #2A2A40; margin-top: 24px; }
/* ── PROGRESS RINGS (DAILY) ── */
.daily-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin: 40px 0;
}
.pulsing-status {
    font-size: 0.75rem;
    font-weight: 600;
    color: #10B981;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 12px;
}
/* ── KITCHEN INTELLIGENCE ── */
.kitchen-hack {
    background: rgba(124,58,237,0.05);
    border: 1px solid rgba(124,58,237,0.15);
    border-radius: 16px;
    padding: 20px;
    margin-top: 20px;
}
.kitchen-hack-title {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #A78BFA;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': '', 'age': 25, 'gender': 'Female',
        'goal': 'Eat cleaner', 'budget': 200, 'region': 'Maharashtra',
        'diet': 'No preference', 'mood': '😐 Neutral', 'medical': 'None',
        'eating_pattern': '3 meals'
    }
if 'demo_mode_active' not in st.session_state:
    st.session_state.demo_mode_active = False

if 'history' not in st.session_state:
    st.session_state.history = []

if 'daily_totals' not in st.session_state:
    st.session_state.daily_totals = {'calories': 0, 'protein': 0, 'fiber': 0}

# --- HELPER: LOTTIE & JSON ---
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_scanning = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_96bovdur.json") # Food scan animation
lottie_success = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_n9u8vyqc.json") # Success check

def extract_json(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())

# --- SIDEBAR: HYPER PERSONALIZATION ---
with st.sidebar:
    # ── DEMO MODE BUTTON OVERHAUL ──
    demo_status = "● Demo Active" if st.session_state.demo_mode_active else "🎯 Demo Mode"
    demo_class = "pulse-green" if st.session_state.demo_mode_active else ""
    
    if st.button(demo_status):
        st.session_state.user_profile = {
            'name': 'Eshwar', 'age': 20, 'gender': 'Male',
            'goal': 'Student budget eating', 'budget': 150, 'region': 'Gujarat',
            'diet': 'Non-veg', 'mood': '🤩 Motivated', 'medical': 'None',
            'eating_pattern': 'Irregular'
        }
        st.session_state.demo_mode_active = True
        st.rerun()
    
    if st.session_state.demo_mode_active:
        st.markdown(f'<div style="text-align:center; color:#10B981; font-size:0.8rem; margin-bottom:10px;"><span class="pulse-green"></span>Demo Mode Activated</div>', unsafe_allow_html=True)

    # ── PROFILE HEADER ──
    p_name = st.session_state.user_profile.get('name', 'Your Profile')
    p_goal = st.session_state.user_profile.get('goal', 'Select a goal')
    st.markdown(f"""
        <div class="profile-header">
            <div class="profile-avatar">🍱</div>
            <div class="profile-name">{p_name if p_name else 'Your Profile'}</div>
            <div class="profile-goal">{p_goal}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color:#7C3AED;'>Customize Journey</h4>", unsafe_allow_html=True)
    
    st.session_state.user_profile['name'] = st.text_input("Full Name", value=st.session_state.user_profile.get('name', ''))
    
    col_age, col_gen = st.columns(2)
    with col_age:
        st.session_state.user_profile['age'] = st.number_input("Age", min_value=12, max_value=100, value=st.session_state.user_profile.get('age', 25))
    with col_gen:
        st.session_state.user_profile['gender'] = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.user_profile.get('gender', 'Female')))
    
    goals = ['Lose weight', 'Build muscle', 'Manage diabetes', 'Eat cleaner', 'Boost energy', 'Manage PCOS', 'Student budget eating', 'Family nutrition']
    st.session_state.user_profile['goal'] = st.selectbox("Current Goal", goals, index=goals.index(st.session_state.user_profile.get('goal', 'Eat cleaner')))
    
    st.session_state.user_profile['budget'] = st.slider("Daily Budget (₹)", min_value=50, max_value=1500, step=10, value=st.session_state.user_profile.get('budget', 200))
    
    regions = ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Punjab', 'Bengal', 'UP', 'Karnataka', 'Rajasthan', 'Other']
    if st.session_state.user_profile.get('region') not in regions:
        regions.append(st.session_state.user_profile.get('region'))
    st.session_state.user_profile['region'] = st.selectbox("Native Region", regions, index=regions.index(st.session_state.user_profile.get('region', 'Maharashtra')))
    
    diets = ['Vegetarian', 'Non-veg', 'Vegan', 'Jain', 'Keto', 'No preference']
    st.session_state.user_profile['diet'] = st.selectbox("Dietary Filter", diets, index=diets.index(st.session_state.user_profile.get('diet', 'No preference')))
    
    moods = ['😊 Happy', '😤 Stressed', '😴 Tired', '😰 Anxious', '🤩 Motivated', '😐 Neutral']
    curr_mood = st.session_state.user_profile.get('mood', '😐 Neutral')
    # Match emoji or text
    mood_idx = 5
    for i, m in enumerate(moods):
        if curr_mood in m or m in curr_mood:
            mood_idx = i
            break
    st.session_state.user_profile['mood'] = st.selectbox("Current State", moods, index=mood_idx)
    
    medicals = ['Diabetes', 'BP', 'PCOS', 'Thyroid', 'None', 'Prefer not to say']
    st.session_state.user_profile['medical'] = st.selectbox("Conditions", medicals, index=medicals.index(st.session_state.user_profile.get('medical', 'None')))
    
    patterns = ['3 meals', '2 meals + snacks', 'Intermittent fasting', 'Irregular']
    st.session_state.user_profile['eating_pattern'] = st.selectbox("Frequency", patterns, index=patterns.index(st.session_state.user_profile.get('eating_pattern', '3 meals')))


# --- ACT 1: HERO SECTION ---
st.markdown("""
<div class="hero-wrapper">
    <div class="hero-eyebrow">
        <div class="hero-dot"></div>
        AMD Slingshot Regional Ideathon 2025
    </div>
    <h1 class="hero-title">WAT-I-EAT</h1>
    <p class="hero-subtitle">
        India's first AI that understands what you 
        <em>actually</em> eat — not what you should.
    </p>
    <div class="stat-strip">
        <div class="stat-chip"><span>56%</span> of India's disease burden from diet</div>
        <div class="stat-chip"><span>44%</span> of Gen Z want to eat healthy but can't</div>
        <div class="stat-chip"><span>1.4B</span> people. Zero personalized nutrition.</div>
    </div>
    <div class="hero-scroll-hint">
        <div class="scroll-line"></div>
        Scroll to analyze your meal
    </div>
</div>
""", unsafe_allow_html=True)

# --- ACT 1.5: THE HEALTH PULSE (DAILY TRACKING) ---
if st.session_state.history:
    st.markdown('<p class="section-label" style="text-align:center;">Act 1.5</p>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title" style="text-align:center;">The Health Pulse</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc" style="text-align:center; margin: 0 auto 40px;">Real-time tracking of your cumulative nutritional footprint today.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="daily-grid">', unsafe_allow_html=True)
    p_col1, p_col2, p_col3 = st.columns(3)
    
    with p_col1:
        # Calorie Ring
        cal_pct = min(st.session_state.daily_totals['calories'] / 2000 * 100, 100)
        st.markdown(f"""
        <div class="score-ring-wrapper card">
            <div class="score-ring" style="--ring-color:#7C3AED; --ring-deg:{int(cal_pct*3.6)}deg;">
                <div class="score-ring-value">{int(st.session_state.daily_totals['calories'])}</div>
            </div>
            <div class="score-ring-label">Calories Eaten</div>
            <div style="font-size:0.75rem; color:#505070; margin-top:10px;">Goal: 2000 kcal</div>
        </div>
        """, unsafe_allow_html=True)

    with p_col2:
        # Protein Ring
        prot_pct = min(st.session_state.daily_totals['protein'] / 100 * 100, 100)
        st.markdown(f"""
        <div class="score-ring-wrapper card">
            <div class="score-ring" style="--ring-color:#DB2777; --ring-deg:{int(prot_pct*3.6)}deg;">
                <div class="score-ring-value">{int(st.session_state.daily_totals['protein'])}g</div>
            </div>
            <div class="score-ring-label">Protein Target</div>
            <div style="font-size:0.75rem; color:#505070; margin-top:10px;">Goal: 100g</div>
        </div>
        """, unsafe_allow_html=True)

    with p_col3:
        # Fiber Ring
        fib_pct = min(st.session_state.daily_totals['fiber'] / 30 * 100, 100)
        st.markdown(f"""
        <div class="score-ring-wrapper card">
            <div class="score-ring" style="--ring-color:#10B981; --ring-deg:{int(fib_pct*3.6)}deg;">
                <div class="score-ring-value">{int(st.session_state.daily_totals['fiber'])}g</div>
            </div>
            <div class="score-ring-label">Fiber Count</div>
            <div style="font-size:0.75rem; color:#505070; margin-top:10px;">Goal: 30g</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-divider" style="margin: 40px 0;"></div>', unsafe_allow_html=True)

# --- PROMPT BUILDER ---
def get_system_prompt():
    p = st.session_state.user_profile
    return f"""
    You are WAT-I-EAT, India's most advanced AI nutritionist. 
    You have deep knowledge of Indian cuisine across all regions — from Gujarati dal dhokli to Tamil sambar, Punjabi butter chicken to Bengali hilsa, street food like vada pav, pani puri, chole bhature, and home cooking. You understand the reality of Indian eating (hostel budgets, festivals, shared family meals, street food).

    USER CONTEXT:
    Name: {p['name'] if p['name'] else 'Friend'}
    Age: {p['age']} | Gender: {p['gender']}
    Goal: {p['goal']}
    Budget: ₹{p['budget']}/day
    Region: {p['region']}
    Diet: {p['diet']}
    Mood: {p['mood']}
    Medical: {p['medical']}
    Eating Pattern: {p['eating_pattern']}

    RULES:
    1. ALWAYS address the user by their name ("{p['name'] if p['name'] else 'Friend'}").
    2. ALWAYS factor in their budget, goal, region, mood, and medical condition.
    3. NEVER recommend they stop eating their cultural foods — find healthier versions or right portions.
    4. Speak warmly, like a knowledgeable friend.
    5. Give ONE specific, actionable recommendation.
    6. Always mention approximate ₹ cost for budget-conscious users.
    7. Return your ENTIRE response in valid, strict JSON matching exactly the requested structure, with no markdown code blocks formatting it (just raw JSON).
    """

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# --- ACT 3: SNAP & KNOW ---
st.markdown("""
<p class="section-label">Step 01</p>
<h2 class="section-title">Snap & Know</h2>
<p class="section-desc">
    Point your camera at any meal — street food, 
    canteen, home cooking. Get a full nutritional 
    intelligence report in seconds.
</p>
""", unsafe_allow_html=True)

up_col1, up_col2 = st.columns(2)
with up_col1:
    uploaded_file = st.file_uploader("Upload meal image", type=["jpg", "jpeg", "png"])
with up_col2:
    camera_file = st.camera_input("Capture live photo")

img_to_process = uploaded_file or camera_file

# Demo image injection
if st.session_state.demo_mode_active and not img_to_process:
    demo_path = "demo_idli_sambar.jpg"
    if os.path.exists(demo_path):
        img_to_process = open(demo_path, "rb")

if img_to_process:
    try:
        pil_image = Image.open(img_to_process)
        # Performance: standard resize
        pil_image.thumbnail((1024, 1024))
        st.image(pil_image, use_container_width=True)
    except Exception as e:
        st.error(f"Image Error: {e}")
        pil_image = None

    analyze_clicked = st.button("✨ ANALYZE MEAL", type="primary")
    
    # Auto-trigger if demo mode was just activated
    if st.session_state.demo_mode_active and pil_image and not uploaded_file and not camera_file:
        analyze_clicked = True
        st.session_state.demo_mode_active = False # Reset flag so it doesn't loop

    if analyze_clicked and pil_image:
        with st.spinner("WAT-I-EAT AI is scanning dish metadata..."):
            try:
                if not client:
                    st.error("API Key missing.")
                    st.stop()
                
                analysis_prompt = get_system_prompt() + """
                TASK: Analyze the food in the primary image. Return a JSON object EXACTLY matching this structure:
                {
                    "food_identified": [{"name": "Food Name", "confidence": "95%"}],
                    "total_calories": 500,
                    "nourish_score": 75,
                    "macros": {
                        "protein": {"amount": "15g", "status": "good", "percent": 20},
                        "carbs": {"amount": "60g", "status": "excess", "percent": 60},
                        "fats": {"amount": "20g", "status": "okay", "percent": 20},
                        "fiber": {"amount": "12g", "status": "good", "percent": 80},
                        "sugar": {"amount": "5g", "status": "good", "percent": 15}
                    },
                    "verdict": {
                        "great": "Specific praise based on condition and goal",
                        "watch_out": "Specific warning",
                        "swap_suggestion": "ONE actionable swap"
                    },
                    "radar_data": {
                        "protein": 7, "carbs": 4, "fats": 6, "vitamins": 8, "minerals": 5, "hydration": 3
                    },
                    "personality": "Impactful Eater",
                    "habit": "Start your day with half a liter of water before this meal.",
                    "kitchen_intelligence": {
                        "hack_name": "Healthy Alternative Name",
                        "instructions": ["Step 1", "Step 2", "Step 3"]
                    }
                }
                """
                # --- Visual Feedback: Lottie Animation ---
                lottie_placeholder = st.empty()
                with lottie_placeholder:
                    if lottie_scanning:
                        st_lottie(lottie_scanning, height=300, key="scanning")
                    else:
                        st.info("AI Vision System Initialization...")
                
                # Convert PIL to bytes
                buf = io.BytesIO()
                pil_image.save(buf, format="JPEG")
                img_bytes = buf.getvalue()
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                        types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),
                        analysis_prompt
                    ]
                )
                analysis = extract_json(response.text)
                lottie_placeholder.empty()
                
                # Update Session History & Daily Totals
                st.session_state.history.append(analysis)
                st.session_state.daily_totals['calories'] += analysis.get('total_calories', 0)
                
                # Macro parsing (stripping 'g', converting to float)
                def clean_float(val): return float(str(val).replace('g','').replace('mg',''))
                try:
                    m = analysis.get('macros', {})
                    st.session_state.daily_totals['protein'] += clean_float(m.get('protein', {}).get('amount', 0))
                    st.session_state.daily_totals['fiber'] += clean_float(m.get('fiber', {}).get('amount', 0))
                except: pass
                
                # Render results Act 3 logic
                r1c1, r1c2, r1c3 = st.columns([1, 1, 1.3])
                
                with r1c1:
                    st.markdown('<div class="card"><p class="card-label">Detected</p>', unsafe_allow_html=True)
                    for f in analysis.get('food_identified', []):
                        st.markdown(f"<h4 style='margin:0;'>{f.get('name')}</h4><p style='font-size:0.8rem;'>{f.get('confidence')} match</p>", unsafe_allow_html=True)
                    st.markdown(f"<div style='margin-top:15px;'><p class='card-label'>Energy</p><h3>{analysis.get('total_calories')} kCal</h3></div>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with r1c2:
                    ns = analysis.get('nourish_score', 0)
                    color = "#10B981" if ns > 70 else ("#FBBF24" if ns > 40 else "#EF4444")
                    deg = (ns / 100) * 360
                    st.markdown(f"""
                    <div class="card" style="text-align:center;">
                        <p class="card-label">NourishScore™</p>
                        <div class="score-ring-wrapper">
                            <div class="score-ring" style="--ring-deg: {deg}deg; --ring-color: {color};">
                                <span class="score-ring-value">{ns}</span>
                            </div>
                            <span class="score-ring-label">Health Grade</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with r1c3:
                    st.markdown('<div class="card"><p class="card-label">Intelligence Verdict</p>', unsafe_allow_html=True)
                    v = analysis.get('verdict', {})
                    st.markdown(f'<div class="verdict-tag verdict-good">✅ {v.get("great")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="verdict-tag verdict-warn">⚠️ {v.get("watch_out")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="verdict-tag verdict-swap">💡 {v.get("swap_suggestion")}</div>', unsafe_allow_html=True)
                    
                    # --- NEW: KITCHEN INTELLIGENCE (AI RECIPE HACK) ---
                    if analysis.get('nourish_score', 100) < 75:
                        hack = analysis.get('kitchen_intelligence', {})
                        if hack:
                            st.markdown(f"""
                            <div class="kitchen-hack">
                                <div class="kitchen-hack-title">
                                    ✨ Kitchen Intel: Healthy Alternative
                                </div>
                                <div style="font-size:1.1rem; font-weight:600; color:white; margin-bottom:8px;">
                                    {hack.get('hack_name', 'Healthy Version')}
                                </div>
                                <div style="margin-top:8px;">
                                    {" ".join([f'<div style="font-size:0.8rem; color:#8080A0; margin-bottom:4px;">• {step}</div>' for step in hack.get('instructions', [])])}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                r2c1, r2c2 = st.columns([1.5, 1])
                with r2c1:
                    st.markdown('<div class="card"><p class="card-label">Nutritional Context</p>', unsafe_allow_html=True)
                    for m_name, m_data in analysis.get('macros', {}).items():
                        if isinstance(m_data, dict):
                            status_c = "macro-fill-green" if m_data.get('status') == 'good' else ("macro-fill-amber" if m_data.get('status') == 'okay' else "macro-fill-red")
                            pct = m_data.get('percent', 50)
                            st.markdown(f"""
                            <div class="macro-row">
                                <div class="macro-header">
                                    <span class="macro-name">{m_name.capitalize()}</span>
                                    <span class="macro-amount">{m_data.get('amount')}</span>
                                </div>
                                <div class="macro-track"><div class="{status_c}" style="width:{pct}%"></div></div>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with r2c2:
                    st.markdown('<div class="card"><p class="card-label">Balance Profile</p>', unsafe_allow_html=True)
                    rd = analysis.get('radar_data', {})
                    categories = list(rd.keys())
                    values = list(rd.values())
                    categories.append(categories[0])
                    values.append(values[0])
                    
                    fig = go.Figure(data=go.Scatterpolar(
                      r=values, theta=categories, fill='toself',
                      fillcolor='rgba(124, 58, 237, 0.4)', line=dict(color='#7C3AED')
                    ))
                    fig.update_layout(
                      polar=dict(radialaxis=dict(visible=False, range=[0, 10]), bgcolor='rgba(0,0,0,0)'),
                      showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(t=20, b=20, l=20, r=20), height=220
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                # --- INSIGHTS SECTION ---
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown("""
                <p class="section-label">Insights</p>
                <h2 class="section-title">Your Food Story</h2>
                """, unsafe_allow_html=True)
                
                icol1, icol2 = st.columns(2)
                with icol1:
                    st.markdown(f"""
                        <div class="personality-badge">
                            <span class="personality-label">Archetype</span>
                            <span class="personality-value">{analysis.get('personality')}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with icol2:
                    st.markdown(f"""
                        <div class="habit-card">
                            <div class="habit-header">The ONE shift for {st.session_state.user_profile['name']}</div>
                            <div class="habit-text">{analysis.get('habit')}</div>
                        </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Intelligence processing failed: {e}")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# --- ACT 4: POWER FEATURES ---
st.markdown("""
<p class="section-label">Step 02</p>
<h2 class="section-title">Power Features</h2>
<p class="section-desc">
    Three tools that go beyond calorie counting — 
    because your relationship with food is more 
    complex than a number.
</p>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛵 Swiggy Interceptor", "😤 Mood-Food Engine", "🏠 My Thali Builder"])

with tab1:
    menu_text = st.text_area("Paste Swiggy/Zomato menu contents:", placeholder="e.g. 1. Butter Chicken 2. Tandoori Roti 3. Salad")
    if st.button("Rank Menu Intelligence"):
        with st.spinner("WAT-I-EAT is optimizing choices..."):
            prompt = get_system_prompt() + f"TASK: Rank these menu items for goal {st.session_state.user_profile['goal']}. Return JSON {{'ranked_dishes': [{{'name', 'rank', 'reason', 'badge': 'good'|'bad'|'okay'}}]}}"
            try:
                out = client.models.generate_content(model='gemini-2.5-flash', contents=[prompt, menu_text] if menu_text else prompt).text
                ranked = extract_json(out).get('ranked_dishes', [])
                for d in ranked:
                    b_class = "best" if d.get('badge') == 'good' else ("worst" if d.get('badge') == 'bad' else "")
                    emoji = "🟢" if d.get('badge') == 'good' else ("🔴" if d.get('badge') == 'bad' else "🟡")
                    st.markdown(f"""
                        <div class="dish-card {b_class}">
                            <div class="dish-name">{emoji} #{d.get('rank')} {d.get('name')}</div>
                            <div class="dish-reason">{d.get('reason')}</div>
                        </div>
                    """, unsafe_allow_html=True)
            except Exception as e: st.error(str(e))

with tab2:
    st.markdown(f"#### Sensing current state: **{st.session_state.user_profile['mood']}**")
    if st.button("Generate Emotional Fixers"):
        with st.spinner("Finding neuro-food alternatives..."):
            prompt = get_system_prompt() + "TASK: Mood fix alternatives. JSON {'craving', 'suggestions': [{'name', 'emoji', 'why'}]}"
            try:
                out = client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text
                mood_data = extract_json(out)
                st.info(f"Emotional Trigger Detected: Likely craving **{mood_data.get('craving')}**")
                for s in mood_data.get('suggestions', []):
                    st.markdown(f"""
                    <div class="mood-suggestion">
                        <div class="mood-food-name">{s.get('emoji')} {s.get('name')}</div>
                        <div class="mood-food-why">{s.get('why')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e: st.error(str(e))

with tab3:
    if st.button("Construct Optimal Regional Thali"):
        with st.spinner(f"Architecting ₹{st.session_state.user_profile['budget']} {st.session_state.user_profile['region']} plan..."):
            prompt = get_system_prompt() + "TASK: 4-meal plan. JSON {'meals': [{'meal', 'dish', 'cals', 'cost', 'why'}], 'total_cost'}"
            try:
                out = client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text
                thali_data = extract_json(out)
                mcol1, mcol2 = st.columns(2)
                for i, m in enumerate(thali_data.get('meals', [])):
                    col = mcol1 if i % 2 == 0 else mcol2
                    with col:
                        st.markdown(f"""
                        <div class="meal-card">
                            <div class="meal-type">{m.get('meal')}</div>
                            <div class="meal-name">{m.get('dish')}</div>
                            <div class="meal-meta">
                                <div class="meal-meta-item">🔥 <strong>{m.get('cals')}</strong> kcal</div>
                                <div class="meal-meta-item">💰 <strong>₹{m.get('cost')}</strong></div>
                            </div>
                            <div class="meal-why">{m.get('why')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                st.success(f"Full Day Investment: ₹{thali_data.get('total_cost')}")
            except Exception as e: st.error(str(e))

st.markdown('<div class="section-divider" style="margin: 60px 0;"></div>', unsafe_allow_html=True)

# --- ACT 6: YOUR LIFE LOG ---
if st.session_state.history:
    st.markdown('<p class="section-label" style="text-align:center;">Act 06</p>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title" style="text-align:center;">Your Life Log</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc" style="text-align:center; margin: 0 auto 40px;">A chronological history of your nutritional footprint.</p>', unsafe_allow_html=True)
    
    # Chronological history cards
    for i, item in enumerate(reversed(st.session_state.history)):
        meal_name = item.get('food_identified', [{}])[0].get('name', 'Unknown Meal')
        score = item.get('nourish_score', 0)
        c_color = "#10B981" if score > 70 else ("#FBBF24" if score > 40 else "#EF4444")
        
        with st.expander(f"Meal {len(st.session_state.history)-i}: {meal_name} (Score: {score})"):
            l_col1, l_col2 = st.columns([1, 2])
            with l_col1:
                st.markdown(f"""
                <div class="card" style="text-align:center; padding:15px; border-color:{c_color};">
                    <h2 style="color:{c_color};">{score}</h2>
                    <p style="font-size:0.7rem; color:#8080A0;">NourishScore</p>
                </div>
                """, unsafe_allow_html=True)
            with l_col2:
                st.markdown(f"**Energy:** {item.get('total_calories')} kcal")
                st.markdown(f"**The Good:** {item.get('verdict', {}).get('great')}")
                st.markdown(f"**Action:** {item.get('verdict', {}).get('swap_suggestion')}")

# --- ACT 5: VISION FOOTER ---
st.markdown(f"""
<div class="footer">
    <div class="footer-logo">WAT-I-EAT</div>
    <div class="footer-tagline">
        Making healthy eating possible for every Indian
    </div>
    <div style="display: flex; justify-content: center; flex-wrap: wrap;">
        <span class="powered-badge">⚡ Google Gemini 2.5 Flash</span>
        <span class="powered-badge">🔴 AMD AI Inference</span>
        <span class="powered-badge">🇮🇳 Built for India</span>
    </div>
    <div class="footer-copy">
        Built at AMD Slingshot Regional Ideathon 2025 · 
        WAT-I-EAT · {time.strftime("%Y")} · All rights reserved
    </div>
</div>
""", unsafe_allow_html=True)
