import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

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
    player_list = sorted(df['Player'].dropna().unique().tolist())
    selected_player = st.sidebar.selectbox("Select Player", player_list)
    player_df = df[df['Player'] == selected_player].copy()

    action_list = sorted(player_df['Action'].dropna().unique().tolist())
    selected_actions = st.sidebar.multiselect("Select Actions to Display", action_list, default=action_list)

    filtered_df = player_df[player_df['Action'].isin(selected_actions)]

    tab1, tab2 = st.tabs(["📊 Data Table", "🏟️ Tactical Pitch"])

    with tab1:
        st.subheader(f"Detailed Stats for: {selected_player}")
        st.dataframe(filtered_df)

    with tab2:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', 
                      linestyle='--', linewidth=1, goal_linestyle='-')
        fig, ax = pitch.draw(figsize=(12, 8))

        for i, row in filtered_df.iterrows():
            tag_str = str(row['Tags']).lower()
            is_success = 'success' in tag_str or 'on target' in tag_str
            color = '#2ecc71' if is_success else '#e74c3c'
            
            action = str(row['Action']).lower()

            # 1. Passes (Solid Arrows)
            if 'pass' in action:
                if pd.notnull(row['x_end_scaled']):
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                                 width=2, color=color, ax=ax, alpha=0.6)

            # 2. Shots (Star Symbol ⭐)
            elif 'shot' in action or 'sh/a' in action:
                # Blue for On Target, Fuchsia for Off Target
                shot_color = '#0000FF' if 'on target' in tag_str else '#FF00FF'
                pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=350, 
                              color=shot_color, edgecolors='black', ax=ax, zorder=3)

            # 3. Aerial Duels (Triangle ▲)
            elif 'aerial' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='^', s=200, 
                              color=color, edgecolors='black', ax=ax)

            # 4. Ground Duels/Tackles (Square ■)
            elif 'duel' in action or 'tackle' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='s', s=180, 
                              color=color, edgecolors='black', ax=ax)

            # 5. Interceptions/Extractions (X - Cross)
            elif 'extraction' in action or 'interception' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='x', s=200, 
                              linewidth=3, color=color, ax=ax)

            # 6. Dribbles (Hollow Circle ○)
            elif 'dribble' in action:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='o', s=180, 
                              facecolors='none', edgecolors=color, linewidth=2, ax=ax)

            # 7. Ball Carries (Yellow Dashed Arrow)
            elif 'carry' in action or 'run' in action:
                if pd.notnull(row['x_end_scaled']):
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                                 width=2, color='#f1c40f', linestyle='--', ax=ax)

        st.pyplot(fig)
        
        # Comprehensive English Legend with Icons & Colors
        st.markdown("""
        ### **Tactical Map Legend:**
        ---
        #### **Shooting:**
        * ⭐ <span style='color:#0000FF'>**Blue Star:**</span> Shot ON Target
        * ⭐ <span style='color:#FF00FF'>**Fuchsia Star:**</span> Shot OFF Target
        
        #### **Passing & Movement:**
        * 🟢 **Green Arrow:** Successful Pass
        * 🔴 **Red Arrow:** Failed Pass
        * 🟡 **Yellow Dashed Arrow:** Ball Carry / Run
        
        #### **Defensive & Duels:**
        * ▲ **Triangle:** Aerial Duel (Green: Won / Red: Lost)
        * ■ **Square:** Ground Duel or Tackle (Green: Won / Red: Lost)
        * ✖ **Cross (X):** Interception or Extraction
        
        #### **Technical Actions:**
        * ○ **Hollow Circle:** Dribble (Green: Success / Red: Failed)
        ---
        """, unsafe_allow_html=True)

else:
    st.info("👋 Welcome! Please upload the actions CSV file to generate your professional tactical report.")
