import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors
import os
import base64

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="TootScouting Pro", layout="wide")

# --- 2. دالة تحميل اللوجو ---
def get_base64_logo():
    path = 'Espoon_Palloseura_logo.png'
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# --- 3. معالجة البيانات (تم إصلاح المشكلة هنا) ---
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    # قراءة الملف وتنظيف أسماء الأعمدة من المسافات الزائدة
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # دالة تحويل الإحداثيات (التي كانت تسبب الخطأ)
    def preprocess_data(data):
        # البحث عن الأعمدة بمرونة
        col_map = {c.lower().strip(): c for c in data.columns}
        x1 = col_map.get('x1')
        y1 = col_map.get('y1')
        x2 = col_map.get('x2')
        y2 = col_map.get('y2')
        
        if x1 and y1:
            data['x_scaled'] = data[x1] * 120
            data['y_scaled'] = data[y1] * 80
            if x2 and y2:
                data['x_end_scaled'] = data[x2] * 120
                data['y_end_scaled'] = data[y2] * 80
        
        # التأكد من أسماء الأعمدة الأساسية
        rename_dict = {c: 'Action' for c in data.columns if 'action' in c.lower()}
        rename_dict.update({c: 'Player' for c in data.columns if 'player' in c.lower()})
        data = data.rename(columns=rename_dict)
        return data

    df = preprocess_data(df)

    # --- 4. دالة الرسم (Heatmap) ---
    def draw_premium_kde_heatmap(dataframe, ax):
        # الفحص الذكي: هل الأعمدة موجودة؟
        if 'x_scaled' in dataframe.columns and 'y_scaled' in dataframe.columns:
            scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
            scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
            sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.04, alpha=0.85, ax=ax, zorder=1)
        else:
            st.error("خطأ: البيانات لا تحتوي على إحداثيات صالحة (x1, y1).")

    # --- 5. واجهة العرض (Tabs) ---
    players = df['Player'].dropna().unique()
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب", players)
    p_df = df[df['Player'] == sel_player].copy()
    
    tab1, tab2 = st.tabs(["🔥 Heatmap", "📊 Data Preview"])
    
    with tab1:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
        fig, ax = pitch.draw(figsize=(10, 7))
        draw_premium_kde_heatmap(p_df, ax)
        st.pyplot(fig)

    with tab2:
        st.write("البيانات بعد المعالجة:", p_df.head())

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
