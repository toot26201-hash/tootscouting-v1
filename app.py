import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
from PIL import Image
import os
import matplotlib.colors as mcolors
import numpy as np
import base64

# Function to read and encode the club logo to Base64
def get_base64_logo():
    current_dir = os.path.dirname(__file__)
    possible_paths = [
        os.path.join(current_dir, 'Espoon_Palloseura_logo.png'),
        os.path.join(current_dir, 'espoon_palloseura_logo.png'),
        'Espoon_Palloseura_logo.png',
        'espoon_palloseura_logo.png'
    ]
    
    logo_filename = None
    for path in possible_paths:
        if os.path.exists(path):
            logo_filename = path
            break
            
    if logo_filename and os.path.exists(logo_filename):
        with open(logo_filename, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# 1. Page Config & Strict Dark Premium Theme
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #334155; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #f8fafc !important; }
    .stTabs [data-baseweb="tab"] { background-color: #1e293b; border: 1px solid #334155; border-radius: 6px; color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { background-color: #a47e3c !important; color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- Sidebar Controls ---
st.sidebar.markdown("## 🛠️ Tactical Control Unit")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8-sig')
    except:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='cp1252')

    df.columns = df.columns.str.strip()
    
    # --- التعديل المباشر لمنع الـ KeyError ---
    df['x_scaled'] = df['X1'] * 120
    df['y_scaled'] = df['Y1'] * 80
    
    if 'X2' in df.columns and 'Y2' in df.columns:
        df['x_end_scaled'] = df['X2'] * 120
        df['y_end_scaled'] = df['Y2'] * 80
    else:
        df['x_end_scaled'] = df['x_scaled']
        df['y_end_scaled'] = df['y_scaled']

    # تنظيف الأسماء
    rename_dict = {c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()}
    rename_dict.update({c: 'Player' for c in df.columns if 'player' in c.lower()})
    rename_dict.update({c: 'Tags' for c in df.columns if 'tag' in c.lower()})
    df = df.rename(columns=rename_dict)

    df['Team'] = 'EPS'
    df = df.dropna(subset=['Action', 'Player'])
    df['Tags'] = df['Tags'].fillna('')
    df['Player'] = df['Player'].astype(str).str.strip()

    team_list = ['EPS']
    selected_team = st.sidebar.selectbox("📋 Select Team", team_list)
    team_df = df.copy()

    # --- (باقي الكود الخاص بك كما هو بالكامل) ---
    # يرجى التأكد من لصق الدوال parse_action_metrics و draw_premium_kde_heatmap و render_... هنا
    # كما هي في كودك الأصلي، فهي ستعمل الآن لأن x_scaled موجودة.

else:
    st.info("👋 Please upload a match CSV file on the left sidebar.")
