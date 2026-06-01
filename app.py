import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
from PIL import Image
import os
import matplotlib.colors as mcolors
import numpy as np
import base64

# Function to read and encode the club logo to Base64
def get_base64_logo():
    current_dir = os.path.dirname(__file__)
    possible_paths = ['Espoon_Palloseura_logo.png', 'espoon_palloseura_logo.png']
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

# --- إعدادات الصفحة والأنماط (CSS) ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    /* بقية الـ CSS الخاص بك كما هو */
    </style>
""", unsafe_allow_html=True)

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
    
    # --- التعديل الجوهري: نظام التعرف على الأعمدة ---
    col_map = {c.lower().strip(): c for c in df.columns}
    x_start_col = col_map.get('x1') or col_map.get('x')
    y_start_col = col_map.get('y1') or col_map.get('y')
    x_end_col = col_map.get('x2') or col_map.get('x end')
    y_end_col = col_map.get('y2') or col_map.get('y end')

    # تحويل الإحداثيات (Scaling)
    if x_start_col and y_start_col:
        df['x_scaled'] = df[x_start_col] * 120
        df['y_scaled'] = df[y_start_col] * 80
        if x_end_col and y_end_col:
            df['x_end_scaled'] = df[x_end_col] * 120
            df['y_end_scaled'] = df[y_end_col] * 80
        else:
            df['x_end_scaled'] = df['x_scaled']
            df['y_end_scaled'] = df['y_scaled']

    # --- استكمال تجهيز البيانات (Rename & Drop) ---
    rename_dict = {c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()}
    rename_dict.update({c: 'Player' for c in df.columns if 'player' in c.lower()})
    rename_dict.update({c: 'Tags' for c in df.columns if 'tag' in c.lower()})
    df = df.rename(columns=rename_dict)
    
    df['Team'] = 'EPS'
    df = df.dropna(subset=['Action', 'Player'])
    
    # --- هنا تستمر باقي الدوال الخاصة بك ---
    # ضع هنا دالة draw_premium_kde_heatmap ودالة parse_action_metrics 
    # ودوال الـ Render التي كانت موجودة في كودك الأصلي كما هي تماماً.

    # ملاحظة: دالة draw_premium_kde_heatmap ستعمل الآن لأن x_scaled موجودة
    def draw_premium_kde_heatmap(dataframe, ax):
        scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
        sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.04, alpha=0.85, bw_method=0.28, zorder=1, ax=ax)

    # --- تكملة الكود ---
    # استمر في وضع منطق الـ Tabs والـ Pitch كما في كودك الأصلي
    
else:
    st.info("👋 Please upload a match CSV file on the left sidebar to generate the dynamic dashboard.")
