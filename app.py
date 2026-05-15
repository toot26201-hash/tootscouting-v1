import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import matplotlib.patches as patches

# 1. إعدادات الصفحة
st.set_page_config(page_title="TootScouting Tactical Pro", layout="wide")

st.title("⚽ TootScouting | Total Performance Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 2. تجهيز الإحداثيات (StatsBomb Scale 120x80)
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    df = df.dropna(subset=['Action', 'Team'])
    
    # 3. الفلاتر الجانبية
    st.sidebar.header("Global Filters")
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    tab1, tab2 = st.tabs(["👤 Individual Analysis", "👥 Team Tactical Map"])

    # ---------------------------------------------------------
    # TAB 1: التحليل الفردي (النسخة الاحترافية)
    # ---------------------------------------------------------
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        p_actions = st.multiselect("Player Options", sorted(p_df['Action'].unique().tolist()), default=sorted(p_df['Action'].unique().tolist()))
        p_filt = p_df[p_df['Action'].isin(p_actions)]

        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig, ax = pitch.draw(figsize=(12, 8))
        
        for i, row in p_filt.iterrows():
            tag, act = str(row['Tags']).lower(), str(row['Action']).lower()
            is_success = 'success' in tag
            col = '#2ecc71' if is_success else '#e74c3c'
            
            if 'shot' in act or 'sh/a' in act:
                s_col = '#0000FF' if 'on target' in tag else '#FF00FF'
                pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=500, color=s_col, edgecolors='black', ax=ax, zorder=5)
            elif 'pass' in act:
                pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color=col, ax=ax, alpha=0.6)
            elif 'aerial' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='^', s=250, color=col, edgecolors='black', ax=ax)
            elif 'duel' in act or 'tackle' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color=col, edgecolors='black', ax=ax)
            elif 'dribble' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='o', s=200, facecolors='none', edgecolors=col, linewidth=2, ax=ax)

        st.pyplot(fig)

    # ---------------------------------------------------------
    # TAB 2: التحليل الجماعي (كتالوج الألوان اللي طلبته)
    # ---------------------------------------------------------
    with tab2:
        st.subheader(f"Team Tactical Distribution: {selected_team}")
        
        team_options = st.multiselect("Select Team Visuals", 
            ["Normal Passes", "Crosses", "Corners", "Through Balls", "Free Kicks", "Throw-in", "Goals/Shots", "Area 14 Hub"],
            default=["Normal Passes", "Crosses", "Goals/Shots"])

        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))

        if "Area 14 Hub" in team_options:
            rect_a14 = patches.Rectangle((80, 18), 22, 44, linewidth=2, edgecolor='blue', facecolor='blue', alpha=0.05, zorder=1)
            ax_t.add_patch(rect_a14)

        for i, row in team_df.iterrows():
            act, tag = str(row['Action']).lower(), str(row['Tags']).lower()
            is_success = 'success' in tag
            
            # 1. الأهداف والتسديدات
            if "Goals/Shots" in team_options:
                if "goal" in tag:
                    pitch_t.scatter(row.x_scaled, row.y_scaled, marker='*', s=800, color='gold', edgecolors='black', ax=ax_t, zorder=6)
                elif "shot" in act or "sh/a" in act:
                    s_col = '#0000FF' if 'on target' in tag else '#FF00FF'
                    pitch_t.scatter(row.x_scaled, row.y_scaled, marker='*', s=350, color=s_col, ax=ax_t, zorder=5)

            # 2. التمريرات العادية (أخضر/أحمر)
            if "Normal Passes" in team_options and "pass" in act and "cross" not in tag and "through" not in tag:
                p_col = '#2ecc71' if is_success else '#e74c3c'
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=1.5, color=p_col, alpha=0.3, ax=ax_t)

            # 3. الكروسات (أزرق: سليم/متقطع)
            if "Crosses" in team_options and "cross" in tag:
                l_style = '-' if is_success else '--'
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue', linestyle=l_style, ax=ax_t)

            # 4. الكورنر (برتقالي)
            if "Corners" in team_options and "corner" in tag:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange', ax=ax_t)

            # 5. الثرو (روز)
            if "Through Balls" in team_options and "through" in tag:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax_t)

            # 6. الفري كيك (تركواز)
            if "Free Kicks" in team_options and "free kick" in tag:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#40E0D0', ax=ax_t)
            
            # 7. التماس (رمادي)
            if "Throw-in" in team_options and "throw-in" in tag:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#A9A9A9', ax=ax_t)

        # --- Legend on Image (Right Side) ---
        legend_els = [
            mlines.Line2D([], [], color='#2ecc71', marker='>', label='Pass Success'),
            mlines.Line2D([], [], color='#e74c3c', marker='>', label='Pass Failed'),
            mlines.Line2D([], [], color='blue', linestyle='-', label='Cross Success'),
            mlines.Line2D([], [], color='blue', linestyle='--', label='Cross Failed'),
            mlines.Line2D([], [], color='orange', label='Corner'),
            mlines.Line2D([], [], color='#FF69B4', label='Through Ball'),
            mlines.Line2D([], [], color='#40E0D0', label='Free Kick'),
            mlines.Line2D([], [], color='gold', marker='*', linestyle='None', label='Goal')
        ]
        ax_t.legend(handles=legend_els, loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9)
        
        st.pyplot(fig_t)

else:
    st.info("👋 Upload CSV to start the master tactical report.")
