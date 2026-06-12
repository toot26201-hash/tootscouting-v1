import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. إعداد الملعب (تأكد أن هذه الأسطر لا يوجد قبلها أي مسافات)
fig, ax = plt.subplots(figsize=(12, 8))
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
pitch.draw(ax=ax)
fig.patch.set_facecolor('#1a1a1a')
plot_placeholder = st.empty()
plot_placeholder.pyplot(fig)
plt.close(fig)

# 2. Sidebar
st.sidebar.header("📁 DATA LOAD & ANALYSIS")
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    if all(col in df.columns for col in ['x1', 'y1', 'x2', 'y2']):
        df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80
        df['x2_scaled'], df['y2_scaled'] = df['x2'] * 120, df['y2'] * 80
        
        # 3. الفلترة
        players_list = ["All Players"] + sorted(df['Player'].dropna().unique().tolist())
        selected_player = st.sidebar.selectbox("👤 PLAYER:", players_list)
        
        # الحصول على كل الأكشنات الفريدة من ملفك
        all_actions = sorted(df['Action'].dropna().unique().tolist())
        selected_actions = st.sidebar.multiselect("Select Actions:", options=all_actions, default=all_actions)
        
        temp_df = df if selected_player == "All Players" else df[df['Player'] == selected_player]
        filtered_df = temp_df[temp_df['Action'].isin(selected_actions)]

        # 4. الرسم
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        # اسم اللاعب كعلامة مائية
        ax.text(60, 40, selected_player, color='#D4AF37', fontsize=60, fontweight='bold', 
                ha='center', va='center', alpha=0.15, zorder=1)

        # 5. حلقة الرسم الديناميكية
        for act in selected_actions:
            subset = filtered_df[filtered_df['Action'] == act]
            if subset.empty: continue
            
            # تحديد الشكل واللون تلقائياً
            act_lower = act.lower()
            if 'pass' in act_lower:
                pitch.arrows(subset['x_scaled'], subset['y_scaled'], subset['x2_scaled'], subset['y2_scaled'], color='#00ffcc', width=2, ax=ax)
            elif 'shot' in act_lower:
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color='#00ff00', marker='*', s=150, ax=ax)
            elif 'interception' in act_lower or 'قطع' in act_lower:
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color='#FFFF00', marker='P', s=150, ax=ax)
            else:
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color='#ff9900', marker='o', s=100, ax=ax)

        plot_placeholder.pyplot(fig)
        plt.close(fig)
