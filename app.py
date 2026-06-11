import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. Draw the pitch immediately on load
st.subheader("🏟️ Tactical Activity Map")

fig, ax = plt.subplots(figsize=(12, 8))
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
pitch.draw(ax=ax)
fig.patch.set_facecolor('#1a1a1a')

plot_placeholder = st.empty()
plot_placeholder.pyplot(fig)
plt.close(fig)

# 2. Sidebar for File Upload and Filters
st.sidebar.header("📁 DATA LOAD & ANALYSIS")
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel or CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    st.sidebar.success("Success is successfully.")
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    column_mapping = {'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'}
    df = df.rename(columns=column_mapping)
    
    required_columns = ['x1', 'y1', 'x2', 'y2']
    if all(col in df.columns for col in required_columns):
        
        # Scaling coordinates to StatsBomb dimensions (120x80)
        df['x_scaled'] = df['x1'] * 120
        df['y_scaled'] = df['y1'] * 80
        df['x2_scaled'] = df['x2'] * 120
        df['y2_scaled'] = df['y2'] * 80
        
        valid_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()].copy()
        valid_df['Action_raw'] = valid_df['Action'].astype(str).str.strip()
        valid_df['Tags'] = valid_df['Tags'].fillna('').astype(str)
        valid_df['Player'] = valid_df['Player'].astype(str).str.strip()
        valid_df['prog_distance'] = valid_df['x2_scaled'] - valid_df['x_scaled']

        # -------------------------------------------------------------
        # 3. Tactical Classification Engine (ONE-LINE SAFE METHOD)
        # -------------------------------------------------------------
        c1 = valid_df['Action_raw'].str.contains('Goal|هدف', case=False) | valid_df['Tags'].str.contains('goal', case=False)
        c2 = valid_df['Action_raw'].str.contains('Shot|تسديد|شوط', case=False)
        c3 = valid_df['Action_raw'].str.contains('Corner|كورنر|ركنية', case=False) | valid_df['Tags'].str.contains('corner', case=False)
        c4 = valid_df['Action_raw'].str.contains('Cross|عرضية', case=False) | valid_df['Tags'].str.contains('cross', case=False)
        c5 = valid_df['Action_raw'].str.contains('Dribble|مرواغة|مراوغة|دريبليج', case=False) | valid_df['Tags'].str.contains('dribble', case=False)
        c6 = valid_df['Action_raw'].str.contains('Through|Key|ثرو', case=False) | valid_df['Tags'].str.contains('through|key|Behind', case=False)
        c7 = valid_df['Action_raw'].str.contains('Tackle|تدخل|افتكاك', case=False) | valid_df['Tags'].str.contains('tackle', case=False)
        c8 = valid_df['Action_raw'].str.contains('Clearance|تشتيت', case=False) | valid_df['Tags'].str.contains('clearance', case=False)
        c9 = valid_df['Action_raw'].str.contains('Air|هوائي|هواء', case=False) | valid_df['Tags'].str.contains('aerial|air', case=False)
        c10 = valid_df['Action_raw'].str.contains('Ground|أرضي|ارضي', case=False) | valid_df['Tags'].str.contains('ground', case=False)
        c11 = valid_df['Action_raw'].str.contains('Foul|فاول|خطأ|خطا', case=False) | valid_df['Tags'].str.contains('foul', case=False)
        c12 = valid_df['Action_raw'].str.contains('Counter|ضغط عكسي|عكسي', case=False) | valid_df['Tags'].str.contains('counterpress|press', case=False)
        c13 = (valid_df['Action_raw'].str.contains('Pass|تمرير', case=False) | valid_df['Action_raw'].str.isnumeric()) & (valid_df['prog_distance'] >= 12)
        c14 = valid_df['Action_raw'].str.contains('Pass|تمرير', case=False) | valid_df['Action_raw'].str.isnumeric()

        tactical_conditions = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14]
        
        tactical_choices = ["⚽ Goal", "👟 Shot", "🚩 Corner", "📐 Cross", "✨ Dribble", "⚡ Through Ball", "🛡️ Tackle", "💥 Clearance", "🪂 Aerial Duel", "🪵 Ground Duel", "⚠️ Foul", "⏱️ Counterpress", "🚀 Progressive Pass", "🔄 Normal Pass"]
        
        valid_df['Clean_Action'] = np.select(tactical_conditions, tactical_choices, default="📋 Other Action")

        # -------------------------------------------------------------
        # 4. Sidebar Filters
        # -------------------------------------------------------------
        st.sidebar.markdown("---")
        players_list = ["All Players"] + list(valid_df['Player'].dropna().unique())
        selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players_list)
            
        temp_df = valid_df.copy()
        if selected_player != "All Players":
            temp_df = temp_df[temp_df['Player'] == selected_player]

        attack_categories = ["⚽ Goal", "👟 Shot", "🚩 Corner", "📐 Cross", "✨ Dribble", "⚡ Through Ball", "🚀 Progressive Pass", "🔄 Normal Pass"]
        defense_categories = ["🛡️ Tackle", "💥 Clearance", "🪂 Aerial Duel", "🪵 Ground Duel", "⚠️ Foul", "⏱️ Counterpress"]

        available_attack = [act for act in attack_categories if act in temp_df['Clean_Action'].unique()]
        available_defense = [act for act in defense_categories if act in temp_df['Clean_Action'].unique()]

        st.sidebar.markdown("### 🏹 OFFENSIVE ACTIONS")
        selected_attack = st.sidebar.multiselect("Select Offensive Actions:", options=available_attack, default=available_attack)

        st.sidebar.markdown("### 🧱 DEFENSIVE ACTIONS")
        selected_defense = st.sidebar.multiselect("Select Defensive Actions:", options=available_defense, default=available_defense)

        final_selected_actions = selected_attack + selected_defense

        if final_selected_actions:
            filtered_df = temp_df[temp_df['Clean_Action'].isin(final_selected_actions)]
        else:
            filtered_df = pd.DataFrame(columns=temp_df.columns)

        # -------------------------------------------------------------
        # 5. Redraw Pitch with Centered Elegant Player Name & Legend
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        legend_elements = []
        drawn_arrow_names = set()
        
        player_display_name = selected_player if selected_player != "All Players" else "All Players"
        ax.text(60, 40, player_display_name, color='#D4AF37', fontsize=45, fontweight='normal', fontstyle='italic', ha='center', va='center', alpha=0.18, zorder=1)

        if not filtered_df.empty:
            movement_labels = ["🔄 Normal Pass", "🚀 Progressive Pass", "⚡ Through Ball", "📐 Cross", "🚩 Corner"]
            
            arrows_df = filtered_df[filtered_df['Clean_Action'].isin(movement_labels)]
            dots_df = filtered_df[~filtered_df['Clean_Action'].isin(movement_labels)]
            
            if not arrows_df.empty:
                for act in arrows_df['Clean_Action'].unique():
                    sub_arrow = arrows_df[arrows_df['Clean_Action'] == act]
                    if "Normal" in act: color, name = '#00ffcc', "Normal Pass"
                    elif "Progressive" in act: color, name = '#ff9900', "Prog. Pass"
                    elif "Through" in act: color, name = '#cc00ff', "Through Ball"
                    elif "Cross" in act: color, name = '#ffff00', "Cross"
                    else: color, name = '#00f0ff', "Corner"
                    
                    has_end = sub_arrow['x2_scaled'].notna() & (sub_arrow['x2_scaled'] != 0) & (sub_arrow['x2_scaled'] != sub_arrow['x_scaled'])
                    arrow_plots = sub_arrow[has_end]
                    dot_plots = sub_arrow[~has_end]
                    
                    if not arrow_plots.empty:
                        pitch.arrows(arrow_plots['x_scaled'], arrow_plots['y_scaled'], arrow_plots['x2_scaled'], arrow_plots['y2_scaled'], width=2, headwidth=3, headlength=3, color=color, alpha=0.8, zorder=3, ax=ax)
                        pitch.scatter(arrow_plots['x_scaled'], arrow_plots['y_scaled'], color=color, s=40, edgecolors='#ffffff', zorder=3, ax=ax)
                    if not dot_plots.empty:
