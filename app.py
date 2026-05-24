import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
from PIL import Image

# 1. Page Config & Logo
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

def add_logo(ax):
    try:import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines

st.set_page_config(page_title="TootScouting Tactical Pro", layout="wide")

st.title("⚽ TootScouting | Elite Tactical Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # Scaling coordinates to StatsBomb dimensions (120x80)
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    st.sidebar.header("Analysis Filters")
    df = df.dropna(subset=['Action', 'Player'])
    
    player_list = sorted(df['Player'].unique().tolist())
    selected_player = st.sidebar.selectbox("Select Player", player_list)
    player_df = df[df['Player'] == selected_player].copy()

    action_list = sorted(player_df['Action'].unique().tolist())
    selected_actions = st.sidebar.multiselect("Select Actions to Display", action_list, default=action_list)

    filtered_df = player_df[player_df['Action'].isin(selected_actions)]

    tab1, tab2 = st.tabs(["📊 Data Table", "🏟️ Tactical Pitch"])

    with tab1:
        st.subheader(f"Detailed Stats for: {selected_player}")
        st.dataframe(filtered_df)

    with tab2:
        # White pitch with dashed lines
        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', 
                      linestyle='--', linewidth=1, goal_linestyle='-')
        fig, ax = pitch.draw(figsize=(12, 9))

        # القائمة دي هنستخدمها عشان نبني الدليل داخل الصورة
        legend_elements = []

        for i, row in filtered_df.iterrows():
            tag_str = str(row['Tags']).lower()
            action = str(row['Action']).lower()
            is_success = 'success' in tag_str
            base_color = '#2ecc71' if is_success else '#e74c3c'

            # 1. Shot (Stars)
            if 'shot' in action:
                shot_color = '#0000FF' if 'on target' in tag_str else '#FF00FF'
                pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=550, 
                              color=shot_color, edgecolors='black', ax=ax, zorder=5)

            # 2. Pass (Arrows)
            elif 'pass' in action:
                if pd.notnull(row['x_end_scaled']):
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                                 width=2, color=base_color, ax=ax, alpha=0.6)

            # 3. Aerial Duel (Triangle)
            elif 'aerial' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='^', s=250, 
                              color=base_color, edgecolors='black', ax=ax)

            # 4. Ground Duel / Tackle (Square)
            elif 'duel' in action or 'tackle' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, 
                              color=base_color, edgecolors='black', ax=ax)

            # 5. Extraction / Interception (X)
            elif 'extraction' in action or 'interception' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, 
                              linewidth=3, color=base_color, ax=ax)

            # 6. Dribble (Hollow Circle)
            elif 'dribble' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='o', s=200, 
                              facecolors='none', edgecolors=base_color, linewidth=2, ax=ax)

            # 7. Ball Carry (Yellow Dashed Arrow)
            elif 'carry' in action or 'run' in action:
                if pd.notnull(row['x_end_scaled']):
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                                 width=2, color='#f1c40f', linestyle='--', ax=ax)

        # --- بناء الدليل داخل الصورة (Legend) ---
        legend_elements = [
            mlines.Line2D([], [], color='#0000FF', marker='*', linestyle='None', markersize=12, label='Shot ON Target'),
            mlines.Line2D([], [], color='#FF00FF', marker='*', linestyle='None', markersize=12, label='Shot OFF Target'),
            mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', markersize=8, label='Pass Success'),
            mlines.Line2D([], [], color='#e74c3c', marker='>', linestyle='-', markersize=8, label='Pass Failed'),
            mlines.Line2D([], [], color='#2ecc71', marker='^', linestyle='None', markersize=10, label='Aerial Won'),
            mlines.Line2D([], [], color='#e74c3c', marker='^', linestyle='None', markersize=10, label='Aerial Lost'),
            mlines.Line2D([], [], color='#2ecc71', marker='s', linestyle='None', markersize=10, label='Ground Won'),
            mlines.Line2D([], [], color='#e74c3c', marker='s', linestyle='None', markersize=10, label='Ground Lost'),
            mlines.Line2D([], [], color='black', marker='x', linestyle='None', markersize=10, label='Interception/X'),
            mlines.Line2D([], [], color='#f1c40f', marker='>', linestyle='--', markersize=8, label='Ball Carry'),
        ]

        # إضافة المربع للصورة
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1), 
                  fontsize='small', facecolor='white', framealpha=0.8, edgecolor='black')

        st.pyplot(fig)
        st.write("💡 *Now the legend is part of the image. You can right-click and 'Save Image As' to share it.*")

