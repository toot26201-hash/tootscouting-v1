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
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    if all(col in df.columns for col in ['x1', 'y1', 'x2', 'y2']):
        df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80
        df['x2_scaled'], df['y2_scaled'] = df['x2'] * 120, df['y2'] * 80
        
        # 3. Tactical Classification (شامل لكل الاكشن الدفاعي)
        conds = [
            df['Action'].str.contains('Pass|تمرير', case=False),
            df['Action'].str.contains('Tackle|تدخل', case=False),
            df['Action'].str.contains('Clearance|تشتيت', case=False),
            df['Action'].str.contains('Aerial|Air|هوائي', case=False),
            df['Action'].str.contains('Ground|أرضي', case=False),
            df['Action'].str.contains('Foul|خطأ', case=False),
            df['Action'].str.contains('Counter|ضغط', case=False)
        ]
        choices = ["Pass", "Tackle", "Clearance", "Aerial Duel", "Ground Duel", "Foul", "Counterpress"]
        df['Type'] = np.select(conds, choices, default="Other")

        # 4. Filters
        st.sidebar.markdown("---")
        players = ["All Players"] + list(df['Player'].dropna().unique())
        selected_player = st.sidebar.selectbox("👤 PLAYER:", players)
        temp_df = df if selected_player == "All Players" else df[df['Player'] == selected_player]
        
        # اختيار الاكشن
        all_actions = ["Pass", "Tackle", "Clearance", "Aerial Duel", "Ground Duel", "Foul", "Counterpress"]
        selected_actions = st.sidebar.multiselect("Select Actions:", options=all_actions, default=all_actions)
        filtered_df = temp_df[temp_df['Type'].isin(selected_actions)]

        # 5. Drawing
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        # إعدادات الألوان والرموز لكل الأكشن
        configs = {
            "Pass": {"color": "#00ffcc", "marker": None, "is_arrow": True},
            "Tackle": {"color": "#ff00ff", "marker": "X"},
            "Clearance": {"color": "#ffffff", "marker": "s"},
            "Aerial Duel": {"color": "#3399ff", "marker": "^"},
            "Ground Duel": {"color": "#8B4513", "marker": "v"},
            "Foul": {"color": "#ffcc00", "marker": "d"},
            "Counterpress": {"color": "#ff3300", "marker": "h"}
        }

        legend_elements = []
        for act in selected_actions:
            cfg = configs[act]
            subset = filtered_df[filtered_df['Type'] == act]
            if subset.empty: continue
            
            if cfg.get("is_arrow"):
                pitch.arrows(subset['x_scaled'], subset['y_scaled'], subset['x2_scaled'], subset['y2_scaled'], color=cfg['color'], width=2, ax=ax)
                legend_elements.append(Line2D([0], [0], color=cfg['color'], lw=2, label=act))
            else:
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color=cfg['color'], marker=cfg['marker'], s=150, ax=ax)
                legend_elements.append(Line2D([0], [0], marker=cfg['marker'], color='none', markerfacecolor=cfg['color'], label=act, markersize=10))

        # الدليل
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, facecolor='#222222', labelcolor='white')
        plot_placeholder.pyplot(fig)
        plt.close(fig)
