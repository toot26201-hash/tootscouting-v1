import streamlit as st
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

        # --- بناء الدليل داخل الصورة (Legend) ناحية اليمين ---
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

        # loc='upper right' بتنقل الدليل لليمين
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1), 
                  fontsize='small', facecolor='white', framealpha=0.8, edgecolor='black')

        st.pyplot(fig)
        st.write("💡 *The legend is now positioned on the right side. Perfect for clarity!*")

else:
    st.info("👋 Upload your CSV file to generate the professional tactical map.")
