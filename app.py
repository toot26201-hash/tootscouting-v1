import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines

st.set_page_config(page_title="TootScouting Ultimate Pro", layout="wide")

st.title("⚽ TootScouting | Total Performance Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 1. تجهيز الإحداثيات
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    # تنظيف البيانات
    df = df.dropna(subset=['Action', 'Team'])
    
    # القائمة الجانبية
    st.sidebar.header("Global Filters")
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    # إنشاء التبويبات (فردي وجماعي)
    tab1, tab2 = st.tabs(["👤 Individual Analysis", "👥 Team Analysis"])

    # ---------------------------------------------------------
    # TAB 1: التحليل الفردي (كل الشغل اللي عملناه بالرموز والألوان)
    # ---------------------------------------------------------
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        selected_player = st.selectbox("Select Player", player_list)
        player_df = team_df[team_df['Player'] == selected_player].copy()
        
        ind_actions = st.multiselect("Select Player Actions", sorted(player_df['Action'].unique().tolist()), default=sorted(player_df['Action'].unique().tolist()))
        p_filtered = player_df[player_df['Action'].isin(ind_actions)]

        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--', linewidth=1)
        fig, ax = pitch.draw(figsize=(12, 8))

        for i, row in p_filtered.iterrows():
            tag_str = str(row['Tags']).lower()
            action = str(row['Action']).lower()
            is_success = 'success' in tag_str
            color = '#2ecc71' if is_success else '#e74c3c'

            if 'shot' in action:
                shot_color = '#0000FF' if 'on target' in tag_str else '#FF00FF'
                pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=550, color=shot_color, edgecolors='black', ax=ax, zorder=5)
            elif 'pass' in action:
                if pd.notnull(row['x_end_scaled']):
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color=color, ax=ax, alpha=0.6)
            elif 'aerial' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='^', s=250, color=color, edgecolors='black', ax=ax)
            elif 'duel' in action or 'tackle' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color=color, edgecolors='black', ax=ax)
            elif 'extraction' in action or 'interception' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, linewidth=3, color=color, ax=ax)
            elif 'dribble' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='o', s=200, facecolors='none', edgecolors=color, linewidth=2, ax=ax)
            elif 'carry' in action or 'run' in action:
                if pd.notnull(row['x_end_scaled']):
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#f1c40f', linestyle='--', ax=ax)

        # Legend (Right Side)
        legend_elements = [
            mlines.Line2D([], [], color='#0000FF', marker='*', linestyle='None', markersize=10, label='Shot ON'),
            mlines.Line2D([], [], color='#FF00FF', marker='*', linestyle='None', markersize=10, label='Shot OFF'),
            mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', label='Pass Success'),
            mlines.Line2D([], [], color='#e74c3c', marker='>', linestyle='-', label='Pass Failed'),
            mlines.Line2D([], [], color='black', marker='^', linestyle='None', label='Aerial'),
            mlines.Line2D([], [], color='black', marker='s', linestyle='None', label='Ground Duel'),
            mlines.Line2D([], [], color='black', marker='x', linestyle='None', label='Interception'),
            mlines.Line2D([], [], color='#f1c40f', marker='>', linestyle='--', label='Ball Carry')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small')
        st.pyplot(fig)

    # ---------------------------------------------------------
    # TAB 2: التحليل الجماعي (Area 14, Box Entries, etc)
    # ---------------------------------------------------------
    with tab2:
        st.subheader(f"Team Performance Profile: {selected_team}")
        
        # حساب إحصائيات الفريق
        col1, col2, col3, col4 = st.columns(4)
        
        shots = team_df[team_df['Action'].str.contains('shot', case=False, na=False)]
        goals = team_df[team_df['Tags'].str.contains('goal', case=False, na=False)]
        # Area 14 Entry: passes ending in x: 80-102 and y: 18-62
        area14 = team_df[(team_df['x_end_scaled'] >= 80) & (team_df['x_end_scaled'] <= 102) & (team_df['y_end_scaled'] >= 18) & (team_df['y_end_scaled'] <= 62)]
        # Box Entry: x_end > 102
        box_entries = team_df[(team_df['x_end_scaled'] > 102) & (team_df['y_end_scaled'] >= 18) & (team_df['y_end_scaled'] <= 62)]

        col1.metric("Total Shots", len(shots))
        col2.metric("Goals", len(goals))
        col3.metric("Area 14 Entries", len(area14))
        col4.metric("Box Entries", len(box_entries))

        # رسم خريطة الفريق الحرارية والـ Zones الهجومية
        st.subheader("Team Offensive Zones & Heatmap")
        pitch_team = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b')
        fig_t, ax_t = pitch_team.draw(figsize=(12, 8))
        
        # رسم Area 14 مظللة
        pitch_team.box(xstart=80, ystart=18, xend=102, yend=62, ax=ax_t, color='blue', alpha=0.1)
        ax_t.text(91, 40, "Area 14", color='blue', ha='center', va='center', alpha=0.5)

        # رسم الـ Heatmap
        pitch_team.kdeplot(team_df.x_scaled, team_df.y_scaled, ax=ax_t, fill=True, cmap='Reds', alpha=0.5)
        
        # رسم الأهداف فقط كعلامات ذهبية
        if not goals.empty:
            pitch_team.scatter(goals.x_scaled, goals.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax_t, label='Goals')

        st.pyplot(fig_t)
        st.write("💡 *The heatmap shows team dominance zones, while 'Area 14' highlights your creative hub access.*")

else:
    st.info("👋 Upload your CSV to access both Individual and Team analytics.")
