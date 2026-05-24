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

def get_base64_logo():
    current_dir = os.path.dirname(__file__)
    logo_path = os.path.join(current_dir, 'Espoon_Palloseura_logo.png')
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

st.set_page_config(page_title="TootScouting Tactical Pro", layout="wide")

st.markdown("""<style>.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }</style>""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV", type=['csv'])

if uploaded_file is not None:
    # قراءة الملف بأمان
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8-sig')
    except:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='cp1252')

    df.columns = df.columns.str.strip()
    st.sidebar.info(f"📁 Columns detected: {list(df.columns)}")

    # ميكانيكية Mapping دفاعية (تحمي من KeyError)
    rename_map = {}
    for col in df.columns:
        c_low = col.lower().replace('_', ' ')
        if 'event' in c_low or 'action' in c_low: rename_map[col] = 'Action'
        elif 'player' in c_low: rename_map[col] = 'Player'
        elif 'tag' in c_low: rename_map[col] = 'Tags'
        elif 'x' in c_low and 'start' in c_low: rename_map[col] = 'x_start'
        elif 'y' in c_low and 'start' in c_low: rename_map[col] = 'y_start'
    
    df = df.rename(columns=rename_map)

    # التحقق من وجود الأعمدة المطلوبة بعد الـ Rename
    required = ['Action', 'Player']
    if all(col in df.columns for col in required):
        df['Action'] = df['Action'].fillna('Unknown')
        df['Player'] = df['Player'].fillna('Unknown')
        df['Tags'] = df['Tags'] if 'Tags' in df.columns else ''
        
        # إحداثيات افتراضية لو مش موجودة
        if 'x_start' not in df.columns: df['x_start'] = 60
        if 'y_start' not in df.columns: df['y_start'] = 40
        
        df['x_scaled'] = df['x_start'] * 1.2
        df['y_scaled'] = df['y_start'] * 0.8
        
        # استكمال باقي الكود بنفس المنطق السابق...
        st.success("✅ Data Loaded Successfully! Ready for analysis.")
    else:
        st.error(f"❌ Columns missing! Please ensure your CSV has columns related to: {required}")
else:
    st.info("👋 Upload a CSV file to start.")
