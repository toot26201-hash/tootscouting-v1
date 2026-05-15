import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import matplotlib.patches as patches
from PIL import Image

# 1. إعدادات الصفحة واللوجو
st.set_page_config(page_title="TootScouting Tactical Pro", layout="wide")

def add_logo(ax):
    try:
        img = Image.open('image_deac96.png')
        ax.imshow(img, extent=[48, 72, 28, 52], alpha=0.15, zorder=0)
    except:
        pass

st.title("⚽ TootScouting | Total Performance Analysis")

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

    # --- دليل الرموز الشامل (بناءً على تعليماتك الأخيرة) ---
    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#2ecc71', marker='>', label='Pass Success'),
            mlines.Line2D([], [], color='blue', marker='>', linestyle='-', label='Cross Success'),
            mlines.Line2D([], [], color='red', marker='>', linestyle='--', label='Cross/Corner Failed'),
            mlines.Line2D([], [], color='#FF69B4', label='Through Ball'),
            mlines.Line2D([], [], color='#2ecc71', marker='^', linestyle='None', label='Aerial Won'),
            mlines.Line2D([], [], color='red', marker='^', linestyle='None', label='Aerial Lost'),
            mlines.Line2D([], [], color='red', marker='s', linestyle='None', label='Ground Duel (All)'),
            mlines.Line2D([], [], color='black', marker='X', linestyle='None', label='Foul (Red X)'),
            mlines.Line2D([], [], color='black', marker='$#$', linestyle='None', label='Counterpress (#)'),
            mlines.Line2D([], [], color='gold', marker='*', linestyle='None', markersize=12, label='Goal'),
        ]

    # ---------------------------------------------------------
    # TAB 1: التحليل الفردي
    # ---------------------------------------------------------
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
            
            # 1. التمريرات
            if 'pass' in act:
                if 'cross' in tag:
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                elif 'through' in tag:
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax)
                else:
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', alpha=0.7, ax=ax)
            
            # 2. الإجراءات الدفاعية (الرموز الجديدة)
            elif 'aerial' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='^', s=250, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax)
            elif 'tackle' in act or 'duel' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color='red', ax=ax) # أرضي أحمر دايماً
            elif 'foul' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, color='red', linewidth=3, ax=ax)
            elif 'counter' in act or 'press' in act:
                ax.text(row.x_scaled, row.y_scaled, '#', color='black', fontsize=20, fontweight='bold', ha='center', va='center')

            # 3. الأهداف
            elif 'shot' in act or 'sh/a' in act:
                if 'goal' in tag:
                    pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax, zorder=5)

        ax.legend(handles=get_full_legend(), loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9)
        st.pyplot(fig)

    # ---------------------------------------------------------
    # TAB 2: التحليل الجماعي
    # ---------------------------------------------------------
    with tab2:
        st.subheader(f"Team Tactical Master: {selected_team}")
        team_options = st.multiselect("Tactical Layers", ["Passes", "Defensive Actions", "Goals/Shots", "Area 14 Hub"], default=["Passes", "Defensive Actions"])
        
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))
        add_logo(ax_t)

        for i, row in team_df.iterrows():
            act, tag = str(row['Action']).lower(), str(row['Tags']).lower()
            is_success = 'success' in tag

            if "Defensive Actions" in team_options:
                if 'aerial' in act:
                    pitch_t.scatter(row.x_scaled, row.y_scaled, marker='^', s=150, color='#2ecc71' if is_success else 'red', ax=ax_t)
                elif 'tackle' in act or 'duel' in act:
                    pitch_t.scatter(row.x_scaled, row.y_scaled, marker='s', s=120, color='red', ax=ax_t)
                elif 'foul' in act:
                    pitch_t.scatter(row.x_scaled, row.y_scaled, marker='x', s=180, color='red', ax=ax_t)

        ax_t.legend(handles=get_full_legend(), loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9)
        st.pyplot(fig_t)
