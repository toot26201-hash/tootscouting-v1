import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
import os
import matplotlib.colors as mcolors
import numpy as np
import base64

# --- إعداد الصفحة ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# --- الدوال التحليلية (تم تعريفها قبل الاستخدام) ---
def get_full_legend():
    return [
        mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', label='Pass Success', markersize=8),
        mlines.Line2D([], [], color='#e74c3c', marker='>', linestyle='-', label='Pass Failed', markersize=8),
        mlines.Line2D([], [], color='blue', marker='>', linestyle='-', label='Cross Success', markersize=8),
        mlines.Line2D([], [], color='red', marker='>', linestyle='--', label='Cross Failed', markersize=8),
        mlines.Line2D([], [], color='#FF69B4', marker='>', linestyle='-', label='Through Ball', markersize=8),
        mlines.Line2D([], [], color='#fbbf24', marker='>', linestyle='-', label='Key Pass 🔑', markersize=10, linewidth=3),
        mlines.Line2D([], [], color='#2563eb', marker='*', label='Shot On-Target', linestyle='None', markersize=12),
        mlines.Line2D([], [], color='#dc2626', marker='*', label='Shot Off-Target', linestyle='None', markersize=12),
        mlines.Line2D([], [], color='blue', marker='x', label='Tackle', linestyle='None', markersize=10),
        mlines.Line2D([], [], color='purple', marker='d', label='Clearance', linestyle='None', markersize=10),
        mlines.Line2D([], [], color='gold', marker='*', label='Goal', linestyle='None', markersize=15)
    ]

def draw_premium_kde_heatmap(dataframe, ax):
    scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
    scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
    sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.04, alpha=0.85, bw_method=0.28, zorder=1, ax=ax)

# --- المعالجة الذكية للبيانات ---
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    # تحويل الأسماء
    rename_dict = {'Action': 'Action', 'Player': 'Player', 'Tags': 'Tags', 'X1': 'x_start', 'Y1': 'y_start', 'X2': 'x_end', 'Y2': 'y_end'}
    df = df.rename(columns=rename_dict)
    
    # حساب الإحداثيات (هنا السر: يتم الحساب فوراً لكل البيانات)
    for col in ['x_start', 'y_start', 'x_end', 'y_end']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['x_scaled'] = df['x_start'] * 120
    df['y_scaled'] = df['y_start'] * 80
    df['x_end_scaled'] = df['x_end'] * 120
    df['y_end_scaled'] = df['y_end'] * 80
    return df.dropna(subset=['Action', 'Player'])

# --- التنفيذ ---
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV", type=['csv'])

if uploaded_file is not None:
    # نقوم بالمعالجة مرة واحدة هنا
    full_df = process_data(uploaded_file)
    
    player_list = sorted([str(p) for p in full_df['Player'].unique() if str(p).strip() not in ['nan', '']])
    sel_player = st.sidebar.selectbox("🎯 Select Player:", player_list)
    p_df = full_df[full_df['Player'] == sel_player].copy()

    # التابات
    tabs = st.tabs(["🔥 Player Heatmap", "🏃‍♂️ Player Actions", "👥 Team Heatmap", "🛡️ Team Defense"])
    
    with tabs[0]: # Player Heatmap
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw()
        draw_premium_kde_heatmap(p_df, ax)
        st.pyplot(fig)

    with tabs[2]: # Team Heatmap
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw()
        draw_premium_kde_heatmap(full_df, ax)
        st.pyplot(fig)

    with tabs[3]: # Team Defense
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw()
        def_df = full_df[full_df['Action'].str.contains('Tackle|Clearance', case=False, na=False)]
        pitch.scatter(def_df.x_scaled, def_df.y_scaled, ax=ax, color='red', marker='x')
        st.pyplot(fig)
else:
    st.info("👋 يرجى رفع ملف CSV.")
