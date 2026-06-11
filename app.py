import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. Pitch Setup
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
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    if all(col in df.columns for col in ['x1', 'y1', 'x2', 'y2']):
        df['x_scaled'] = df['x1'] * 120
        df['y_scaled'] = df['y1'] * 80
        df['x2_scaled'] = df['x2'] * 120
        df['y2_scaled'] = df['y2'] * 80
        
        valid_df = df.copy()
        valid_df['Action_raw'] = valid_df['Action'].astype(str).str.strip()
        valid_df['Tags'] = valid_df['Tags'].fillna('').astype(str)
        
        # 3. Tactical Classification
        tactical_conditions = [
            valid_df['Action_raw'].str.contains('Goal', case=False),
            valid_df['Action_raw'].str.contains('Shot', case=False),
            valid_df['Action_raw'].str.contains('Tackle', case=False),
            valid_df['Action_raw'].str.contains('Clearance', case=False),
            valid_df['Action_raw'].str.contains('Aerial|Air', case=False),
            valid_df['Action_raw'].str.contains('Pass', case=False)
        ]
        tactical_choices = ["⚽ Goal", "👟 Shot", "🛡️ Tackle", "💥 Clearance", "🪂 Aerial Duel", "🔄 Pass"]
        valid_df['Clean_Action'] = np.select(tactical_conditions, tactical_choices, default="📋 Other")

        # 4. Filters
        players_list = ["All Players"] + list(valid_df['Player'].dropna().unique())
        selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players_list)
        temp_df = valid_df if selected_player == "All Players" else valid_df[valid_df['Player'] == selected_player]
        
        st.sidebar.markdown("### 🏹 ACTIONS")
        # تم إظهار كل الاختيارات دائماً
        selected_actions = st.sidebar.multiselect("Select Actions:", options=tactical_choices, default=tactical_choices)
        filtered_df = temp_df[temp_df['Clean_Action'].isin(selected_actions)]

        # 5. Visualization
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        legend_elements = []
        
        # رسم التمريرات كأسهم
        passes = filtered_df[filtered_df['Clean_Action'] == "🔄 Pass"]
        if not passes.empty:
            pitch.arrows(passes['x_scaled'], passes['y_scaled'], passes['x2_scaled'], passes['y2_scaled'], color='#00ffcc', width=2, headwidth=4, headlength=4, ax=ax)
            legend_elements.append(Line2D([0], [0], color='#00ffcc', lw=2, label="Pass"))
            
        # رسم باقي الأكشن كنقط
        markers = {"⚽ Goal": "*", "👟 Shot": "o", "🛡️ Tackle": "X", "💥 Clearance": "s", "🪂 Aerial Duel": "^"}
        colors = {"⚽ Goal": "#00ff00", "👟 Shot": "#ff3366", "🛡️ Tackle": "#ff00ff", "💥 Clearance": "#ffffff", "🪂 Aerial Duel": "#3399ff"}
        
        for act in tactical_choices:
            if act == "🔄 Pass": continue
            subset = filtered_df[filtered_df['Clean_Action'] == act]
            if not subset.empty:
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color=colors[act], marker=markers[act], s=150, ax=ax)
                legend_elements.append(Line2D([0], [0], marker=markers[act], color='none', markerfacecolor=colors[act], label=act, markersize=10))

        # Legend
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5, facecolor='#222222', labelcolor='white')
        
        plot_placeholder.pyplot(fig)
        plt.close(fig)
