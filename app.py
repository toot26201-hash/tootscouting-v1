import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="TootScouting Professional", layout="wide")

st.title("⚽ TootScouting | Custom Tactical Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # Scaling to StatsBomb dimensions
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    st.sidebar.header("Analysis Filters")
    player_list = sorted(df['Player'].dropna().unique().tolist())
    selected_player = st.sidebar.selectbox("Select Player", player_list)
    player_df = df[df['Player'] == selected_player].copy()

    action_list = sorted(player_df['Action'].dropna().unique().tolist())
    selected_actions = st.sidebar.multiselect("Select Actions to Display", action_list, default=action_list[:3])

    filtered_df = player_df[player_df['Action'].isin(selected_actions)]

    tab1, tab2 = st.tabs(["📊 Table View", "🏟️ Professional Pitch"])

    with tab1:
        st.subheader(f"Data for: {selected_player}")
        st.dataframe(filtered_df)

    with tab2:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', 
                      linestyle='--', linewidth=1, goal_linestyle='-')
        fig, ax = pitch.draw(figsize=(12, 8))

        for i, row in filtered_df.iterrows():
            # Determine Color
            is_success = 'success' in str(row['Tags']).lower()
            color = '#2ecc71' if is_success else '#e74c3c'
            
            action = str(row['Action']).lower()

            # 1. Pass (Arrows)
            if 'pass' in action:
                if pd.notnull(row['x_end_scaled']):
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                                 width=2, color=color, ax=ax, alpha=0.6)

            # 2. Aerial Duels (Triangle)
            elif 'aerial' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='^', s=200, 
                              color=color, edgecolors='black', ax=ax)

            # 3. Ground Duels (Square)
            elif 'duel' in action or 'tackle' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='s', s=180, 
                              color=color, edgecolors='black', ax=ax)

            # 4. Extractions/Interceptions (X - الصدادة)
            elif 'extraction' in action or 'interception' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='x', s=200, 
                              linewidth=3, color=color, ax=ax)

            # 5. Dribble (Hollow Circle - الدائرة المفرغة)
            elif 'dribble' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='o', s=180, 
                              facecolors='none', edgecolors=color, linewidth=2, ax=ax)

            # 6. Ball Carry (Yellow Dashed Arrow)
            elif 'carry' in action or 'run' in action:
                if pd.notnull(row['x_end_scaled']):
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                                 width=2, color='#f1c40f', linestyle='--', ax=ax)

        st.pyplot(fig)
        
        # English Legend
        st.markdown("""
        ### **Tactical Key (English):**
        * ▲ **Triangle:** Aerial Duel (Green: Win / Red: Loss)
        * ■ **Square:** Ground Duel / Tackle (Green: Win / Red: Loss)
        * **X (Cross):** Interception / Extraction
        * ○ **Hollow Circle:** Dribble
        * **--- > (Yellow Dashed):** Ball Carry
        * **Solid Arrow:** Pass (Green: Success / Red: Failed)
        """)

else:
    st.info("👋 Upload the CSV file to generate the professional report.")
