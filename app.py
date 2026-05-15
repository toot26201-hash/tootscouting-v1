import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import matplotlib.patches as patches # مهمة جداً لرسم المربعات

st.set_page_config(page_title="TootScouting Ultimate Pro", layout="wide")

st.title("⚽ TootScouting | Total Performance Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 1. تجهيز الإحداثيات (StatsBomb Scale)
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    # تنظيف البيانات
    df = df.dropna(subset=['Action', 'Team'])
    
    # القائمة الجانبية للفريق
    st.sidebar.header("Global Filters")
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    tab1, tab2 = st.tabs(["👤 Individual Analysis", "👥 Team Analysis"])

    # --- TAB 1: التحليل الفردي (النسخة الاحترافية بالرموز) ---
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

            # تطبيق الرموز المخصصة (Shot, Pass, Aerial, Duel, etc.)
            if 'shot' in action or 'sh/a' in action:
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
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.8)
        st.pyplot(fig)

    # --- TAB 2: التحليل الجماعي (تحديث منطقة Area 14 و Box Entries) ---
    with tab2:
        st.subheader(f"Team Performance Profile: {selected_team}")
        
        # مسميات الأكشن من ملفك لضمان دقة الحسابات
        shots_team = team_df[team_df['Action'].str.contains('shot|sh/a', case=False, na=False)]
        goals_team = team_df[team_df['Tags'].str.contains('goal', case=False, na=False)]
        
        # حساب الدخول للمناطق الحساسة
        area14_entries = team_df[(team_df['x_end_scaled'] >= 80) & (team_df['x_end_scaled'] <= 102) & 
                                (team_df['y_end_scaled'] >= 18) & (team_df['y_end_scaled'] <= 62)]
        
        box_entries = team_df[(team_df['x_end_scaled'] > 102) & 
                             (team_df['y_end_scaled'] >= 18) & (team_df['y_end_scaled'] <= 62)]
        
        final_third = team_df[(team_df['x_end_scaled'] > 80)]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Shots", len(shots_team))
        col2.metric("Goals Scored", len(goals_team))
        col3.metric("Area 14 Access", len(area14_entries))
        col4.metric("Box Entries", len(box_entries))

        st.subheader("Team Dominance Map")
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 8))
        
        # --- حل مشكلة الخطأ: رسم Area 14 باستخدام Patch يدوي ---
        # إحداثيات Area 14 في Statsbomb: يبدأ من x=80 وطوله 22، يبدأ من y=18 وعرضه 44
        area14_rect = patches.Rectangle((80, 18), 22, 44, linewidth=2, edgecolor='blue', facecolor='blue', alpha=0.1, zorder=1)
        ax_t.add_patch(area14_rect)
        ax_t.text(91, 40, "Area 14", color='blue', ha='center', va='center', fontweight='bold', alpha=0.5)

        # رسم الـ Heatmap الجماعية
        if len(team_df) > 1:
            pitch_t.kdeplot(team_df.x_scaled, team_df.y_scaled, ax=ax_t, fill=True, cmap='Reds', alpha=0.4, zorder=0)

        # رسم الأهداف كنجوم ذهبية مميزة للفريق
        if not goals_team.empty:
            pitch_t.scatter(goals_team.x_scaled, goals_team.y_scaled, marker='*', s=700, color='gold', edgecolors='black', ax=ax_t, zorder=5, label='Goals')

        st.pyplot(fig_t)

else:
    st.info("👋 Upload your CSV file to generate the complete Individual & Team report.")
