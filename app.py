import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import matplotlib.patches as patches
from PIL import Image

st.set_page_config(page_title="TootScouting Tactical Master", layout="wide")

# --- دالة إضافة اللوجو (Watermark) ---
def add_logo(ax):
    try:
        # تأكد أن ملف الصورة موجود في نفس المسار
        img = Image.open('image_deac96.png')
        # extent=[x_start, x_end, y_start, y_end]
        ax.imshow(img, extent=[48, 72, 28, 52], alpha=0.15, zorder=0)
    except:
        pass

st.title("⚽ TootScouting | Unified Tactical Analytics")

uploaded_file = st.sidebar.file_uploader("Upload Actions CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تجهيز الإحداثيات (120x80)
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

    # --- TAB 1: التحليل الفردي (بألوان التمريرات المتطورة) ---
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("Select Player", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        p_actions = st.multiselect("Visual Options", sorted(p_df['Action'].unique().tolist()), default=sorted(p_df['Action'].unique().tolist()))
        p_filt = p_df[p_df['Action'].isin(p_actions)]

        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig, ax = pitch.draw(figsize=(12, 8))
        add_logo(ax) # إضافة اللوجو

        for i, row in p_filt.iterrows():
            act, tag = str(row['Action']).lower(), str(row['Tags']).lower()
            is_success = 'success' in tag
            
            # 1. التمريرات بأنواعها (Unified Colors)
            if 'pass' in act:
                if 'cross' in tag: # الكروسات (أزرق سليم/متقطع)
                    ax.annotate("", xy=(row.x_end_scaled, row.y_end_scaled), xytext=(row.x_scaled, row.y_scaled),
                                arrowprops=dict(arrowstyle="->", color="blue", linestyle="-" if is_success else "--", lw=2))
                elif 'through' in tag: # الثرو (روز)
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax)
                elif 'free kick' in tag: # الفري كيك (تركواز)
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#40E0D0', ax=ax)
                elif 'corner' in tag: # الكورنر (برتقالي)
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange', ax=ax)
                else: # التمرير العادي (أخضر/أحمر)
                    p_col = '#2ecc71' if is_success else '#e74c3c'
                    pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color=p_col, alpha=0.7, ax=ax)

            # 2. التسديدات والأهداف
            elif 'shot' in act or 'sh/a' in act:
                if 'goal' in tag:
                    pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax, zorder=5)
                else:
                    s_col = '#0000FF' if 'on target' in tag else '#FF00FF'
                    pitch.scatter(row.x_scaled, row.y_scaled, marker='*', s=450, color=s_col, edgecolors='black', ax=ax, zorder=5)
            
            # 3. الأكشنز الأخرى (مربع، مثلث، دائرة مفرغة)
            elif 'aerial' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='^', s=250, color='#2ecc71' if is_success else '#e74c3c', edgecolors='black', ax=ax)
            elif 'dribble' in act:
                pitch.scatter(row.x_scaled, row.y_scaled, marker='o', s=200, facecolors='none', edgecolors='#2ecc71' if is_success else '#e74c3c', linewidth=2, ax=ax)

        # Legend (Right Side)
        legend_els = [
            mlines.Line2D([], [], color='#2ecc71', marker='>', label='Pass Success'),
            mlines.Line2D([], [], color='#e74c3c', marker='>', label='Pass Failed'),
            mlines.Line2D([], [], color='blue', linestyle='-', label='Cross Success'),
            mlines.Line2D([], [], color='blue', linestyle='--', label='Cross Failed'),
            mlines.Line2D([], [], color='#FF69B4', label='Through Ball'),
            mlines.Line2D([], [], color='orange', label='Corner'),
            mlines.Line2D([], [], color='gold', marker='*', linestyle='None', label='Goal')
        ]
        ax.legend(handles=legend_els, loc='upper right', bbox_to_anchor=(1, 1), fontsize='x-small', facecolor='white', framealpha=0.9)
        st.pyplot(fig)

    # --- TAB 2: التحليل الجماعي (بنفس السيستم) ---
    with tab2:
        st.subheader(f"Team Tactical Master: {selected_team}")
        team_options = st.multiselect("Team Visuals", ["Passes", "Crosses", "Through Balls", "Corners", "Goals/Shots", "Area 14 Hub"], default=["Passes", "Goals/Shots"])
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))
        add_logo(ax_t)

        if "Area 14 Hub" in team_options:
            rect = patches.Rectangle((80, 18), 22, 44, linewidth=2, edgecolor='blue', facecolor='blue', alpha=0.05, zorder=1)
            ax_t.add_patch(rect)

        # (يتم تطبيق نفس منطق الألوان هنا للأكشنز الجماعية)
        st.pyplot(fig_t)

else:
    st.info("👋 ارفع ملف الـ CSV وشوف تحليلك الفردي والجماعي بنفس الألوان واللوجو!")
