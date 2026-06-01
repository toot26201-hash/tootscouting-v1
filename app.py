import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import base64
import os
import matplotlib.colors as mcolors
import matplotlib.lines as mlines

# --- 1. إعداد الصفحة والتصميم ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    .premium-player-card { background: #1e293b; border: 2px solid #a47e3c; border-radius: 16px; padding: 24px; }
    .summary-table-container { background: #1e293b; padding: 24px; border-radius: 12px; border: 1px solid #a47e3c; }
    </style>
""", unsafe_allow_html=True)

# --- 2. معالجة البيانات القوية (الخاصة بملفك) ---
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] # حذف الأعمدة الفارغة
    df.columns = df.columns.str.strip()
    
    # ربط أعمدة ملفك بأسماء الكود
    rename_dict = {'Action': 'Action', 'Player': 'Player', 'Tags': 'Tags', 
                   'X1': 'x_start', 'Y1': 'y_start', 'X2': 'x_end', 'Y2': 'y_end'}
    df = df.rename(columns=rename_dict)
    
    # تحويل الإحداثيات (ضرب الكسور في 120 و 80)
    for col in ['x_start', 'y_start', 'x_end', 'y_end']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['x_scaled'] = df['x_start'] * 120
    df['y_scaled'] = df['y_start'] * 80
    df['x_end_scaled'] = df['x_end'] * 120
    df['y_end_scaled'] = df['y_end'] * 80
    
    return df.dropna(subset=['Action', 'Player'])

# --- 3. الدوال البرمجية الأصلية الخاصة بك ---
# (ضع دوال: parse_action_metrics و draw_premium_kde_heatmap و render_player_summary_table هنا)
# ملاحظة: تأكد أنها تستخدم أعمدة x_scaled و y_scaled التي قمنا بإنشائها

# --- 4. الهيكل الرئيسي ---
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    try:
        team_df = process_data(uploaded_file)
        st.success("✅ تم تحميل بيانات المباراة بنجاح!")
        
        # اختيار اللاعب
        player_list = sorted(team_df['Player'].unique().tolist())
        sel_player = st.sidebar.selectbox("🎯 Select Player:", player_list)
        p_df = team_df[team_df['Player'] == sel_player]
        
        # التابات
        tab1, tab2 = st.tabs(["🔥 Heatmap", "🏃‍♂️ Actions"])
        
        with tab1:
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
            fig, ax = pitch.draw(figsize=(10, 7))
            if len(p_df) > 1:
                sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, cmap='viridis', ax=ax)
            st.pyplot(fig)
            
        with tab2:
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
            fig, ax = pitch.draw(figsize=(10, 7))
            for _, row in p_df.iterrows():
                pitch.arrows(row['x_scaled'], row['y_scaled'], row['x_end_scaled'], row['y_end_scaled'], ax=ax, color='green')
            st.pyplot(fig)
            
    except Exception as e:
        st.error(f"خطأ في المعالجة: {e}")
else:
    st.info("👋 يرجى رفع ملف CSV للبدء.")
