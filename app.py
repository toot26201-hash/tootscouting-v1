import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
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

# --- 3. تحميل البيانات (مع إصلاح الأعمدة) ---
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تصحيح الأعمدة (الجزء الذي كان يسبب الخطأ)
    df = df.rename(columns={'X1': 'x start', 'Y1': 'y start', 'X2': 'x end', 'Y2': 'y end'})
    
    # إنشاء الأعمدة المطلوبة
    df['x_scaled'] = df['x start'] * 120
    df['y_scaled'] = df['y start'] * 80
    df['x_end_scaled'] = df['x end'] * 120
    df['y_end_scaled'] = df['y end'] * 80
    
    # تنظيف الأسماء (Action, Player, Tags)
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df = df.rename(columns={c: 'Tags' for c in df.columns if 'tag' in c.lower()})
    df['Player'] = df['Player'].fillna('Unknown').astype(str)
    
    # --- 4. دمج دوالك هنا ---
    # ضع هنا دالة draw_premium_kde_heatmap ودالة parse_action_metrics 
    # ودالة render_player_summary_table كما كانت في كودك الأصلي
    
    def draw_premium_kde_heatmap(dataframe, ax):
        scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
        sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.04, alpha=0.85, ax=ax, zorder=1)

    # --- 5. التنفيذ ---
    players = sorted(df['Player'].unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب", players)
    p_df = df[df['Player'] == sel_player].copy()
    
    tab1, tab2, tab3 = st.tabs(["🔥 Heatmap", "🏃‍♂️ Actions", "📊 Stats"])
    
    with tab1:
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        draw_premium_kde_heatmap(p_df, ax)
        st.pyplot(fig)
        
    with tab2:
        st.write("هنا ستظهر خرائط التحركات (ضع دالة parse_action_metrics الخاصة بك هنا)")
        
    with tab3:
        st.write("هنا ستظهر الجداول والإحصائيات")

else:
    st.info("👋 يرجى رفع الملف.")
