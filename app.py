import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
from PIL import Image

# 1. إعدادات الصفحة واللوجو
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
    
    # تحويل الإحداثيات
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

    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#2ecc71', marker='>', label='Pass Success'),
            mlines.Line2D([], [], color='blue', marker='x', label='Tackle (Blue X)', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='purple', marker='d', label='Clearance', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#2ecc71', marker='s', label='Ground Duel Won', linestyle='None'),
            mlines.Line2D([], [], color='red', marker='s', label='Ground Duel Lost', linestyle='None'),
            mlines.Line2D([], [], color='gold', marker='*', label='Goal', linestyle='None', markersize=12)
        ]

    # --- TAB 1: التحليل الفردي ---
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        # عرض الأكشنز المتاحة فعلياً في ملفك
        available_actions = sorted(p_df['Action'].unique().tolist())
        p_actions = st.multiselect("Player Visuals", available_actions, default=available_actions)
        p_filt = p_df[p_df['Action'].isin(p_actions)]

        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig, ax = pitch.draw(figsize=(11, 8))
        add_logo(ax)

        for i, row in p_filt.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag
            
            # منطق التدخلات (Tackles & Interceptions)
            if 'tackle' in act or 'inter' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, color='blue', linewidth=3, ax=ax)
            
            # منطق التشتيت (Clearances)
            elif 'clear' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='d', s=200, color='purple', ax=ax)
            
            # الالتحامات الأرضية (Ground Duels)
            elif 'duel' in act and 'aerial' not in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color='#2ecc71' if is_success else 'red', ax=ax)
            
            # باقي الأكشنز (تمريرات، أهداف...)
            elif 'pass' in act:
                pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax)
            elif 'goal' in tag:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax, zorder=5)

        ax.legend(handles=get_full_legend(), loc='upper right', fontsize='x-small')
        st.pyplot(fig)

    # --- TAB 2: التحليل الجماعي ---
    with tab2:
        col1, col2 = st.columns(2)
        with col2:
            # التأكد من كتابة الخيارات بالظبط كما في منطق الرسم
            d_opt = st.multiselect("Defense & Attack Layers", 
                                  ["Tackles", "Clearances", "Ground Duels", "Goals"], 
                                  default=["Tackles", "Ground Duels"])
        
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))
        add_logo(ax_t)

        for i, row in team_df.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag

            if "Tackles" in d_opt and ('tackle' in act or 'inter' in act):
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='x', s=180, color='blue', linewidth=2, ax=ax_t)
            
            if "Clearances" in d_opt and 'clear' in act:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='d', s=150, color='purple', ax=ax_t)
                
            if "Ground Duels" in d_opt and 'duel' in act and 'aerial' not in act:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='s', s=120, color='#2ecc71' if is_success else 'red', ax=ax_t)
            
            if "Goals" in d_opt and "goal" in tag:
                pitch_t.scatter(row.x_scaled, row.y_scaled, marker='*', s=800, color='gold', ax=ax_t, zorder=6)

        ax_t.legend(handles=get_full_legend(), loc='upper right', fontsize='x-small')
        st.pyplot(fig_t)
