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
    
    # تحويل الإحداثيات (ضرب في أبعاد الملعب 120x80)
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    df = df.dropna(subset=['Action', 'Team'])
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    tab1, tab2 = st.tabs(["👤 التحليل الفردي", "👥 التحليل الجماعي"])

    # دالة موحدة للدليل (Legend) لضمان ظهور الرموز
    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#2ecc71', marker='>', label='تمريرة ناجحة', linestyle='-', markersize=8),
            mlines.Line2D([], [], color='blue', marker='x', label='تدخل (Tackle) - X أزرق', linestyle='None', markersize=10, markeredgewidth=2),
            mlines.Line2D([], [], color='purple', marker='d', label='تشتيت (Clearance)', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#2ecc71', marker='s', label='التحام أرضي ناجح', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='red', marker='s', label='التحام أرضي فاشل', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#2ecc71', marker='^', label='التحام هوائي ناجح', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='red', marker='^', label='التحام هوائي فاشل', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='gold', marker='*', label='هدف', linestyle='None', markersize=12)
        ]

    # --- الجزء المشترك لمنطق الرسم ---
    def draw_actions(dataframe, ax, pitch_obj, selected_layers):
        for i, row in dataframe.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'ناجح' in tag
            
            # 1. التدخلات (Tackles / Interceptions)
            if any(word in act for word in ['tackle', 'inter', 'تدخل', 'قطع']):
                if "Tackles" in selected_layers or "تدخلات" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=250, color='blue', linewidth=3, ax=ax)
            
            # 2. التشتيت (Clearances)
            elif any(word in act for word in ['clear', 'تشتيت']):
                if "Clearances" in selected_layers or "تشتيت" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='d', s=200, color='purple', ax=ax)
            
            # 3. الالتحام الهوائي (Aerial Duels)
            elif any(word in act for word in ['aerial', 'هوائي']):
                if "Aerial Duels" in selected_layers or "التحام هوائي" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='^', s=250, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax)
            
            # 4. الالتحام الأرضي (Ground Duels)
            elif any(word in act for word in ['duel', 'ground', 'التحام', 'صراع']) and 'aerial' not in act:
                if "Ground Duels" in selected_layers or "التحام أرضي" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color='#2ecc71' if is_success else 'red', ax=ax)
            
            # 5. التمريرات
            elif 'pass' in act or 'تمرير' in act:
                if "Passes" in selected_layers or "تمريرات" in selected_layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.6)

            # 6. الأهداف
            if 'goal' in tag or 'هدف' in tag:
                if "Goals" in selected_layers or "أهداف" in selected_layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax, zorder=5)

    # --- TAB 1: التحليل الفردي ---
    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("اختر اللاعب", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        # ليرات الفردي
        p_layers = ["Passes", "Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Goals"]
        selected_p_layers = st.multiselect("اختر ماذا تريد أن ترى على الملعب", p_layers, default=p_layers)

        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig, ax = pitch.draw(figsize=(11, 8))
        add_logo(ax)
        
        draw_actions(p_df, ax, pitch, selected_p_layers)
        
        ax.legend(handles=get_full_legend(), loc='upper right', fontsize='small', framealpha=0.8)
        st.pyplot(fig)

    # --- TAB 2: التحليل الجماعي ---
    with tab2:
        col1, col2 = st.columns(2)
        with col2:
            team_layers = ["Passes", "Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Goals"]
            selected_t_layers = st.multiselect("طبقات التحليل الجماعي", team_layers, default=["Tackles", "Ground Duels", "Goals"])
        
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b', linestyle='--')
        fig_t, ax_t = pitch_t.draw(figsize=(12, 9))
        add_logo(ax_t)

        draw_actions(team_df, ax_t, pitch_t, selected_t_layers)

        ax_t.legend(handles=get_full_legend(), loc='upper right', fontsize='small', framealpha=0.8)
        st.pyplot(fig_t)

else:
    st.info("👋 ارفع ملف الـ CSV عشان نبدأ التحليل يا بطل!")
