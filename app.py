import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
import matplotlib.colors as mcolors
import os
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# (تم تقليص الأنماط CSS لتوفير المساحة، يمكنك الاحتفاظ بالأنماط الخاصة بك كما هي)

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
    
    # تحسين التعرف على الأعمدة لتناسب ملفك (X1, Y1, X2, Y2)
    col_map = {c.lower().strip(): c for c in df.columns}
    
    # اختيار الأعمدة الصحيحة بناءً على ملفك
    x_start = col_map.get('x1')
    y_start = col_map.get('y1')
    x_end = col_map.get('x2')
    y_end = col_map.get('y2')

    if x_start and y_start:
        df['x_scaled'] = df[x_start] * 120
        df['y_scaled'] = df[y_start] * 80
        
        if x_end and y_end:
            df['x_end_scaled'] = df[x_end] * 120
            df['y_end_scaled'] = df[y_end] * 80
        else:
            df['x_end_scaled'] = df['x_scaled']
            df['y_end_scaled'] = df['y_scaled']

    # تنظيف البيانات الأساسية
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df = df.rename(columns={c: 'Tags' for c in df.columns if 'tag' in c.lower()})
    
    df['Action'] = df['Action'].fillna('Unknown')
    df['Player'] = df['Player'].fillna('Unknown')
    
    # دالة الرسم المحدثة
    def draw_premium_kde_heatmap(dataframe, ax):
        # التأكد من وجود الأعمدة قبل الرسم
        if 'x_scaled' in dataframe.columns and 'y_scaled' in dataframe.columns:
            scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
            scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
            sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.04, alpha=0.85, ax=ax)
        else:
            st.error("لم يتم العثور على إحداثيات صالحة للرسم.")

    # --- عرض المحتوى ---
    tab1, tab2 = st.tabs(["🔥 Heatmap", "🏃‍♂️ Actions"])
    
    players = df['Player'].unique()
    sel_player = st.sidebar.selectbox("اختر اللاعب", players)
    p_df = df[df['Player'] == sel_player].copy()
    
    with tab1:
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw()
        draw_premium_kde_heatmap(p_df, ax)
        st.pyplot(fig)
else:
    st.info("يرجى رفع ملف CSV للبدء.")
