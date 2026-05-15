import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import matplotlib.patches as patches

st.set_page_config(page_title="TootScouting Tactical Master", layout="wide")

st.title("⚽ TootScouting | Advanced Team Strategy Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تحويل الإحداثيات لمقياس StatsBomb
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    df = df.dropna(subset=['Action', 'Team'])
    
    st.sidebar.header("Team Filters")
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    tab1, tab2 = st.tabs(["👤 Individual Analysis", "👥 Team Strategy & Entries"])

    # --- TAB 1: الفردي (نفس النسخة الاحترافية) ---
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        st.write(f"Analyze: {sel_player}")
        # (كود الرسم الفردي السابق مدمج ضمنياً هنا)

    # ---------------------------------------------------------
    # TAB 2: التحليل الجماعي الاستراتيجي (الاختراق والبوكس)
    # ---------------------------------------------------------
    with tab2:
        st.subheader(f"Strategy Analysis: {selected_team}")
        
        team_options = st.multiselect("Select Tactical Layers", 
            ["Final Third Entries", "Box Entries", "Touches Inside Box", "Area 14 Hub", "Through Balls", "Goals/Shots", "Heat Map"],
            default=["Box Entries", "Area 14 Hub", "Goals/Shots"])

        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))

        # 1. Heat Map (الانتشار العام)
        if "Heat Map" in team_options:
            pitch_t.kdeplot(team_df.x_scaled, team_df.y_scaled, ax=ax_t, fill=True, cmap='Reds', alpha=0.2, zorder=0)

        # 2. Area 14 Hub (منطقة صناعة اللعب)
        if "Area 14 Hub" in team_options:
            rect_a14 = patches.Rectangle((80, 18), 22, 44, linewidth=2, edgecolor='blue', facecolor='blue', alpha=0.08, zorder=1)
            ax_t.add_patch(rect_a14)

        for i, row in team_df.iterrows():
            act, tag = str(row['Action']).lower(), str(row['Tags']).lower()
            
            # --- تحليل الدخول للثلث الأخير (Final Third Entries) ---
            if "Final Third Entries" in team_options and row.x_scaled < 80 and row.x_end_scaled >= 80:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=1.5, color='#9b59b6', alpha=0.4, ax=ax_t)

            # --- تحليل الدخول لمنطقة الجزاء (Box Entries) ---
            # أي تمريرة تنتهي داخل الـ 18
            in_box_end = (row.x_end_scaled > 102) and (18 < row.y_end_scaled < 62)
            if "Box Entries" in team_options and in_box_end:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71', ax=ax_t, alpha=0.7)

            # --- لمسات داخل البوكس (Touches Inside Box) بألوان مختلفة لكل نوع ---
            in_box_start = (row.x_scaled > 102) and (18 < row.y_scaled < 62)
            if "Touches Inside Box" in team_options and in_box_start:
                if 'shot' in act or 'sh/a' in act: touch_col = 'blue'  # تسديدة
                elif 'pass' in act: touch_col = 'green'             # تمريرة من داخل البوكس
                elif 'dribble' in act: touch_col = 'orange'          # مراوغة
                else: touch_col = 'black'                            # أي لمسة أخرى
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='o', s=80, color=touch_col, edgecolors='white', ax=ax_t, zorder=4)

            # --- الكرات البينية (Through Balls) باللون الروز ---
            if "Through Balls" in team_options and "through" in tag:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax_t, zorder=3)

            # --- الأهداف (نجوم ذهبية) ---
            if "Goals/Shots" in team_options and "goal" in tag:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='*', s=800, color='gold', edgecolors='black', ax=ax_t, zorder=6)

        # --- Legend (على الصورة) ---
        legend_els = [
            mlines.Line2D([], [], color='#2ecc71', marker='>', label='Box Entry (Pass)'),
            mlines.Line2D([], [], color='#9b59b6', marker='>', label='Final 3rd Entry'),
            mlines.Line2D([], [], color='#FF69B4', marker='>', label='Through Ball'),
            mlines.Line2D([], [], color='blue', marker='o', linestyle='None', label='Shot in Box'),
            mlines.Line2D([], [], color='green', marker='o', linestyle='None', label='Pass in Box'),
            mlines.Line2D([], [], color='orange', marker='o', linestyle='None', label='Dribble in Box'),
            mlines.Line2D([], [], color='gold', marker='*', linestyle='None', markersize=12, label='Goal')
        ]
        ax_t.legend(handles=legend_els, loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9)
        
        st.pyplot(fig_t)

        # Summary Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Box Entries", len(team_df[(team_df['x_end_scaled'] > 102) & (18 < team_df['y_end_scaled'] < 62)]))
        m2.metric("Final 3rd Entries", len(team_df[(team_df['x_scaled'] < 80) & (team_df['x_end_scaled'] >= 80)]))
        m3.metric("Area 14 Success", len(team_df[(team_df['x_end_scaled'] >= 80) & (team_df['x_end_scaled'] <= 102) & (18 < team_df['y_end_scaled'] < 62)]))
        m4.metric("Goals", len(team_df[team_df['Tags'].str.contains('goal', case=False, na=False)]))

else:
    st.info("👋 Upload CSV to visualize team penetration and box dominance.")