else:
    st.info("👋 Upload your CSV file to generate the professional tactical map.")
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

    # --- Unified Legend (The Master Legend) ---
    def get_full_legend():
        return [
            # Passing Legend
            mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', label='Pass Success', markersize=8),
            mlines.Line2D([], [], color='#e74c3c', marker='>', linestyle='-', label='Pass Failed', markersize=8),
            mlines.Line2D([], [], color='blue', marker='>', linestyle='-', label='Cross Success', markersize=8),
            mlines.Line2D([], [], color='red', marker='>', linestyle='--', label='Cross Failed', markersize=8),
            mlines.Line2D([], [], color='#FF69B4', marker='>', linestyle='-', label='Through Ball', markersize=8),
            mlines.Line2D([], [], color='orange', marker='>', linestyle='-', label='Corner', markersize=8),
            mlines.Line2D([], [], color='#40E0D0', marker='>', linestyle='-', label='Free Kick', markersize=8),
            # Defensive & Attack Legend
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

    # --- Drawing Engine ---
    def draw_actions(dataframe, ax, pitch_obj, selected_layers):
        for i, row in dataframe.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'ناجح' in tag
            
            # 1. Passes Logic
            if 'pass' in act or 'تمرير' in act:
                if "Passes" in selected_layers:
                    if 'cross' in tag:
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                    elif 'through' in tag:
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax)
                    elif 'corner' in tag:
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                    elif 'free kick' in tag:
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#40E0D0', ax=ax)
                    else:
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.6)

            # 2. Tackles / Interceptions
            elif any(word in act for word in ['tackle', 'inter', 'تدخل', 'قطع']):
                if "Tackles" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, color='blue', linewidth=3, ax=ax)
            
            # 3. Clearances
            elif any(word in act for word in ['clear', 'تشتيت']):
                if "Clearances" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='d', s=200, color='purple', ax=ax)
            
            # 4. Aerial Duels
            elif any(word in act for word in ['aerial', 'هوائي']):
                if "Aerial Duels" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='^', s=250, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax)
            
            # 5. Ground Duels
            elif any(word in act for word in ['duel', 'ground', 'التحام', 'صراع']) and 'aerial' not in act:
                if "Ground Duels" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color='#2ecc71' if is_success else 'red', ax=ax)
            
            # 6. Fouls
            elif 'foul' in act:
                if "Fouls" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, color='red', linewidth=3, ax=ax)

            # 7. Goals
            if 'goal' in tag or 'هدف' in tag:
                if "Goals" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax, zorder=5)

    # --- TAB 1: Individual ---
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        p_layers = ["Passes", "Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Goals"]
        selected_p_layers = st.multiselect("Select Visual Layers", p_layers, default=p_layers)

        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig, ax = pitch.draw(figsize=(11, 8))
        add_logo(ax)
        
        draw_actions(p_df, ax, pitch, selected_p_layers)
        
        ax.legend(handles=get_full_legend(), loc='upper right', fontsize='x-small', framealpha=0.8, bbox_to_anchor=(1, 1))
        st.pyplot(fig)

    # --- TAB 2: Team ---
    with tab2:
        col1, col2 = st.columns(2)
        with col2:
            team_layers = ["Passes", "Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Goals"]
            selected_t_layers = st.multiselect("Team Tactical Layers", team_layers, default=["Tackles", "Ground Duels", "Goals"])
        
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))
        add_logo(ax_t)

        draw_actions(team_df, ax_t, pitch_t, selected_t_layers)

        ax_t.legend(handles=get_full_legend(), loc='upper right', fontsize='x-small', framealpha=0.8, bbox_to_anchor=(1, 1))
        st.pyplot(fig_t)

else:
    st.info("👋 Please upload your CSV file to start analysis!")
