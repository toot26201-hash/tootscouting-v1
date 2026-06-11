import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. Draw the pitch
st.subheader("🏟️ Tactical Activity Map")
fig, ax = plt.subplots(figsize=(12, 8))
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
pitch.draw(ax=ax)
fig.patch.set_facecolor('#1a1a1a')
plot_placeholder = st.empty()
plot_placeholder.pyplot(fig)
plt.close(fig)

# 2. Sidebar
st.sidebar.header("📁 DATA LOAD & ANALYSIS")
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel or CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    
    col_map = {'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'}
    df = df.rename(columns=col_map)
    
    if all(col in df.columns for col in ['x1', 'y1', 'x2', 'y2']):
        df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80
        df['x2_scaled'], df['y2_scaled'] = df['x2'] * 120, df['y2'] * 80
        
        valid_df = df.dropna(subset=['x_scaled', 'y_scaled']).copy()
        valid_df['Action_raw'] = valid_df['Action'].astype(str).str.strip()
        
        # 3. Enhanced Classification Engine
        # هنا ضفت البحث عن "Aerial" بوضوح
        conds = [
            valid_df['Action_raw'].str.contains('Goal|هدف', case=False),
            valid_df['Action_raw'].str.contains('Shot|تسديد', case=False),
            valid_df['Action_raw'].str.contains('Aerial', case=False), # هذا هو السطر المسؤول عن الالتحام الهوائي
            valid_df['Action_raw'].str.contains('Tackle', case=False),
            valid_df['Action_raw'].str.contains('Pass', case=False)
        ]
        choices = ["Goal", "Shot", "Aerial Duel", "Tackle", "Pass"]
        valid_df['Clean_Action'] = np.select(conds, choices, default="Other")

        # 4. Filter
        players = ["All Players"] + list(valid_df['Player'].unique())
        sel_player = st.sidebar.selectbox("👤 PLAYER:", players)
        temp_df = valid_df if sel_player == "All Players" else valid_df[valid_df['Player'] == sel_player]
        
        all_acts = ["Goal", "Shot", "Aerial Duel", "Tackle", "Pass"]
        selected_acts = st.sidebar.multiselect("Actions:", options=all_acts, default=all_acts)
        filtered_df = temp_df[temp_df['Clean_Action'].isin(selected_acts)]

        # 5. Visualization with Legend
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        colors = {"Goal": "#00ff00", "Shot": "#ff3366", "Aerial Duel": "#3399ff", "Tackle": "#ff00ff", "Pass": "#00ffcc"}
        markers = {"Goal": "*", "Shot": "o", "Aerial Duel": "^", "Tackle": "X", "Pass": "h"}
        
        legend_elements = []
        for action in selected_acts:
            subset = filtered_df[filtered_df['Clean_Action'] == action]
            if not subset.empty:
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color=colors[action], 
                              marker=markers[action], s=150, ax=ax, label=action)
                legend_elements.append(Line2D([0], [0], marker=markers[action], color='none', 
                                            markerfacecolor=colors[action], label=action, markersize=12))

        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), 
                      ncol=5, facecolor='#222222', labelcolor='white')
            
        plot_placeholder.pyplot(fig)
        st.success(f"Showing {len(filtered_df)} actions.")
        plt.close(fig)
