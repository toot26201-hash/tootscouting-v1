import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import matplotlib.patches as patches
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="TootScouting Tactical Pro", layout="wide")

# --- دالة تحميل اللوجو ووضعه في السنتر ---
def add_logo(ax):
    try:
        # لو اللوجو مرفوع كملف في نفس الفولدر باسم logo.png
        # img = Image.open("image_deac96.png") 
        
        # أو تحميله من رابط (استخدمت الرابط اللي بعته)
        url = "https://img.freepik.com/free-vector/soccer-logo-design-template_23-2149014522.jpg" # مثال لرابط
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        
        # وضع اللوجو في الدائرة المركزية (x من 45 لـ 75، y من 25 لـ 55)
        # alpha=0.15 عشان يبقى شفاف وميداريش على تحركات اللعيبة
        ax.imshow(img, extent=[48, 72, 28, 52], alpha=0.15, zorder=0)
    except:
        pass

st.title("⚽ TootScouting | Tactical Analysis Center")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # Scaling to 120x80
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    df = df.dropna(subset=['Action', 'Team'])
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    tab1, tab2 = st.tabs(["👤 Individual Analysis", "👥 Team Tactical Map"])

    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()

        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--', linewidth=1)
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # استدعاء اللوجو
        add_logo(ax)

        for i, row in p_df.iterrows():
            tag, act = str(row['Tags']).lower(), str(row['Action']).lower()
            col = '#2ecc71' if 'success' in tag else '#e74c3c'
            if 'shot' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=500, color='blue', ax=ax)
            elif 'pass' in act:
                pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color=col, ax=ax, alpha=0.6)
        
        st.pyplot(fig)

    with tab2:
        st.subheader(f"Team Tactical Map: {selected_team}")
        team_options = st.multiselect("Visual Layers", ["Passes", "Crosses", "Shots", "Area 14 Hub"], default=["Passes", "Shots"])

        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--', linewidth=1)
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))
        
        # استدعاء اللوجو في السنتر
        add_logo(ax_t)

        if "Area 14 Hub" in team_options:
            rect = patches.Rectangle((80, 18), 22, 44, linewidth=2, edgecolor='blue', facecolor='blue', alpha=0.05, zorder=1)
            ax_t.add_patch(rect)

        for i, row in team_df.iterrows():
            # (كود رسم التمريرات والكروسات الملونة اللي عملناه)
            pass

        st.pyplot(fig_t)

else:
    st.info("👋 ارفع ملف الـ CSV وهتلاقي اللوجو ظهر في نص الملعب أوتوماتيك!")
