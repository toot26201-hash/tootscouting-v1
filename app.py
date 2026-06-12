import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Tactical Advanced Analysis")

# تحميل البيانات
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80

    # دالة تحديد المناطق التكتيكية
    def get_tactical_zone(x, y):
        # Final Third: X > 80
        # Zone 14: X (80-100), Y (30-50)
        # Penalty Box: X (102-120), Y (18-62)
        if 102 <= x <= 120 and 18 <= y <= 62: return "Penalty Box"
        if 80 <= x <= 100 and 30 <= y <= 50: return "Zone 14"
        if x >= 80: return "Final Third"
        return "Other"

    # تصنيف ذكي
    def classify(row):
        val = str(row['Action']).lower()
        x, y = row['x_scaled'], row['y_scaled']
        
        if 'cross' in val or 'عرضية' in val: return "Cross"
        if 'corner' in val or 'ركنية' in val: return "Corner"
        if 'shot' in val or 'تسديد' in val: return "Shot"
        if 'pass' in val and x >= 80: return "Final Third Entry"
        if 'dribble' in val and (102 <= x <= 120): return "Box Entry"
        
        zone = get_tactical_zone(x, y)
        if zone != "Other": return zone
        return "Other"

    df['Type'] = df.apply(classify, axis=1)

    # الفلترة
    selected_actions = st.sidebar.multiselect("Select Tactical Actions:", options=df['Type'].unique().tolist(), default=df['Type'].unique().tolist())
    filtered_df = df[df['Type'].isin(selected_actions)]

    # الرسم
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Tactical Actions Map")
        fig1, ax1 = plt.subplots(figsize=(10, 7))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax1)
        fig1.patch.set_facecolor('#1a1a1a')
        
        for _, row in filtered_df.iterrows():
            # ألوان مميزة لكل منطقة
            color = '#32CD32' if row['Type'] == "Penalty Box" else '#FFD700' if row['Type'] == "Zone 14" else '#ffffff'
            pitch.scatter(row['x_scaled'], row['y_scaled'], color=color, s=150, ax=ax1, label=row['Type'])
            
        st.pyplot(fig1)

    with col2:
        st.subheader("🔥 Zone Heatmap")
        fig2, ax2 = plt.subplots(figsize=(10, 7))
        pitch.draw(ax=ax2)
        fig2.patch.set_facecolor('#1a1a1a')
        if not filtered_df.empty:
            pitch.kdeplot(filtered_df['x_scaled'], filtered_df['y_scaled'], ax=ax2, fill=True, levels=100, cmap='inferno', alpha=0.6)
        st.pyplot(fig2)
