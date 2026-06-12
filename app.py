import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Tactical Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    # تحجيم الإحداثيات
    df['x_scaled'], df['y_scaled'] = df['x1'] * 1.2, df['y1'] * 0.8
    df['x2_scaled'], df['y2_scaled'] = df['x2'] * 1.2, df['y2'] * 0.8

    # تصنيف الأكشن
    def classify(row):
        val = str(row['Action']).lower()
        x, y = row['x_scaled'], row['y_scaled']
        if (102 <= x <= 120) and (18 <= y <= 62): return "Box Touch"
        if (80 <= x <= 100) and (30 <= y <= 50): return "Zone 14"
        return "Action"

    df['Type'] = df.apply(classify, axis=1)

    # اختيار الأكشنات
    all_actions = df['Type'].unique().tolist()
    selected_actions = st.sidebar.multiselect("Select Tactical Actions:", options=all_actions, default=all_actions)
    filtered_df = df[df['Type'].isin(selected_actions)]

    col1, col2 = st.columns(2)
    
    # 1. ملعب الأسهم (يظهر كل الأكشنات كأسهم)
    with col1:
        st.subheader("📍 Movement & Actions")
        fig1, ax1 = plt.subplots(figsize=(10, 7))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax1)
        fig1.patch.set_facecolor('#1a1a1a')
        
        for _, row in filtered_df.iterrows():
            pitch.arrows(row['x_scaled'], row['y_scaled'], row['x2_scaled'], row['y2_scaled'], 
                         color='#00ffcc', width=2, headwidth=4, headlength=4, ax=ax1)
        st.pyplot(fig1)

    # 2. ملعب اللمسات (دوائر للمناطق الخاصة)
    with col2:
        st.subheader("🔥 Key Zones Touches")
        fig2, ax2 = plt.subplots(figsize=(10, 7))
        pitch.draw(ax=ax2)
        fig2.patch.set_facecolor('#1a1a1a')
        
        for act in ["Box Touch", "Zone 14"]:
            if act in selected_actions:
                subset = filtered_df[filtered_df['Type'] == act]
                color = '#FFD700' if act == "Zone 14" else '#FF4500'
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color=color, s=200, edgecolors='white', ax=ax2, label=act)
        
        ax2.legend(loc='upper right', facecolor='#222222', labelcolor='white')
        st.pyplot(fig2)
