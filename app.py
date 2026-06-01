import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
import numpy as np
import base64
import os
import matplotlib.colors as mcolors

# 1. الإعدادات والتصميم
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# (ضع هنا دالة get_base64_logo() الخاصة بك)

st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    .premium-player-card { background: #1e293b; border: 2px solid #a47e3c; border-radius: 16px; padding: 24px; }
    .summary-table-container { background: #1e293b; padding: 24px; border-radius: 12px; border: 1px solid #a47e3c; }
</style>""", unsafe_allow_html=True)

# 2. المعالجة الذكية (هذه هي الخطوة التي تحل الـ KeyError)
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip()
    
    rename_dict = {'Action': 'Action', 'Player': 'Player', 'Tags': 'Tags', 
                   'X1': 'x_start', 'Y1': 'y_start', 'X2': 'x_end', 'Y2': 'y_end'}
    df = df.rename(columns=rename_dict)
    
    # تحويل الإحداثيات فوراً
    for col in ['x_start', 'y_start', 'x_end', 'y_end']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['x_scaled'] = df['x_start'] * 120
    df['y_scaled'] = df['y_start'] * 80
    df['x_end_scaled'] = df['x_end'] * 120
    df['y_end_scaled'] = df['y_end'] * 80
    
    return df.dropna(subset=['Action', 'Player'])

# 3. الدوال (ضع دوالك الأصلية هنا: parse_action_metrics, draw_premium_kde_heatmap, etc.)
# --- [تأكد أن الدوال هنا تستخدم x_scaled و y_scaled كما في الكود الذي أرسلته أنت] ---

# 4. الهيكل الرئيسي
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    # المعالجة هنا
    team_df = process_data(uploaded_file)
    
    # اختيار اللاعب
    player_list = sorted([p for p in team_df['Player'].unique() if str(p).strip() != ''])
    sel_player = st.sidebar.selectbox("🎯 Focus Player:", player_list)
    p_df = team_df[team_df['Player'] == sel_player].copy()
    
    # التابات
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔥 Heatmap", "🏃‍♂️ Actions", "📊 Stats", "👥 Team Heat", "🛡️ Team Defense"])
    
    with tab1:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
        fig, ax = pitch.draw(figsize=(10, 7))
        # استخدام دالتك هنا
        if 'x_scaled' in p_df.columns:
            draw_premium_kde_heatmap(p_df, ax) 
        st.pyplot(fig)
    
    # [أكمل باقي التابات بنفس الطريقة...]

else:
    st.info("👋 يرجى رفع ملف CSV للبدء.")
