import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
import os
import matplotlib.colors as mcolors
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
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

# --- Page Config ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# --- Custom CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #334155; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #f8fafc !important; }
    .premium-player-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 2px solid #a47e3c; border-radius: 16px; padding: 24px; }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- Sidebar Controls ---
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8-sig')
    except:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='cp1252')

    # تنظيف الأسماء
    df.columns = df.columns.str.strip()
    
    # تحسين الربط (Mapping)
    rename_dict = {}
    for col in df.columns:
        c_low = col.lower().strip()
        if 'event' in c_low or 'action' in c_low: rename_dict[col] = 'Action'
        elif 'player' in c_low: rename_dict[col] = 'Player'
        elif 'tag' in c_low: rename_dict[col] = 'Tags'
    df = df.rename(columns=rename_dict)

    # --- التعديل الجوهري لمنع KeyError ---
    required_cols = ['Action', 'Player']
    if all(col in df.columns for col in required_cols):
        df = df.dropna(subset=required_cols)
    else:
        st.error(f"❌ خطأ: لم يتم العثور على الأعمدة المطلوبة. الأعمدة الموجودة هي: {df.columns.tolist()}")
        st.stop()

    df['Team'] = 'EPS'
    df['Tags'] = df['Tags'].fillna('')
    df['Player'] = df['Player'].astype(str).str.strip()

    # --- باقي الكود الخاص بك ---
    # (ملاحظة: يمكنك وضع بقية الدوال ورسم الرسوم البيانية هنا كما كانت في كودك الأصلي)
    st.success("✅ تم تحميل البيانات بنجاح!")
    
    # مثال بسيط لاستكمال العرض
    st.write("معاينة البيانات:", df.head())

else:
    st.info("👋 الرجاء رفع ملف CSV للبدء.")
