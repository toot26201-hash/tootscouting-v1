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
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    if all(col in df.columns for col in ['x1', 'y1', 'x2', 'y2']):
        df['x_scaled'] = df['x1'] * 120
        df['y_scaled'] = df['y1'] * 80
        df['x2_scaled'] = df['x2'] * 120
        df['y2_scaled'] = df['y2'] * 80
        
        valid_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()].copy()
        valid_df['Action_raw'] = valid_df['Action'].astype(str).str.strip()
        valid_df['Tags'] = valid_df['Tags'].fillna('').astype(str)
        
        # 3. Tactical Classification Engine (تم تحديث شروط التصنيف)
        tactical_conditions = [
            valid_df['Action_raw'].str.contains('Goal|هدف', case=False) | valid_df['Tags'].str.contains('goal', case=False),
            valid_df['Action_raw'].str.contains('Shot|تسديد', case=False),
            valid_df['Action_raw'].str.contains('Corner|ركنية', case=False),
            valid_df['Action_raw'].str.contains('Cross|عرضية', case=False),
            valid_df['Action_raw'].str.contains('Dribble|مراوغة', case=False),
            valid_df['Action_raw'].str.contains('Through|Key', case=False),
            valid_df['Action_raw'].str.contains('Tackle|تدخل', case=False),
            valid_df['Action_raw'].str.contains('Clearance|تشتيت', case=False),
            # تم إضافة الالتحام الهوائي هنا ليدخل في التصنيف الدفاعي
            valid_df['Action_raw'].str.contains('Aerial|Air|هوائي', case=False) | valid_df['Tags'].str.contains('aerial|air', case=False),
            valid_df['Action_raw'].str.contains('Ground|أرضي', case=False),
            valid_df['Action_raw'].str.contains('Foul|خطأ', case=False),
            valid_df['Action_raw'].str.contains('Counter|ضغط', case=False),
            (valid_df['Action_raw'].str.contains('Pass|تمرير', case=False)) & ((valid_df['x2_scaled'] - valid_df['x_scaled']) >= 12),
            valid_df['Action_raw'].str.contains('Pass|تمرير', case=False)
        ]
        tactical_choices = ["⚽ Goal", "👟 Shot", "🚩 Corner", "📐 Cross", "✨ Dribble", "⚡ Through Ball", "🛡️ Tackle", "💥 Clearance", "🪂 Aerial Duel", "🪵 Ground Duel", "⚠️ Foul", "⏱️ Counterpress", "🚀 Progressive Pass", "🔄 Normal Pass"]
        valid_df['Clean_Action'] = np.select(tactical_conditions, tactical_choices, default="📋 Other")

        # 4. Filters
        players_list = ["All Players"] + list(valid_df['Player'].dropna().unique())
        selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players_list)
        temp_df = valid_df if selected_player == "All Players" else valid_df[valid_df['Player'] == selected_player]

        defense_categories = ["🛡️ Tackle", "💥 Clearance", "🪂 Aerial Duel", "🪵 Ground Duel", "⚠️ Foul", "⏱️ Counterpress"]
        attack_categories = ["⚽ Goal", "👟 Shot", "🚩 Corner", "📐 Cross", "✨ Dribble", "⚡ Through Ball", "🚀 Progressive Pass", "🔄 Normal Pass"]
        
        st.sidebar.markdown("### 🧱 DEFENSIVE ACTIONS")
        selected_defense = st.sidebar.multiselect("Select:", options=defense_categories, default=defense_categories)
        st.sidebar.markdown("### 🏹 OFFENSIVE ACTIONS")
        selected_attack = st.sidebar.multiselect("Select:", options=attack_categories, default=attack_categories)

        filtered_df = temp_df[temp_df['Clean_Action'].isin(selected_defense + selected_attack)]

        # 5. Drawing
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        
        # رسم الأسهم للتمريرات والنقط لباقي الأكشن كما طلبت
        movement_labels = ["🔄 Normal Pass", "🚀 Progressive Pass", "⚡ Through Ball", "📐 Cross", "🚩 Corner"]
        arrows_df = filtered_df[filtered_df['Clean_Action'].isin(movement_labels)]
        dots_df = filtered_df[~filtered_df['Clean_Action'].isin(movement_labels)]

        # رسم الأسهم
        for act in arrows_df['Clean_Action'].unique():
            sub = arrows_df[arrows_df['Clean_Action'] == act]
            pitch.arrows(sub['x_scaled'], sub['y_scaled'], sub['x2_scaled'], sub['y2_scaled'], color='#00ffcc', ax=ax)
        
        # رسم النقط (بما فيها Aerial Duel)
        for act in dots_df['Clean_Action'].unique():
            sub = dots_df[dots_df['Clean_Action'] == act]
            marker = '^' if 'Aerial' in act else 'o'
            color = '#3399ff' if 'Aerial' in act else '#ffffff'
            pitch.scatter(sub['x_scaled'], sub['y_scaled'], color=color, marker=marker, s=150, ax=ax, label=act)

        plot_placeholder.pyplot(fig)
