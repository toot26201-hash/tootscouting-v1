import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import matplotlib.patches as patches
from PIL import Image

# 1. إعدادات الصفحة واللوجو
st.set_page_config(page_title="TootScouting Ultimate Pro", layout="wide")

def add_logo(ax):
    try:
        img = Image.open('image_deac96.png')
        ax.imshow(img, extent=[48, 72, 28, 52], alpha=0.15, zorder=0)
    except:
        pass

st.title("⚽ TootScouting | Tactical Analysis Master")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
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

    # --- تحديث دليل الرموز ليعكس الألوان الجديدة ---
    def get_legend_elements():
        return [
            mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', label='Pass Success'),
            mlines.Line2D([], [], color='#e74c3c', marker='>', linestyle='-', label='Pass Failed'),
            mlines.Line2D([], [], color='blue', marker='>', linestyle='-', label='Cross Success'),
            mlines.Line2D([], [], color='red', marker='>', linestyle='--', label='Cross Failed'),
            mlines.Line2D([], [], color='orange', marker='>', linestyle='-', label='Corner Success'),
            mlines.Line2D([], [], color='red', marker='>', linestyle='--', label='Corner Failed'),
            mlines.Line2D([], [], color='#FF69B4', label='Through Ball'),
            mlines.Line2D([], [], color='gold', marker='*', linestyle='None', markersize=12, label='Goal'),
        ]

    # ---------------------------------------------------------
    # TAB 1: التحليل الفردي
    # ---------------------------------------------------------
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        p_actions = st.multiselect("Player Visuals", sorted(p_df['Action'].unique().tolist()), default=sorted(p_df['Action'].unique().tolist()))
        p_filt = p_df[p_df['Action'].isin(p_actions)]

        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig, ax = pitch.draw(figsize=(11, 8))
        add_logo(ax)

        for i, row in p_filt.iterrows():
            act, tag = str(row['Action']).lower(), str(row['Tags']).lower()
            is_success = 'success' in tag
            
            if 'pass' in act:
                # الكروسات: أزرق للصح / أحمر متقطع للغلط
                if 'cross' in tag:
                    p_color = 'blue' if is_success else 'red'
                    p_style = 'solid' if is_success else 'dashed'
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                                 width=2, color=p_color, linestyle=p_style, ax=ax)
                
                # الكورنر: برتقالي للصح / أحمر متقطع للغلط
                elif 'corner' in tag:
                    p_color = 'orange' if is_success else 'red'
                    p_style = 'solid' if is_success else 'dashed'
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                                 width=2, color=p_color, linestyle=p_style, ax=ax)
                
                elif 'through' in tag:
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax)
                else:
                    p_col = '#2ecc71' if is_success else '#e74c3c'
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color=p_col, alpha=0.7, ax=ax)
            
            elif 'shot' in act or 'sh/a' in act:
                if 'goal' in tag:
                    pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax, zorder=5)
                else:
                    s_col = '#0000FF' if 'on target' in tag else '#FF00FF'
                    pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=450, color=s_col, edgecolors='black', ax=ax, zorder=5)
        
        ax.legend(handles=get_legend_elements(), loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9)
        st.pyplot(fig)

    # ---------------------------------------------------------
    # TAB 2: التحليل الجماعي
    # ---------------------------------------------------------
    with tab2:
        st.subheader(f"Team Tactical Master: {selected_team}")
        team_options = st.multiselect("Tactical Layers", 
            ["Normal Passes", "Crosses", "Through Balls", "Goals/Shots", "Area 14 Hub"], 
            default=["Normal Passes", "Crosses", "Goals/Shots"])
        
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))
        add_logo(ax_t)

        if "Area 14 Hub" in team_options:
            rect_a14 = patches.Rectangle((80, 18), 22, 44, linewidth=2, edgecolor='blue', facecolor='blue', alpha=0.05, zorder=1)
            ax_t.add_patch(rect_a14)

        for i, row in team_df.iterrows():
            act, tag = str(row['Action']).lower(), str(row['Tags']).lower()
            is_success = 'success' in tag

            # الكروسات الجماعية
            if "Crosses" in team_options and "cross" in tag:
                p_color = 'blue' if is_success else 'red'
                p_style = 'solid' if is_success else 'dashed'
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                               width=2, color=p_color, linestyle=p_style, ax=ax_t)

            # التمريرات العادية
            if "Normal Passes" in team_options and "pass" in act and "cross" not in tag and "through" not in tag and "corner" not in tag:
                p_col = '#2ecc71' if is_success else '#e74c3c'
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=1.5, color=p_col, alpha=0.3, ax=ax_t)

            if "Through Balls" in team_options and "through" in tag:
                pitch_t.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax_t)

            if "Goals/Shots" in team_options:
                if "goal" in tag:
                    pitch_t.scatter(row.x_scaled, row.y_scaled, marker='*', s=800, color='gold', edgecolors='black', ax=ax_t, zorder=6)
                elif "shot" in act or "sh/a" in act:
                    s_col = '#0000FF' if 'on target' in tag else '#FF00FF'
                    pitch_t.scatter(row.x_scaled, row.y_scaled, marker='*', s=350, color=s_col, ax=ax_t, zorder=5)

        ax_t.legend(handles=get_legend_elements(), loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9)
        st.pyplot(fig_t)

else:
    st.info("👋 ارفع ملف الـ CSV.. دلوقتي الكروسات والرنيات الفاشلة باللون الأحمر المتقطع.")
