import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import matplotlib.patches as patches

st.set_page_config(page_title="TootScouting Tactical Master", layout="wide")

st.title("⚽ TootScouting | Advanced Strategic Analytics")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تحويل الإحداثيات لمقياس StatsBomb (120x80)
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    df = df.dropna(subset=['Action', 'Team'])
    
    st.sidebar.header("Global Filters")
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    tab1, tab2 = st.tabs(["👤 Individual Analysis", "👥 Team Strategy & Box Control"])

    # --- TAB 1: التحليل الفردي (النسخة المستقرة) ---
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        p_actions = st.multiselect("Actions", sorted(p_df['Action'].unique().tolist()), default=sorted(p_df['Action'].unique().tolist()))
        p_filt = p_df[p_df['Action'].isin(p_actions)]
        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig, ax = pitch.draw(figsize=(10, 7))
        for i, row in p_filt.iterrows():
            tag, act = str(row['Tags']).lower(), str(row['Action']).lower()
            color = '#2ecc71' if 'success' in tag else '#e74c3c'
            if 'shot' in act or 'sh/a' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=400, color='#0000FF' if 'on target' in tag else '#FF00FF', ax=ax)
            elif 'pass' in act:
                pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color=color, ax=ax, alpha=0.5)
        st.pyplot(fig)

    # ---------------------------------------------------------
    # TAB 2: التحليل الجماعي الاستراتيجي (تصحيح الـ ValueError)
    # ---------------------------------------------------------
    with tab2:
        st.subheader(f"Strategy & Penetration: {selected_team}")
        
        team_options = st.multiselect("Tactical Layers", 
            ["Final Third Entries", "Box Entries", "Touches Inside Box", "Area 14 Hub", "Through Balls", "Goals/Shots", "Heat Map"],
            default=["Box Entries", "Goals/Shots", "Area 14 Hub"])

        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))

        # 1. Area 14 Hub Visual
        if "Area 14 Hub" in team_options:
            rect_a14 = patches.Rectangle((80, 18), 22, 44, linewidth=2, edgecolor='blue', facecolor='blue', alpha=0.05, zorder=1)
            ax_t.add_patch(rect_a14)

        # 2. Heat Map
        if "Heat Map" in team_options:
            pitch_t.kdeplot(team_df.x_scaled, team_df.y_scaled, ax=ax_t, fill=True, cmap='Reds', alpha=0.2, zorder=0)

        for i, row in team_df.iterrows():
            act, tag = str(row['Action']).lower(), str(row['Tags']).lower()
            
            # --- تحليل الدخول للثلث الأخير ---
            if "Final Third Entries" in team_options and row.x_scaled < 80 and row.x_end_scaled >= 80:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=1.5, color='#9b59b6', alpha=0.3, ax=ax_t)

            # --- تحليل الدخول لمنطقة الجزاء ---
            in_box_end = (row.x_end_scaled > 102) & (row.y_end_scaled > 18) & (row.y_end_scaled < 62)
            if "Box Entries" in team_options and in_box_end:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71', alpha=0.6, ax=ax_t)

            # --- لمسات الصندوق الملونة (Touches Inside Box) ---
            in_box_start = (row.x_scaled > 102) & (row.y_scaled > 18) & (row.y_scaled < 62)
            if "Touches Inside Box" in team_options and in_box_start:
                if 'shot' in act or 'sh/a' in act: t_col = 'blue'    # تسديد
                elif 'pass' in act: t_col = 'green'               # تمرير
                elif 'dribble' in act: t_col = 'orange'            # مراوغة
                else: t_col = 'black'                              # لمسة أخرى
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='o', s=80, color=t_col, edgecolors='white', ax=ax_t, zorder=4)

            # --- الثرو بولز والأهداف ---
            if "Through Balls" in team_options and "through" in tag:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax_t)
            
            if "Goals/Shots" in team_options and "goal" in tag:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='*', s=700, color='gold', edgecolors='black', ax=ax_t, zorder=6)

        # Legend on Image
        legend_els = [
            mlines.Line2D([], [], color='#2ecc71', marker='>', label='Box Entry'),
            mlines.Line2D([], [], color='#9b59b6', marker='>', label='Final 3rd Entry'),
            mlines.Line2D([], [], color='blue', marker='o', linestyle='None', label='Shot in Box'),
            mlines.Line2D([], [], color='green', marker='o', linestyle='None', label='Pass in Box'),
            mlines.Line2D([], [], color='orange', marker='o', linestyle='None', label='Dribble in Box'),
            mlines.Line2D([], [], color='gold', marker='*', linestyle='None', markersize=10, label='Goal')
        ]
        ax_t.legend(handles=legend_els, loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9)
        st.pyplot(fig_t)

        # --- تصحيح الـ Metrics (السبب الرئيسي للخطأ) ---
        st.write("---")
        m1, m2, m3, m4 = st.columns(4)
        
        # استخدام & للفصل بين الشروط بدل المقارنة المزدوجة
        box_count = len(team_df[(team_df['x_end_scaled'] > 102) & (team_df['y_end_scaled'] > 18) & (team_df['y_end_scaled'] < 62)])
        f3rd_count = len(team_df[(team_df['x_scaled'] < 80) & (team_df['x_end_scaled'] >= 80)])
        a14_count = len(team_df[(team_df['x_end_scaled'] >= 80) & (team_df['x_end_scaled'] <= 102) & (team_df['y_end_scaled'] > 18) & (team_df['y_end_scaled'] < 62)])
        goal_count = len(team_df[team_df['Tags'].str.contains('goal', case=False, na=False)])

        m1.metric("Box Entries", box_count)
        m2.metric("Final 3rd Entries", f3rd_count)
        m3.metric("Area 14 Hub", a14_count)
        m4.metric("Goals", goal_count)

else:
    st.info("👋 Upload CSV to solve errors and start analysis.")
