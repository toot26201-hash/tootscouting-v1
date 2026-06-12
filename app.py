import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Tactical Analysis")

# تحميل البيانات
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    # تحويل الإحداثيات (سواء كانت 0-100 أو 0-120، سنقوم بضبطها لـ 120x80)
    df['x_scaled'], df['y_scaled'] = df['x1'] * 1.2, df['y1'] * 0.8
    df['x2_scaled'], df['y2_scaled'] = df['x2'] * 1.2, df['y2'] * 0.8

    # دالة التصنيف والمنطق المكاني
    def classify(row):
        val = str(row['Action']).lower()
        x, y = row['x_scaled'], row['y_scaled']
        # تعريف المناطق
        in_box = (102 <= x <= 120) and (18 <= y <= 62)
        in_z14 = (80 <= x <= 100) and (30 <= y <= 50)
        
        if 'cross' in val: return "Cross"
        if 'corner' in val: return "Corner"
        if 'shot' in val: return "Shot"
        if in_box: return "Box Touch"
        if in_z14: return "Zone 14"
        return "Action"

    df['Type'] = df.apply(classify, axis=1)

    # الفلترة
    selected_actions = st.sidebar.multiselect("Select Tactical Actions:", options=df['Type'].unique().tolist(), default=df['Type'].unique().tolist())
    filtered_df = df[df['Type'].isin(selected_actions)]

    # الرسم
    col1, col2 = st.columns(2)
    
    # 1. ملعب الأسهم (كل شيء إلا البوكس والزونات)
    with col1:
        st.subheader("📍 Movement & Actions (Arrows)")
        fig1, ax1 = plt.subplots(figsize=(10, 7))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax1)
        fig1.patch.set_facecolor('#1a1a1a')
        
        for _, row in filtered_df.iterrows():
            if row['Type'] not in ["Box Touch", "Zone 14"]:
                pitch.arrows(row['x_scaled'], row['y_scaled'], row['x2_scaled'], row['y2_scaled'], 
                             color='#00ffcc', width=2, headwidth=4, headlength=4, ax=ax1)
        st.pyplot(fig1)

    # 2. ملعب اللمسات والزونات (الدوائر فقط)
    with col2:
        st.subheader("🔥 Key Zones & Touches (Markers)")
        fig2, ax2 = plt.subplots(figsize=(10, 7))
        pitch.draw(ax=ax2)
        fig2.patch.set_facecolor('#1a1a1a')
        
        # رسم الدوائر فقط
        for act in ["Box Touch", "Zone 14"]:
            if act in selected_actions:
                subset = filtered_df[filtered_df['Type'] == act]
                color = '#FFD700' if act == "Zone 14" else '#FF4500'
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color=color, s=200, edgecolors='white', ax=ax2, label=act)
        
        ax2.legend(loc='upper right', facecolor='#222222', labelcolor='white')
        st.pyplot(fig2)
