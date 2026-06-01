import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
import numpy as np
import base64
import os
import matplotlib.colors as mcolors

# --- 1. الدوال الأصلية للتصميم والرسم ---
def get_base64_logo():
    current_dir = os.path.dirname(__file__)
    possible_paths = ['Espoon_Palloseura_logo.png', 'espoon_palloseura_logo.png']
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

def draw_premium_kde_heatmap(dataframe, ax):
    scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
    scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
    sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.04, alpha=0.85, bw_method=0.28, zorder=1, ax=ax)

# --- 2. معالجة البيانات القوية (مخصصة لملفك) ---
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] # حذف الأعمدة الفارغة
    df.columns = df.columns.str.strip()
    
    # ربط أعمدة ملفك بأسماء الكود
    rename_dict = {'Action': 'Action', 'Player': 'Player', 'Tags': 'Tags', 
                   'X1': 'x_start', 'Y1': 'y_start', 'X2': 'x_end', 'Y2': 'y_end'}
    df = df.rename(columns=rename_dict)
    
    # تحويل الإحداثيات (ضرب الكسور في 120 و 80)
    for col in ['x_start', 'y_start', 'x_end', 'y_end']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['x_scaled'] = df['x_start'] * 120
    df['y_scaled'] = df['y_start'] * 80
    df['x_end_scaled'] = df['x_end'] * 120
    df['y_end_scaled'] = df['y_end'] * 80
    
    return df.dropna(subset=['Action', 'Player'])

# --- 3. إعداد الصفحة ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    .premium-player-card { background: #1e293b; border: 2px solid #a47e3c; border-radius: 16px; padding: 24px; }
</style>""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    team_df = process_data(uploaded_file)
    st.success("✅ تم تحميل بيانات المباراة بنجاح!")
    
    # اختيار اللاعب
    player_list = sorted(team_df['Player'].unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 Select Player:", player_list)
    p_df = team_df[team_df['Player'] == sel_player]
    
    # التابات
    tab1, tab2 = st.tabs(["🔥 Heatmap", "🏃‍♂️ Actions Map"])
    
    with tab1:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
        fig, ax = pitch.draw(figsize=(10, 7))
        if len(p_df) > 1:
            draw_premium_kde_heatmap(p_df, ax)
        st.pyplot(fig)
        
    with tab2:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
        fig, ax = pitch.draw(figsize=(10, 7))
        for _, row in p_df.iterrows():
            if 'Pass' in str(row['Action']):
                pitch.arrows(row['x_scaled'], row['y_scaled'], row['x_end_scaled'], row['y_end_scaled'], ax=ax, color='green')
        st.pyplot(fig)

else:
    st.info("👋 يرجى رفع ملف CSV للبدء.")
