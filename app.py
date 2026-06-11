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
        valid_df['Tags'] = valid_df['Tags'].fillna('').astype(str)
        valid_df['Player'] = valid_df['Player'].astype(str).str.strip()
        valid_df['prog_dist'] = valid_df['x2_scaled'] - valid_df['x_scaled']

        # 3. Classification
        conds = [
            valid_df['Action_raw'].str.contains('Goal|هدف', case=False) | valid_df['Tags'].str.contains('goal', case=False),
            valid_df['Action_raw'].str.contains('Shot|تسديد|شوط', case=False),
            valid_df['Action_raw'].str.contains('Corner|كورنر|ركنية', case=False) | valid_df['Tags'].str.contains('corner', case=False),
            valid_df['Action_raw'].str.contains('Cross|عرضية', case=False) | valid_df['Tags'].str.contains('cross', case=False),
            valid_df['Action_raw'].str.contains('Dribble|مرواغة|مراوغة|دريبليج', case=False) | valid_df['Tags'].str.contains('dribble', case=False),
            valid_df['Action_raw'].str.contains('Through|Key|ثرو', case=False) | valid_df['Tags'].str.contains('through|key|Behind', case=False),
            valid_df['Action_raw'].str.contains('Tackle|تدخل|افتكاك', case=False) | valid_df['Tags'].str.contains('tackle', case=False),
            valid_df['Action_raw'].str.contains('Clearance|تشتيت|extraction', case=False) | valid_df['Tags'].str.contains('clearance|extraction', case=False),
            valid_df['Action_raw'].str.contains('Air|هوائي|هواء|Aerial', case=False) | valid_df['Tags'].str.contains('aerial|air', case=False),
            valid_df['Action_raw'].str.contains('Ground|أرضي|ارضي', case=False) | valid_df['Tags'].str.contains('ground', case=False),
            valid_df['Action_raw'].str.contains('Foul|فاول|خطأ|خطا', case=False) | valid_df['Tags'].str.contains('foul', case=False),
            valid_df['Action_raw'].str.contains('Counter|ضغط عكسي|عكسي|counter pressing', case=False) | valid_df['Tags'].str.contains('counterpress|press|counter pressing', case=False),
            (valid_df['Action_raw'].str.contains('Pass|تمرير', case=False)) & (valid_df['prog_dist'] >= 12),
            valid_df['Action_raw'].str.contains('Pass|تمرير', case=False)
        ]
        choices = ["⚽ Goal", "👟 Shot", "🚩 Corner", "📐 Cross", "✨ Dribble", "⚡ Through Ball", "🛡️ Tackle", "💥 Clearance", "🪂 Aerial Duel", "🪵 Ground Duel", "⚠️ Foul", "⏱️ Counterpress", "🚀 Progressive Pass", "🔄 Normal Pass"]
        valid_df['Clean_Action'] = np.select(conds, choices, default="📋 Other Action")

        # 4. Filter
        players = ["All Players"] + list(valid_df['Player'].unique())
        sel_player = st.sidebar.selectbox("👤 PLAYER:", players)
        temp_df = valid_df if sel_player == "All Players" else valid_df[valid_df['Player'] == sel_player]
        
        att_cats = ["⚽ Goal", "👟 Shot", "🚩 Corner", "📐 Cross", "✨ Dribble", "⚡ Through Ball", "🚀 Progressive Pass", "🔄 Normal Pass"]
        def_cats = ["🛡️ Tackle", "💥 Clearance", "🪂 Aerial Duel", "🪵 Ground Duel", "⚠️ Foul", "⏱️ Counterpress"]
        
        sel_att = st.sidebar.multiselect("Offensive:", options=att_cats, default=att_cats)
        sel_def = st.sidebar.multiselect("Defensive:", options=def_cats, default=def_cats)
        
        final_acts = sel_att + sel_def
        filtered_df = temp_df[temp_df['Clean_Action'].isin(final_acts)]

        # 5. Visualization
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                # Simple plotting logic
                color = '#00ffcc' if "Pass" in row['Clean_Action'] else '#ff3366'
                pitch.scatter(row['x_scaled'], row['y_scaled'], color=color, s=100, ax=ax)
            plot_placeholder.pyplot(fig)
            st.success(f"Analyzed {len(filtered_df)} actions.")
        else:
            st.warning("No actions match filters.")
        plt.close(fig)
