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
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

# Page Config
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    h1, h2, h3, p { color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- Sidebar Controls ---
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    
    # Mapping
    rename_dict = {}
    for col in df.columns:
        c_low = col.lower().replace('_', ' ').strip()
        if 'event type' in c_low or c_low in ['action', 'event', 'action type']: rename_dict[col] = 'Action'
        elif 'player' in c_low: rename_dict[col] = 'Player'
        elif 'tag' in c_low: rename_dict[col] = 'Tags'
    df = df.rename(columns=rename_dict)
    
    df['Team'] = 'EPS'
    df = df.dropna(subset=['Action', 'Player'])
    df['Tags'] = df['Tags'].fillna('')

    # Coordinates
    col_map_lower = {c.lower().replace('_', ' ').strip(): c for c in df.columns}
    x_start = col_map_lower.get('x start') or col_map_lower.get('x')
    y_start = col_map_lower.get('y start') or col_map_lower.get('y')
    
    if x_start and y_start:
        df['x_scaled'] = df[x_start] if df[x_start].max() > 1 else df[x_start] * 120
        df['y_scaled'] = df[y_start] if df[y_start].max() > 1 else df[y_start] * 80
        df['x_end_scaled'] = df['x_scaled'] # Simplified
        df['y_end_scaled'] = df['y_scaled']
    
    # Legend Logic
    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#2ecc71', marker='>', label='Pass Success', linestyle='-', markersize=8),
            mlines.Line2D([], [], color='#e74c3c', marker='>', label='Pass Failed', linestyle='-', markersize=8),
            mlines.Line2D([], [], color='#38bdf8', marker='>', label='Cross Success', linestyle='-', markersize=8),
            mlines.Line2D([], [], color='#ef4444', marker='>', label='Cross Failed', linestyle='--', markersize=8),
            mlines.Line2D([], [], color='#FF69B4', marker='>', label='Through Ball', linestyle='-', markersize=8),
            mlines.Line2D([], [], color='#fbbf24', marker='>', label='Key Pass', linestyle='-', markersize=10),
            mlines.Line2D([], [], color='#3b82f6', marker='*', label='Shot On-Target', linestyle='None', markersize=12),
            mlines.Line2D([], [], color='#ef4444', marker='*', label='Shot Off-Target', linestyle='None', markersize=12),
            mlines.Line2D([], [], color='#60a5fa', marker='x', label='Tackle', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#c084fc', marker='d', label='Clearance', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#34d399', marker='s', label='Ground Duel', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#f87171', marker='^', label='Aerial Duel', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#f87171', marker='x', label='Foul', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#0f172a', marker='o', label='Counterpress', linestyle='None', markersize=8),
            mlines.Line2D([], [], color='#fbbf24', marker='*', label='Goal', linestyle='None', markersize=15)
        ]

    # Parsing & Drawing (Legend with white background)
    def apply_legend(ax, handles):
        ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1.01, 1), 
                  fontsize='small', framealpha=1, facecolor='#ffffff', edgecolor='#334155', labelcolor='black')

    # ... (باقي دوال الرسم مثل parse_action_metrics و draw_premium_kde_heatmap كما هي)
    # ملاحظة: تأكد عند استدعاء ax.legend في كل Tabs أنك تستخدم دالة apply_legend المذكورة أعلاه.

    # مثال لتطبيق التغيير في التاب:
    # ax_ind_all.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), 
    #                   fontsize='small', framealpha=1, facecolor='#ffffff', edgecolor='#334155', labelcolor='black')

    st.success("تم تحديث إعدادات الألوان بنجاح!")
else:
    st.info("يرجى رفع ملف CSV للبدء.")
