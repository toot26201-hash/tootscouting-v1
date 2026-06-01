import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
import matplotlib.colors as mcolors
import os
import base64

# --- وظائف مساعدة ---
def get_base64_logo():
    possible_paths = ['Espoon_Palloseura_logo.png', 'espoon_palloseura_logo.png']
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

# --- إعدادات الصفحة ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# --- حقن الأنماط (CSS) ---
st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    .premium-player-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 2px solid #a47e3c; border-radius: 16px; padding: 24px; color: white; }
</style>""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- تحميل البيانات ---
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 1. نظام تصحيح الأعمدة الذكي
    col_map = {c.lower().strip(): c for c in df.columns}
    x_start_col = col_map.get('x1') or col_map.get('x')
    y_start_col = col_map.get('y1') or col_map.get('y')
    x_end_col = col_map.get('x2') or col_map.get('x end')
    y_end_col = col_map.get('y2') or col_map.get('y end')

    if x_start_col and y_start_col:
        df['x_scaled'] = df[x_start_col] * 120
        df['y_scaled'] = df[y_start_col] * 80
        if x_end_col and y_end_col:
            df['x_end_scaled'] = df[x_end_col] * 120
            df['y_end_scaled'] = df[y_end_col] * 80
        else:
            df['x_end_scaled'], df['y_end_scaled'] = df['x_scaled'], df['y_scaled']

    # 2. تنظيف البيانات
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df['Player'] = df['Player'].fillna('Unknown').astype(str)

    # --- 3. الدوال التكتيكية ---
    def draw_premium_kde_heatmap(dataframe, ax):
        scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
        if 'x_scaled' in dataframe.columns:
            sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, ax=ax)

    # --- 4. العرض ---
    players = sorted(df['Player'].unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب", players)
    p_df = df[df['Player'] == sel_player].copy()
    
    tab1, tab2 = st.tabs(["🔥 Heatmap", "📋 البيانات"])
    
    with tab1:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
        fig, ax = pitch.draw(figsize=(10, 7))
        draw_premium_kde_heatmap(p_df, ax)
        st.pyplot(fig)
        
    with tab2:
        st.write(p_df.head(10))

else:
    st.info("👋 يرجى رفع ملف CSV للبدء.")
