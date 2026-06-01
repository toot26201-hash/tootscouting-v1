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

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #334155; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #f8fafc !important; }
    .stTabs [data-baseweb="tab"] { background-color: #1e293b; border: 1px solid #334155; border-radius: 6px; color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { background-color: #a47e3c !important; color: #ffffff !important; }
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
    
    # --- إصلاح جذري لإسماء الأعمدة ---
    # تحويل X1/Y1 إلى الأسماء التي يتوقعها كودك تلقائياً
    rename_map = {}
    if 'X1' in df.columns: rename_map['X1'] = 'x start'
    if 'Y1' in df.columns: rename_map['Y1'] = 'y start'
    if 'X2' in df.columns: rename_map['X2'] = 'x end'
    if 'Y2' in df.columns: rename_map['Y2'] = 'y end'
    df = df.rename(columns=rename_map)
    
    # تحويل الإحداثيات (Scaling)
    col_map_lower = {c.lower().strip(): c for c in df.columns}
    x_start_col = col_map_lower.get('x start')
    y_start_col = col_map_lower.get('y start')
    x_end_col = col_map_lower.get('x end')
    y_end_col = col_map_lower.get('y end')

    if x_start_col and y_start_col:
        df['x_scaled'] = df[x_start_col] * 120
        df['y_scaled'] = df[y_start_col] * 80
        if x_end_col and y_end_col:
            df['x_end_scaled'] = df[x_end_col] * 120
            df['y_end_scaled'] = df[y_end_col] * 80
        else:
            df['x_end_scaled'] = df['x_scaled']
            df['y_end_scaled'] = df['y_scaled']

    # --- باقي الكود الأصلي ---
    # (هنا يكمل كودك الأصلي...)
    # بما أننا قمنا بتحويل X1 و Y1 إلى x start و y start في الأعلى، 
    # فإن باقي كودك سيعمل الآن دون أي تعديل إضافي.
    
    # انسخ بقية الكود الخاص بك من هنا للأسفل
    
else:
    st.info("👋 Please upload a match CSV file on the left sidebar.")
