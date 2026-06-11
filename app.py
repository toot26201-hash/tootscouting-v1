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
        
    st.sidebar.success("File Loaded Successfully!")
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    column_mapping = {'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'}
    df = df.rename(columns=column_mapping)
    
    required_columns = ['x1', 'y1', 'x2', 'y2']
    if all(col in df.columns for col in required_columns):
        
        # Scaling coordinates
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
        # 3. Tactical Classification Engine (Refined for your Data)
        # -------------------------------------------------------------
        tactical_conditions = []
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Goal|هدف', case=False) | valid_df['Tags'].str.contains('goal', case=False))
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Shot|تسديد|شوط', case=False))
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Corner|كورنر|ركنية', case=False) | valid_df['Tags'].str.contains('corner', case=False))
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Cross|عرضية', case=False) | valid_df['Tags'].str.contains('cross', case=False))
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Dribble|مرواغة|مراوغة|دريبليج', case=False) | valid_df['Tags'].str.contains('dribble', case=False))
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Through|Key|ثرو', case=False) | valid_df['Tags'].str.contains('through|key|Behind', case=False))
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Tackle|تدخل|افتكاك', case=False) | valid_df['Tags'].str.contains('tackle', case=False))
        # Support for 'extraction'
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Clearance|تشتيت|extraction', case=False) | valid_df['Tags'].str.contains('clearance|extraction', case=False))
        # Support for 'Aerial'
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Air|هوائي|هواء|Aerial', case=False) | valid_df['Tags'].str.contains('aerial|air', case=False))
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Ground|أرضي|ارضي', case=False) | valid_df['Tags'].str.contains('ground', case=False))
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Foul|فاول|خطأ|خطا', case=False) | valid_df['Tags'].str.contains('foul', case=False))
        # Support for 'counter pressing'
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Counter|ضغط عكسي|عكسي|counter pressing', case=False) | valid_df['Tags'].str.contains('counterpress|press|counter pressing', case=False))
        tactical_conditions.append((valid_df['Action_raw'].str.contains('Pass|تمرير', case=False) | valid_df['Action_raw'].str.isnumeric()) & (valid_df['prog_distance'] >= 12))
        tactical_conditions.append(valid_df['Action_raw'].str.contains('Pass|تمرير', case=False) | valid_df['Action_raw'].str.isnumeric())
        
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
            filtered_df = temp_df[temp_df['Clean_Action'].
