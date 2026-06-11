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

        # 3. Tactical Classification Engine
        tactical_conditions = [
            valid_df['Action_raw'].str.contains('Goal|هدف', case=False) | valid_df['Tags'].str.contains('goal', case=False),
            valid_df['Action_raw'].str.contains('Shot|تسديد|شوط', case=False),
            valid_df['Action_raw'].str.contains('Corner|كورنر|ركنية', case=False) | valid_df['Tags'].str.contains('corner', case=False),
            valid_df['Action_raw'].str.contains('Cross|عرضية', case=False) | valid_df['Tags'].str.contains('cross', case=False),
            valid_df['Action_raw'].str.contains('Dribble|مراوغة', case=False) | valid_df['Tags'].str.contains('dribble', case=False),
            valid_df['Action_raw'].str.contains('Through|ثرو', case=False) | valid_df['Tags'].str.contains('through', case=False),
            valid_df['Action_raw'].str.contains('Tackle|تدخل', case=False) | valid_df['Tags'].str.contains('tackle', case=False),
            valid_df['Action_raw'].str.contains('Clearance|تشتيت', case=False) | valid_df['Tags'].str.contains('clearance', case=False),
            valid_df['Action_raw'].str.contains('Aerial|Air|هوائي', case=False) | valid_df['Tags'].str.contains('aerial|air', case=False),
            valid_df['Action_raw'].str.contains('Ground|أرضي', case=False) | valid_df['Tags'].str.contains('ground', case=False),
            valid_df['Action_raw'].str.contains('Foul|فاول|خطأ', case=False) | valid_df['Tags'].str.contains('foul', case=False),
            valid_df['Action_raw'].str.contains('Counter|ضغط', case=False) | valid_df['Tags'].str.contains('counterpress', case=False),
            (valid_df['Action_raw'].str.contains('Pass|تمرير', case=False)) & (valid_df['prog_distance'] >= 12),
            valid_df['Action_raw'].str.contains('Pass|تمرير', case=False)
        ]
        
        tactical_choices = ["⚽ Goal", "👟 Shot", "🚩 Corner", "📐 Cross", "✨ Dribble", "⚡ Through Ball", "🛡️ Tackle", "💥 Clearance", "🪂 Aerial Duel", "🪵 Ground Duel", "⚠️ Foul", "⏱️ Counterpress", "🚀 Progressive Pass", "🔄 Normal Pass"]
        valid_df['Clean_Action'] = np.select(tactical_conditions, tactical_choices, default="📋 Other Action")

        # 4. Sidebar Filters
        st.sidebar.markdown("---")
        players_list = ["All Players"] + list(valid_df['Player'].dropna().unique())
        selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players_list)
            
        temp_df = valid_df.copy()
        if selected_player != "All Players":
            temp_df = temp_df[temp_df['Player'] == selected_player]

        # Categories for MultiSelect
        attack_categories = ["⚽ Goal", "👟 Shot", "🚩 Corner", "📐 Cross", "✨ Dribble", "⚡ Through Ball", "🚀 Progressive Pass", "🔄 Normal Pass"]
        defense_categories = ["🛡️ Tackle", "💥 Clearance", "🪂 Aerial Duel", "🪵 Ground Duel", "⚠️ Foul", "⏱️ Counterpress"]

        st.sidebar.markdown("### 🏹 OFFENSIVE ACTIONS")
        selected_attack = st.sidebar.multiselect("Select:", options=attack_categories, default=attack_categories)

        st.sidebar.markdown("### 🧱 DEFENSIVE ACTIONS")
        selected_defense = st.sidebar.multiselect("Select:", options=defense_categories, default=defense_categories)

        final_selected_actions = selected_attack + selected_defense
        filtered_df = temp_df[temp_df['Clean_Action'].isin(final_selected_actions)]

        # 5. Drawing
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        legend_elements = []
        
        # Plotting
        if not filtered_df.empty:
            # Arrows (Passes)
            movement_labels = ["🔄 Normal Pass", "🚀 Progressive Pass", "⚡ Through Ball", "📐 Cross", "🚩 Corner"]
            arrows_df = filtered_df[filtered_df['Clean_Action'].isin(movement_labels)]
            dots_df = filtered_df[~filtered_df['Clean_Action'].isin(movement_labels)]
            
            # ... [بقية منطق الرسم كما هو، تأكد فقط من إضافة Aerial Duel في Dots]
            for act in dots_df['Clean_Action'].unique():
                sub = dots_df[dots_df['Clean_Action'] == act]
                if "Aerial" in act:
                    pitch.scatter(sub['x_scaled'], sub['y_scaled'], color='#3399ff', marker='^', s=130, ax=ax, label=act)
                else:
                    pitch.scatter(sub['x_scaled'], sub['y_scaled'], s=120, ax=ax, label=act)
            
        plot_placeholder.pyplot(fig)
        plt.close(fig)
