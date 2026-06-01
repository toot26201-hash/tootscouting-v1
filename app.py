import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
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

st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# --- CSS Theme ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    .premium-player-card { background: #1e293b; border: 2px solid #a47e3c; border-radius: 16px; padding: 24px; }
    .summary-table-container { background: #1e293b; padding: 24px; border-radius: 12px; border: 1px solid #a47e3c; }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- Sidebar Controls ---
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    # --- معالجة البيانات القوية ---
    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] # حذف الأعمدة الفارغة
    df.columns = df.columns.str.strip()
    
    # تحويل الأسماء لتوحيدها مع الكود
    rename_dict = {'Action': 'Action', 'Player': 'Player', 'X1': 'x_start', 'Y1': 'y_start', 'X2': 'x_end', 'Y2': 'y_end', 'Tags': 'Tags'}
    df = df.rename(columns=rename_dict)
    
    # معالجة إحداثيات LongoMatch (الضرب في 120 و 80)
    for col in ['x_start', 'y_start', 'x_end', 'y_end']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    df['x_scaled'] = df['x_start'] * 120
    df['y_scaled'] = df['y_start'] * 80
    df['x_end_scaled'] = df['x_end'] * 120
    df['y_end_scaled'] = df['y_end'] * 80
    
    df = df.dropna(subset=['Action', 'Player'])
    df['Tags'] = df['Tags'].fillna('').astype(str)
    df['Team'] = 'EPS'
    
    # --- بقية الكود ---
    team_df = df.copy()
    all_selected_layers = ["Normal Passes", "Crosses", "Shots", "Goals", "Tackles", "Ground Duels", "Clearances", "Aerial Duels", "Counterpress"]

    # (هنا يتم وضع دوال parse_action_metrics و draw_premium_kde_heatmap كما هي في كودك الأصلي)
    # ملاحظة: الكود الخاص بك سيعمل الآن لأن الأعمدة x_scaled موجودة وجاهزة
    
    # --- عرض التابات ---
    tab1, tab2, tab3 = st.tabs(["🔥 Heatmap", "🏃‍♂️ Actions", "📊 Stats"])
    
    player_list = sorted(team_df['Player'].unique())
    sel_player = st.sidebar.selectbox("🎯 Select Player:", player_list)
    p_df = team_df[team_df['Player'] == sel_player]

    with tab1:
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        if len(p_df) > 1:
            sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, cmap='viridis', ax=ax)
        st.pyplot(fig)
        
    with tab2:
        st.write("خريطة العمليات للاعب:", sel_player)
        # هنا يمكنك استدعاء دالة parse_action_metrics الخاصة بك
        
    with tab3:
        st.write("إحصائيات اللاعب")

else:
    st.info("👋 يرجى رفع ملف CSV للبدء.")
