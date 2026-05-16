import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines  # تم إصلاح السطر هنا بنجاح!
import seaborn as sns
from PIL import Image
import os
import matplotlib.colors as mcolors
import numpy as np

# 1. Page Config & Strict Dark Premium Theme (TootScouting Global Style)
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

st.markdown("""
    <style>
    /* Global Background and Text Color */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: #f8fafc !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #334155;
    }
    
    /* Text Typography Upgrades */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #f8fafc !important;
    }
    
    /* Custom Navigation Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #0f172a;
        padding: 8px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        color: #94a3b8 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #a47e3c !important; 
        color: #ffffff !important;
        border-color: #a47e3c !important;
    }

    /* PREMIUM SCOUTLAB PLAYER CARD DESIGN */
    .premium-player-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid #a47e3c;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
    }
    .premium-card-left {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .premium-player-img-wrapper {
        position: relative;
        width: 110px;
        height: 110px;
        border-radius: 50%;
        border: 3px solid #a47e3c;
        background-color: #1e293b;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 15px rgba(164, 126, 60, 0.4);
    }
    .premium-player-avatar {
        font-size: 55px;
    }
    .premium-player-meta h2 {
        margin: 0;
        font-size: 2rem !important;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .premium-player-meta p {
        margin: 4px 0 0 0;
        font-size: 1rem;
        color: #94a3b8;
        font-weight: 500;
    }
    .premium-card-right {
        display: flex;
        gap: 15px;
    }
    .premium-stat-tile {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(164, 126, 60, 0.3);
        border-radius: 12px;
        padding: 15px;
        min-width: 100px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .premium-stat-tile-large {
        background: linear-gradient(135deg, #a47e3c 0%, #6d4c1b 100%);
        border: 1px solid #a47e3c;
    }
    .premium-tile-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }
    .premium-tile-lbl {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 6px;
        letter-spacing: 0.5px;
    }
    .premium-stat-tile-large .premium-tile-lbl {
        color: #f1f5f9;
    }

    /* Player Performance Summary Table Theme with Neon Progress Bars */
    .summary-table-container {
        background: #1e293b;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
        margin-bottom: 25px;
        border: 1px solid rgba(164, 126, 60, 0.3);
    }
    .summary-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 16px;
        border-bottom: 2px solid #a47e3c;
        padding-bottom: 8px;
    }
    .player-summary-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
    }
    .player-summary-table th {
        background-color: #0f172a;
        color: #94a3b8;
        font-weight: 600;
        padding: 14px;
        font-size: 0.9rem;
        border-bottom: 2px solid #334155;
    }
    .player-summary-table td {
        padding: 14px;
        font-size: 0.95rem;
        color: #e2e8f0;
        border-bottom: 1px solid #334155;
    }
    .player-summary-table tr:hover {
        background-color: rgba(164, 126, 60, 0.1);
    }
    .stat-badge {
        background-color: #0f172a;
        color: #38bdf8;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }
    
    /* Progress Bar Neon Design */
    .progress-bar-bg {
        background-color: #0f172a;
        border-radius: 6px;
        width: 140px;
        height: 12px;
        display: inline-block;
        margin-right: 12px;
        vertical-align: middle;
        overflow: hidden;
        border: 1px solid #334155;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #a47e3c 0%, #38bdf8 100%);
        height: 100%;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# دالة دمج لوجو النادي الشفاف في سنتر الملعب
def add_club_logo(ax):
    logo_filename = 'Espoon_Palloseura_logo.png'
    if os.path.exists(logo_filename):
        try:
            img = Image.open(logo_filename)
            ax.imshow(img, extent=[45, 75, 25, 55], alpha=0.18, zorder=2)
        except:
            pass

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- Sidebar Controls ---
st.sidebar.markdown("## 🛠️ Tactical Control Unit")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    df = df.dropna(subset=['Action', 'Team'])
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("📋 Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    with st.sidebar.expander("🎯 Passing Filters", expanded=True):
        selected_passes = st.multiselect("Pass Types:", ["Normal Passes", "Crosses", "Through Balls", "Corners", "Free Kicks"], default=["Normal Passes", "Crosses"])
        
    with st.sidebar.expander("
