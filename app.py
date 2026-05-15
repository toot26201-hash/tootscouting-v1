import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
from PIL import Image

# 1. إعدادات الصفحة واللوجو
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

def add_logo(ax):
    try:
        img = Image.open('image_deac96.png')
        ax.imshow(img, extent=[48, 72, 28, 52], alpha=0.15, zorder=0)
    except:
        pass

st.title("⚽ TootScouting | Total Tactical Analysis System")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    df = df.dropna(subset=['Action', 'Team'])
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    tab1, tab2 = st.tabs(["👤 Individual Analysis", "👥 Team Strategy Analysis"])

    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', label='Pass Success'),
            mlines.Line2D([], [], color='#e74c3c', marker='>', linestyle='-', label='Pass Failed'),
            mlines.Line2D([], [], color='blue', marker='>', linestyle='-', label='Cross Success'),
            mlines.Line2D([], [], color='red', marker='>', linestyle='--', label='Cross Failed'),
            mlines.Line2D([], [], color='#FF69B4', label='Through Ball'),
            mlines.Line2D([], [], color='blue', marker='x', linestyle='None', markersize=10, markeredgewidth=2, label='Tackle (Blue X)'),
            mlines.Line2D([], [], color='purple', marker='d', linestyle='None', markersize=10, label='Clearance'),
            mlines.Line2D([], [], color='#2ecc71', marker='s', linestyle='None', label='Ground Duel Won'),
            mlines.Line2D([], [], color='red', marker='s', linestyle='None', label='Ground Duel Lost'),
            mlines.Line2D([], [], color='#2ecc71', marker='^', linestyle='None', label='Aerial Won'),
            mlines.Line2D([], [], color='red', marker='^', linestyle='None', label='Aerial Lost'),
            mlines.Line2D([], [], color='red', marker='x', linestyle='None', markersize=10, label='Foul (Red X)'),
            mlines.Line2D([], [], color='black', marker='o', linestyle='None', label='Counterpress (#)'),
            mlines.Line2D([], [], color='gold', marker='*', linestyle='None', markersize=12, label='Goal')
        ]

    # --- TAB 1: التحليل الفردي ---
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        p_actions = st.multiselect("Player Visuals", sorted(p_df['Action'].unique().tolist()), default=sorted(p_df['Action'].unique().tolist()))
        p_filt = p_df[p_df['Action'].isin(p_actions)]

        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig, ax = pitch.draw(figsize=(11, 8))
        add_logo(ax)

        for i, row in p_filt.iterrows():
            act, tag = str(row['Action']).lower(), str(row['Tags']).lower()
            is_success = 'success' in tag
            
            if 'pass' in act:
                if 'cross' in tag:
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                elif 'through' in tag:
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax)
                else:
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', alpha=0.7, ax=ax)
            
            # تم تحسين شروط البحث هنا لتشمل الكلمات الجزئية
            elif 'tackle' in act or 'interception' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, color='blue', linewidth=3, ax=ax)
            elif 'clearance' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='d', s=200, color='purple', ax=ax)
            elif 'aerial' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='^', s=250, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax)
            elif 'duel' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color='#2ecc71' if is_success else 'red', ax=ax)
            elif 'foul' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, color='red', linewidth=3, ax=ax)
            elif 'counter' in act or 'press' in act:
                ax.text(row.x_scaled, row.y_scaled, '#', color='black', fontsize=20, fontweight='bold', ha='center', va='center')
            elif 'goal' in tag:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax, zorder=5)

        ax.legend(handles=get_full_legend(), loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9)
        st.pyplot(fig)

    # --- TAB 2: التحليل الجماعي ---
    with tab2:
        st.subheader(f"Team Tactical Master: {selected_team}")
        col1, col2 = st.columns(2)
        with col1:
            p_opt = st.multiselect("Passing Layers", ["Normal Passes", "Crosses", "Through Balls"], default=["Normal Passes", "Crosses"])
        with col2:
            d_opt = st.multiselect("Defense & Attack Layers", ["Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Counterpress", "Goals"], default=["Tackles", "Ground Duels", "Goals"])
        
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))
        add_logo(ax_t)

        for i, row in team_df.iterrows():
            act, tag = str(row['Action']).lower(), str(row['Tags']).lower()
            is_success = 'success' in tag

            if "Normal Passes" in p_opt and "pass" in act and "cross" not in tag and "through" not in tag:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=1.5, color='#2ecc71' if is_success else '#e74c3c', alpha=0.3, ax=ax_t)
            if "Crosses" in p_opt and "cross" in tag:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax_t)
            if "Through Balls" in p_opt and "through" in tag:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax_t)

            # تفعيل خيارات الدفاع في الجماعي
            if "Tackles" in d_opt and ('tackle' in act or 'interception' in act):
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='x', s=180, color='blue', linewidth=2, ax=ax_t)
            if "Clearances" in d_opt and 'clearance' in act:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='d', s=150, color='purple', ax=ax_t)
            if "Ground Duels" in d_opt and 'duel' in act and 'aerial' not in act:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='s', s=120, color='#2ecc71' if is_success else 'red', ax=ax_t)
            if "Aerial Duels" in d_opt and 'aerial' in act:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='^', s=150, color='#2ecc71' if is_success else 'red', ax=ax_t)
            if "Fouls" in d_opt and 'foul' in act:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='x', s=180, color='red', ax=ax_t)
            if "Counterpress" in d_opt and ("counter" in act or "press" in act):
                ax_t.text(row.x_scaled, row.y_scaled, '#', color='black', fontsize=15, ha='center', va='center')
            if "Goals" in d_opt and "goal" in tag:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='*', s=800, color='gold', edgecolors='black', ax=ax_t, zorder=6)

        ax_t.legend(handles=get_full_legend(), loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9)
        st.pyplot(fig_t)
