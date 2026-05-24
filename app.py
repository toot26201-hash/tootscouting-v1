import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
import matplotlib.colors as mcolors
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="TootScouting Pro", layout="wide")

# --- الـ CSS للثيم ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- التحكم ---
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # --- دالة رسم الـ Legend بالخلفية البيضاء ---
    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#00FF66', marker='>', linestyle='-', label='Pass Success', markersize=8),
            mlines.Line2D([], [], color='#FF3333', marker='>', linestyle='-', label='Pass Failed', markersize=8),
            mlines.Line2D([], [], color='#00CCFF', marker='x', label='Tackle', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#FFCC00', marker='*', label='Goal', linestyle='None', markersize=15)
        ]

    # --- تجهيز البيانات للإحداثيات ---
    df['x_scaled'] = df['X Start'] * 1.2
    df['y_scaled'] = df['Y Start'] * 0.8
    df['x_end_scaled'] = df['X End'] * 1.2
    df['y_end_scaled'] = df['Y End'] * 0.8

    # --- رسم التابات ---
    tab1, tab2 = st.tabs(["🏃‍♂️ Action Map", "📊 Data Preview"])
    
    with tab1:
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black')
        pitch.draw(ax=ax)
        
        # رسم الأكشنز (مثال بسيط)
        pitch.arrows(df['x_scaled'], df['y_scaled'], df['x_end_scaled'], df['y_end_scaled'], ax=ax, color='green')
        
        # اللمسة السحرية: خلفية بيضاء للـ Legend
        ax.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), 
                  facecolor='white', edgecolor='black', labelcolor='black')
        
        st.pyplot(fig)

    with tab2:
        st.dataframe(df)

else:
    st.info("👋 ارفع ملف الـ CSV يا بطل عشان نبدأ التحليل.")
