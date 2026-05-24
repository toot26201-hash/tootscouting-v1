import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
import matplotlib.colors as mcolors

# إعداد الصفحة
st.set_page_config(page_title="TootScouting | Tactical Analysis Pro", layout="wide")

# تنسيق CSS للخلفية البيضاء
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3 { color: #1e293b !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Lab")

# رفع الملف
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    # --- 1. نظام اكتشاف الأعمدة الذكي ---
    col_map_lower = {c.lower().replace('_', ' ').strip(): c for c in df.columns}
    x_col = col_map_lower.get('x start') or col_map_lower.get('x') or col_map_lower.get('xstart')
    y_col = col_map_lower.get('y start') or col_map_lower.get('y') or col_map_lower.get('ystart')

    if x_col and y_col:
        df['x_scaled'] = df[x_col] if df[x_col].max() > 1 else df[x_col] * 120
        df['y_scaled'] = df[y_col] if df[y_col].max() > 1 else df[y_col] * 80
        
        # --- 2. إعداد الملعب بخلفية بيضاء ---
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linewidth=1.5)
        fig, ax = pitch.draw(figsize=(10, 7))
        fig.patch.set_facecolor('#ffffff') 
        
        # --- 3. رسم الهيت ماب المحدثة (للخلفية البيضاء) ---
        scout_lab_colors = ["#f1f5f9", "#bae6fd", "#38bdf8", "#0284c7", "#1e3a8a"]
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("white_mode", scout_lab_colors, N=256)
        sns.kdeplot(x=df['x_scaled'], y=df['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.05, alpha=0.6, ax=ax)
        
        st.pyplot(fig)
        
        # هنا يمكنك استدعاء الدوال الأخرى الخاصة بك (parse_action_metrics) 
        # مع التأكد من استخدام الألوان الداكنة التي اقترحتها لك سابقاً.

    else:
        st.error(f"⚠️ لم نتمكن من اكتشاف أعمدة الإحداثيات. الأعمدة المتاحة: {list(df.columns)}")
else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
