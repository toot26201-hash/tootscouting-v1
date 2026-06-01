import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors
import os
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# --- دالة تحميل اللوجو ---
def get_base64_logo():
    path = 'Espoon_Palloseura_logo.png'
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- تحميل البيانات وتجهيزها ---
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 1. نظام التعرف على الأعمدة بناءً على ملفك
    col_map = {c.lower().strip(): c for c in df.columns}
    x_col = col_map.get('x1')
    y_col = col_map.get('y1')
    x_e_col = col_map.get('x2')
    y_e_col = col_map.get('y2')

    # 2. تحويل الإحداثيات فوراً
    if x_col and y_col:
        df['x_scaled'] = df[x_col] * 120
        df['y_scaled'] = df[y_col] * 80
        if x_e_col and y_e_col:
            df['x_end_scaled'] = df[x_e_col] * 120
            df['y_end_scaled'] = df[y_e_col] * 80
        else:
            df['x_end_scaled'] = df['x_scaled']
            df['y_end_scaled'] = df['y_scaled']
    
    # تنظيف الأسماء
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    
    # دالة الرسم (تم إصلاحها)
    def draw_premium_kde_heatmap(dataframe, ax):
        scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
        # الرسم يعتمد الآن على x_scaled التي أنشأناها في الأعلى
        sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.04, alpha=0.85, ax=ax, zorder=1)

    # --- واجهة العرض ---
    players = df['Player'].dropna().unique()
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب", players)
    p_df = df[df['Player'] == sel_player].copy()
    
    tab1, tab2 = st.tabs(["🔥 Heatmap", "📊 Data Preview"])
    
    with tab1:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
        fig, ax = pitch.draw(figsize=(10, 7))
        if 'x_scaled' in p_df.columns:
            draw_premium_kde_heatmap(p_df, ax)
            st.pyplot(fig)
        else:
            st.error("لم يتم العثور على أعمدة الإحداثيات الصحيحة!")

    with tab2:
        st.write("بيانات اللاعب المختارة:", p_df.head())

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
