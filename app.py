import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. Pitch Setup
fig, ax = plt.subplots(figsize=(12, 8))
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
pitch.draw(ax=ax)
fig.patch.set_facecolor('#1a1a1a')
plot_placeholder = st.empty()

# 2. Sidebar
st.sidebar.header("📁 DATA LOAD & ANALYSIS")
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel or CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    if all(col in df.columns for col in ['x1', 'y1', 'x2', 'y2']):
        df['x1'], df['y1'] = df['x1'] * 120, df['y1'] * 80
        df['x2'], df['y2'] = df['x2'] * 120, df['y2'] * 80
        valid_df = df.dropna(subset=['x1', 'y1']).copy()
        valid_df['Action_raw'] = valid_df['Action'].astype(str).str.strip()
        
        # 3. Classification
        conds = [
            valid_df['Action_raw'].str.contains('Pass|تمرير', case=False),
            valid_df['Action_raw'].str.contains('Aerial|Air|هوائي', case=False),
            valid_df['Action_raw'].str.contains('Tackle|تدخل', case=False),
            valid_df['Action_raw'].str.contains('Goal|Shot|تسديد', case=False),
            valid_df['Action_raw'].str.contains('Clearance|تشتيت', case=False)
        ]
        choices = ["Pass", "Aerial Duel", "Tackle", "Goal/Shot", "Clearance"]
        valid_df['Type'] = np.select(conds, choices, default="Other")

        # 4. Filters
        players = ["All Players"] + list(valid_df['Player'].unique())
        selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players)
        temp_df = valid_df if selected_player == "All Players" else valid_df[valid_df['Player'] == selected_player]
        
        # 5. Visualization
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        # رسم التمريرات (أسهم)
        passes = temp_df[temp_df['Type'] == "Pass"]
        if not passes.empty:
            pitch.arrows(passes['x1'], passes['y1'], passes['x2'], passes['y2'], color='#00ffcc', width=2, ax=ax, label="Pass")
        
        # رسم باقي الأكشن (نقط)
        colors = {"Aerial Duel": "#3399ff", "Tackle": "#ff00ff", "Goal/Shot": "#00ff00", "Clearance": "#ffffff"}
        markers = {"Aerial Duel": "^", "Tackle": "X", "Goal/Shot": "*", "Clearance": "s"}
        
        for t in ["Aerial Duel", "Tackle", "Goal/Shot", "Clearance"]:
            subset = temp_df[temp_df['Type'] == t]
            if not subset.empty:
                pitch.scatter(subset['x1'], subset['y1'], color=colors[t], marker=markers[t], s=150, ax=ax, label=t)

        # الدليل (Legend) - هنا الجزء اللي بيظهر لك كل الرموز
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5, 
                  facecolor='#222222', labelcolor='white', fontsize=12, frameon=True)
        
        plot_placeholder.pyplot(fig)
        plt.close(fig)
