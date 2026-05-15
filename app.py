import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
from PIL import Image

# 1. Page Config & Logo
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
    
    # Coordinates Scaling (120x80)
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

    # --- Comprehensive Legend ---
    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', label='Pass Success', markersize=8),
            mlines.Line2D([], [], color='#e74c3c', marker='>', linestyle='-', label='Pass Failed', markersize=8),
            mlines.Line2D([], [], color='blue', marker='>', linestyle='-', label='Cross Success', markersize=8),
            mlines.Line2D([], [], color='red', marker='>', linestyle='--', label='Cross Failed', markersize=8),
            mlines.Line2D([], [], color='#FF69B4', marker='>', linestyle='-', label='Through Ball', markersize=8),
            mlines.Line2D([], [], color='orange', marker='>', linestyle='-', label='Corner', markersize=8),
            mlines.Line2D([], [], color='#40E0D0', marker='>', linestyle='-', label='Free Kick', markersize=8),
            mlines.Line2D([], [], color='blue', marker='x', label='Tackle (Blue X)', linestyle='None', markersize=10, markeredgewidth=2),
            mlines.Line2D([], [], color='purple', marker='d', label='Clearance', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#2ecc71', marker='s', label='Ground Duel Won', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='red', marker='s', label='Ground Duel Lost', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#2ecc71', marker='^', label='Aerial Won', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='red', marker='^', label='Aerial Lost', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='red', marker='x', label='Foul (Red X)', linestyle='None', markersize=10, markeredgewidth=2),
            mlines.Line2D([], [], color='black', marker='o', label='Counterpress (#)', linestyle='None', markersize=8),
            mlines.Line2D([], [], color='gold', marker='*', label='Goal', linestyle='None', markersize=12)
        ]

    # --- Fixed Drawing Logic ---
    def draw_actions(dataframe, ax, pitch_obj, selected_layers):
        for i, row in dataframe.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'ناجح' in tag
            
            # --- Passing Types ---
            if 'pass' in act or 'تمرير' in act:
                if 'cross' in tag and "Crosses" in selected_layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                elif 'through' in tag and "Through Balls" in selected_layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax)
                elif 'corner' in tag and "Corners" in selected_layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                elif 'free kick' in tag and "Free Kicks" in selected_layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#40E0D0', ax=ax)
                elif "Normal Passes" in selected_layers and not any(k in tag for k in ['cross', 'through', 'corner', 'free kick']):
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.6)

            # --- Defensive Types ---
            elif any(word in act for word in ['tackle', 'inter', 'تدخل', 'قطع']):
                if "Tackles" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, color='blue', linewidth=3, ax=ax)
            elif 'clear' in act and "Clearances" in selected_layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='d', s=200, color='purple', ax=ax)
            elif 'aerial' in act and "Aerial Duels" in selected_layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='^', s=250, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax)
            elif 'duel' in act and 'aerial' not in act and "Ground Duels" in selected_layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color='#2ecc71' if is_success else 'red', ax=ax)
            elif 'foul' in act and "Fouls" in selected_layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, color='red', linewidth=3, ax=ax)
            elif ('counter' in act or 'press' in act) and "Counterpress" in selected_layers:
                ax.text(row.x_scaled, row.y_scaled, '#', color='black', fontsize=20, fontweight='bold', ha='center', va='center')
            
            # --- Goals ---
            if ('goal' in tag or 'هدف' in tag) and "Goals" in selected_layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax, zorder=5)

    # --- TAB 1: Individual ---
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        # أزرار تحكم مفصلة
        st.write("### Filter Visual Layers")
        col1, col2 = st.columns(2)
        with col1:
            p_pass_layers = st.multiselect("Passing Actions", ["Normal Passes", "Crosses", "Through Balls", "Corners", "Free Kicks"], default=["Normal Passes", "Crosses"])
        with col2:
            p_def_layers = st.multiselect("Defensive & Attack Actions", ["Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Counterpress", "Goals"], default=["Tackles", "Ground Duels", "Goals"])
        
        all_selected_p = p_pass_layers + p_def_layers

        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig, ax = pitch.draw(figsize=(11, 8))
        add_logo(ax)
        draw_actions(p_df, ax, pitch, all_selected_p)
        ax.legend(handles=get_full_legend(), loc='upper right', fontsize='x-small', framealpha=0.8, bbox_to_anchor=(1.15, 1))
        st.pyplot(fig)

    # --- TAB 2: Team ---
    with tab2:
        st.write("### Global Team Layers")
        tc1, tc2 = st.columns(2)
        with tc1:
            t_pass_layers = st.multiselect("Team Passing", ["Normal Passes", "Crosses", "Through Balls", "Corners", "Free Kicks"], default=["Crosses"])
        with tc2:
            t_def_layers = st.multiselect("Team Defense/Attack", ["Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Counterpress", "Goals"], default=["Tackles", "Ground Duels"])
        
        all_selected_t = t_pass_layers + t_def_layers

        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))
        add_logo(ax_t)
        draw_actions(team_df, ax_t, pitch_t, all_selected_t)
        ax_t.legend(handles=get_full_legend(), loc='upper right', fontsize='x-small', framealpha=0.8, bbox_to_anchor=(1.15, 1))
        st.pyplot(fig_t)

else:
    st.info("👋 ارفع ملف الـ CSV.. كل نوع تمريرة وأكشن بقى ليه زرار مستقل!")
