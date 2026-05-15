import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="TootScouting Analytics", layout="wide")

st.title("⚽ TootScouting | Advanced Performance Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Actions File (CSV)", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # Scale coordinates to StatsBomb dimensions (120x80)
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    st.sidebar.header("Filter Dashboard")
    
    # 1. Player Filter
    player_list = sorted(df['Player'].dropna().unique().tolist())
    selected_player = st.sidebar.selectbox("Select Player", player_list)
    player_df = df[df['Player'] == selected_player].copy()

    # 2. Action Filter
    action_list = sorted(player_df['Action'].dropna().unique().tolist())
    default_val = [a for a in ["Pass"] if a in action_list]
    selected_actions = st.sidebar.multiselect("Select Event Types", action_list, default=default_val)

    filtered_df = player_df[player_df['Action'].isin(selected_actions)]

    tab1, tab2 = st.tabs(["📊 Data Table", "🏟️ Tactical Pitch"])

    with tab1:
        st.subheader(f"Analysis for: {selected_player}")
        st.dataframe(filtered_df)

    with tab2:
        # WHITE PITCH with dashed lines
        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', 
                      linestyle='--', linewidth=1, goal_linestyle='-')
        fig, ax = pitch.draw(figsize=(12, 8))

        # Define Marker styles for different actions
        # (Pass uses arrows, others use markers)
        marker_map = {
            'Aerial': 'o',      # Circle
            'Dribble': 's',     # Square
            'Tackle': 'X',      # Cross
            'Foul': 'P',        # Plus
            'Interception': 'D', # Diamond
            'Pressing': '^'     # Triangle
        }

        # 1. Plot PASSES as Arrows
        passes = filtered_df[filtered_df['Action'].str.contains('Pass', case=False, na=False)]
        for i, row in passes.iterrows():
            if pd.notnull(row['x_end_scaled']):
                color = '#2ecc71' if 'success' in str(row['Tags']).lower() else '#e74c3c' # Green/Red
                pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                             width=2, headwidth=3, headlength=3, color=color, ax=ax, alpha=0.7)

        # 2. Plot OTHER ACTIONS with different markers
        others = filtered_df[~filtered_df['Action'].str.contains('Pass', case=False, na=False)]
        
        for action in selected_actions:
            if 'Pass' in action: continue
            
            action_data = others[others['Action'] == action]
            if not action_data.empty:
                marker = marker_map.get(action, 'o') # Use circle as default if action not in map
                pitch.scatter(action_data.x_scaled, action_data.y_scaled, s=150, 
                              edgecolors='black', facecolors='#3498db', marker=marker, 
                              ax=ax, label=action)

        if len(selected_actions) > 1 or 'Pass' not in selected_actions:
            ax.legend(facecolor='white', handlelength=2, edgecolor='black', fontsize=10, loc='upper left')

        st.pyplot(fig)
        
        # Legend Description in English
        st.markdown("""
        ### **Legend Key:**
        * **Green Arrow:** Successful Pass
        * **Red Arrow:** Failed Pass
        * **Markers:** Represents different event types (see legend on pitch)
        """)

else:
    st.info("👋 Please upload an Actions CSV file to start the tactical analysis.")
