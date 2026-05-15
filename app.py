import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import matplotlib.patches as patches

st.set_page_config(page_title="TootScouting Tactical Pro", layout="wide")

st.title("⚽ TootScouting | Total Performance Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # Scaling to StatsBomb (120x80)
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

    tab1, tab2 = st.tabs(["👤 Individual Analysis", "👥 Team Analysis"])

    # ---------------------------------------------------------
    # TAB 1: التحليل الفردي (نفس شغلك الاحترافي)
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
            tag = str(row['Tags']).lower()
            act = str(row['Action']).lower()
            col = '#2ecc71' if 'success' in tag else '#e74c3c'
            if 'shot' in act:
                s_col = '#0000FF' if 'on target' in tag else '#FF00FF'
                pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=500, color=s_col, edgecolors='black', ax=ax)
            elif 'pass' in act:
                pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color=col, ax=ax, alpha=0.6)
            elif 'aerial' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='^', s=250, color=col, edgecolors='black', ax=ax)
            elif 'duel' in act or 'tackle' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color=col, edgecolors='black', ax=ax)
            elif 'extraction' in act or 'interception' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, color=col, ax=ax)
            elif 'dribble' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='o', s=200, facecolors='none', edgecolors=col, linewidth=2, ax=ax)
            elif 'carry' in act or 'run' in act:
                pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#f1c40f', linestyle='--', ax=ax)

        st.pyplot(fig)

    # ---------------------------------------------------------
    # TAB 2: التحليل الجماعي (برموز ثابتة وجاهزة)
    # ---------------------------------------------------------
    with tab2:
        st.subheader(f"Team Tactical Options: {selected_team}")
        team_options = st.multiselect("Select Team Visuals", 
            ["Goals", "Shots", "Box Entries", "Touches inside Box", "Final Third Entries", "Passes (All)", "Fouls", "Area 14 Hub", "Heat Map"],
            default=["Goals", "Shots", "Area 14 Hub"])

        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))

        # 1. Heat Map (Underlay)
        if "Heat Map" in team_options:
            pitch_t.kdeplot(team_df.x_scaled, team_df.y_scaled, ax=ax_t, fill=True, cmap='Reds', alpha=0.2, zorder=0)

        # 2. Area 14 Hub
        if "Area 14 Hub" in team_options:
            rect_a14 = patches.Rectangle((80, 18), 22, 44, linewidth=2, edgecolor='blue', facecolor='blue', alpha=0.1, zorder=1)
            ax_t.add_patch(rect_a14)
            ax_t.text(91, 40, "Area 14", color='blue', ha='center', va='center', fontweight='bold', alpha=0.5)

        for i, row in team_df.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            
            # Goals (Gold Stars)
            if "Goals" in team_options and "goal" in tag:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='*', s=800, color='gold', edgecolors='black', ax=ax_t, zorder=6)
            
            # Shots (Stars)
            elif "Shots" in team_options and "shot" in act:
                s_col = '#0000FF' if 'on target' in tag else '#FF00FF'
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='*', s=350, color=s_col, ax=ax_t, zorder=5)

            # Box Entries (Green Arrows into the box)
            if "Box Entries" in team_options and row.x_end_scaled > 102 and (18 < row.y_end_scaled < 62):
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71', alpha=0.5, ax=ax_t)
            
            # Touches inside Box (Black Dots)
            in_box = (row.x_scaled > 102) and (18 < row.y_scaled < 62)
            if "Touches inside Box" in team_options and in_box:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='o', s=60, color='black', alpha=0.3, ax=ax_t)

            # Final Third Entries (Blue Arrows)
            if "Final Third Entries" in team_options and row.x_scaled < 80 and row.x_end_scaled > 80:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=1, color='blue', alpha=0.3, ax=ax_t)

            # Fouls (P Marker)
            if "Fouls" in team_options and "foul" in act:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='P', s=200, color='orange', edgecolors='black', ax=ax_t)

        # --- Legend on Image (Right Side) ---
        legend_els = [
            mlines.Line2D([], [], color='gold', marker='*', linestyle='None', markersize=12, label='Goal'),
            mlines.Line2D([], [], color='#0000FF', marker='*', linestyle='None', markersize=10, label='Shot ON'),
            mlines.Line2D([], [], color='#FF00FF', marker='*', linestyle='None', markersize=10, label='Shot OFF'),
            mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', markersize=8, label='Box Entry'),
            mlines.Line2D([], [], color='blue', alpha=0.3, marker='>', linestyle='-', markersize=8, label='Final 3rd Entry'),
            mlines.Line2D([], [], color='black', alpha=0.3, marker='o', linestyle='None', markersize=6, label='Box Touch'),
            mlines.Line2D([], [], color='blue', alpha=0.1, marker='s', linestyle='None', markersize=15, label='Area 14'),
            mlines.Line2D([], [], color='orange', marker='P', linestyle='None', markersize=10, label='Foul')
        ]
        ax_t.legend(handles=legend_els, loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9, edgecolor='black')
        
        st.pyplot(fig_t)

else:
    st.info("👋 Ready for Team & Individual Analysis? Upload CSV.")
