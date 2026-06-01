import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors
import os
import base64

# --- 1. الدوال الأصلية كما هي ---
def get_base64_logo():
    possible_paths = ['Espoon_Palloseura_logo.png', 'espoon_palloseura_logo.png']
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- 3. تحميل البيانات (مع إصلاح الأعمدة) ---
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # إصلاح الأعمدة (الخطوة التي كانت تسبب الانهيار)
    # نربط أعمدة ملفك X1, Y1 بما يتوقعه الكود
    df = df.rename(columns={'X1': 'x start', 'Y1': 'y start', 'X2': 'x end', 'Y2': 'y end'})
    df['x_scaled'] = df['x start'] * 120
    df['y_scaled'] = df['y start'] * 80
    
    # تنظيف الأسماء (Action, Player)
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df['Player'] = df['Player'].fillna('Unknown').astype(str)
    
    # --- 4. واجهة العرض (Tabs) ---
    players = sorted(df['Player'].unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب", players)
    p_df = df[df['Player'] == sel_player].copy()
    
    # تقسيم الشاشة إلى Tabs
    tab1, tab2, tab3 = st.tabs(["🔥 Heatmap", "📋 البيانات", "📊 جدول الإحصائيات"])
    
    with tab1:
        st.subheader(f"Heatmap: {sel_player}")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
        fig, ax = pitch.draw(figsize=(10, 7))
        scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
        sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], cmap=scout_cmap, fill=True, ax=ax)
        st.pyplot(fig)
        
    with tab2:
        st.subheader("سجل الأكشن الخاص باللاعب")
        st.dataframe(p_df[['Time', 'Action', 'Tags']])
        
    with tab3:
        st.subheader("إحصائيات ملخصة")
        st.write(f"إجمالي عدد الأكشن: {len(p_df)}")
        st.write(p_df['Action'].value_counts())

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
