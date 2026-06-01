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
    possible_paths = [
        os.path.join(current_dir, 'Espoon_Palloseura_logo.png'),
        os.path.join(current_dir, 'espoon_palloseura_logo.png'),
        'Espoon_Palloseura_logo.png',
        'espoon_palloseura_logo.png'
    ]
    logo_filename = None
    for path in possible_paths:
        if os.path.exists(path):
            logo_filename = path
            break
    if logo_filename and os.path.exists(logo_filename):
        with open(logo_filename, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# 1. Page Config
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# (CSS هنا يبقى كما هو في كودك الأصلي...)
st.markdown("""<style> .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; } </style>""", unsafe_allow_html=True)

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
    
    # --- التعديل الجوهري هنا: تصحيح الأعمدة ---
    # ننشئ قاموس للبحث عن الأعمدة بأي حالة أحرف
    col_map = {c.lower().strip(): c for c in df.columns}
    
    # البحث عن الأعمدة الصحيحة (X1, Y1, X2, Y2)
    x_start_col = col_map.get('x1') or col_map.get('x')
    y_start_col = col_map.get('y1') or col_map.get('y')
    x_end_col = col_map.get('x2')
    y_end_col = col_map.get('y2')

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

    # تنظيف الأسماء الأساسية
    rename_dict = {c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()}
    rename_dict.update({c: 'Player' for c in df.columns if 'player' in c.lower()})
    rename_dict.update({c: 'Tags' for c in df.columns if 'tag' in c.lower()})
    df = df.rename(columns=rename_dict)
    
    df['Team'] = 'EPS'
    df = df.dropna(subset=['Action', 'Player'])
    df['Tags'] = df['Tags'].fillna('')
    df['Player'] = df['Player'].astype(str).str.strip()

    # --- باقي الكود الخاص بك (الدوال و الـ Tabs) ---
    # تأكد من نسخ دالة draw_premium_kde_heatmap و parse_action_metrics هنا كما كانت في كودك الأصلي
    # وسوف تعمل الآن لأن الأعمدة x_scaled و y_scaled أصبحت موجودة ومضمونة.
    
    # ... ضع بقية كودك من أول def get_full_legend(): إلى نهاية الملف هنا ...
    
else:
    st.info("👋 Please upload a match CSV file.")
