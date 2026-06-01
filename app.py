import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors
import numpy as np

# 1. تعريف الدوال أولاً (هذا يحل الـ NameError)
def draw_premium_kde_heatmap(dataframe, ax):
    scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
    scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
    sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.04, alpha=0.85, bw_method=0.28, zorder=1, ax=ax)

def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip()
    rename_dict = {'Action': 'Action', 'Player': 'Player', 'Tags': 'Tags', 
                   'X1': 'x_start', 'Y1': 'y_start', 'X2': 'x_end', 'Y2': 'y_end'}
    df = df.rename(columns=rename_dict)
    for col in ['x_start', 'y_start', 'x_end', 'y_end']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['x_scaled'] = df['x_start'] * 120
    df['y_scaled'] = df['y_start'] * 80
    return df.dropna(subset=['Action', 'Player'])

# 2. واجهة التطبيق
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    team_df = process_data(uploaded_file)
    
    # اختيار اللاعب
    player_list = sorted(team_df['Player'].unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 Select Player:", player_list)
    p_df = team_df[team_df['Player'] == sel_player].copy()
    
    # الرسم
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # استدعاء الدالة الآن بعد أن تم تعريفها في الأعلى
    draw_premium_kde_heatmap(p_df, ax)
    st.pyplot(fig)
else:
    st.info("👋 يرجى رفع ملف CSV.")
