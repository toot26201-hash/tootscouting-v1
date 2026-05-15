import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import matplotlib.patches as patches
from PIL import Image # مكتبة معالجة الصور

st.set_page_config(page_title="TootScouting Tactical Pro", layout="wide")

# تحميل لوجو TootScouting اللي إنت رفعته
try:
    logo = Image.open('image_deac96.png')
except:
    logo = None

st.title("⚽ TootScouting | Advanced Strategic Analytics")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تحويل الإحداثيات لمقياس StatsBomb (120x80)
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

    tab1, tab2 = st.tabs(["👤 Individual Analysis", "👥 Team Strategy & Logos"])

    # --- TAB 1: التحليل الفردي مع اللوجو ---
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--', linewidth=1, goal_linestyle='-')
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # إضافة اللوجو في نص الملعب (بشفافية بسيطة عشان مبيغطيش على الداتا)
        if logo:
            # الإحداثيات: [x_start, x_end, y_start, y_end] - السنتر هو (60, 40)
            ax.imshow(logo, extent=[45, 75, 25, 55], alpha=0.15, zorder=0)

        for i, row in p_df.iterrows():
            # (كود رسم الأكشنز الفردية هنا كما في النسخ السابقة)
            pass
            
        st.pyplot(fig)

    # --- TAB 2: التحليل الجماعي مع اللوجو في الدائرة المركزية ---
    with tab2:
        st.subheader(f"Strategy & Box Control: {selected_team}")
        
        team_options = st.multiselect("Tactical Layers", 
            ["Final Third Entries", "Box Entries", "Touches Inside Box", "Area 14 Hub", "Goals/Shots"],
            default=["Box Entries", "Area 14 Hub"])

        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--', linewidth=1, goal_linestyle='-')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))

        # إضافة لوجو TootScouting كـ Watermark في نص الملعب
        if logo:
            ax_t.imshow(logo, extent=[50, 70, 30, 50], alpha=0.2, zorder=0)

        # رسم الـ Area 14
        if "Area 14 Hub" in team_options:
            rect_a14 = patches.Rectangle((80, 18), 22, 44, linewidth=2, edgecolor='blue', facecolor='blue', alpha=0.05, zorder=1)
            ax_t.add_patch(rect_a14)

        for i, row in team_df.iterrows():
            act, tag = str(row['Action']).lower(), str(row['Tags']).lower()
            
            # (كود رسم الكروسات، الثرو بولز، ولمسات الصندوق الملونة هنا)
            # مثال لدخول البوكس:
            in_box_end = (row.x_end_scaled > 102) & (row.y_end_scaled > 18) & (row.y_end_scaled < 62)
            if "Box Entries" in team_options and in_box_end:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71', alpha=0.6, ax=ax_t)

        st.pyplot(fig_t)

else:
    st.info("👋 ارفع ملف الـ CSV عشان تظهر الخرائط وعليها اللوجو الخاص بك.")
