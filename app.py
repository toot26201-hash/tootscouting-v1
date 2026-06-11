import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. إعداد الملعب (يظهر دائماً)
def draw_pitch():
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
    pitch.draw(ax=ax)
    fig.patch.set_facecolor('#1a1a1a')
    return fig, ax

# 2. Sidebar
st.sidebar.header("📁 DATA LOAD")
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

fig, ax = draw_pitch()
plot_placeholder = st.empty()
plot_placeholder.pyplot(fig)

if uploaded_file is not None:
    # قراءة الملف
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # التأكد من وجود الأعمدة
    required = ['Action', 'X Start', 'Y Start', 'X End', 'Y End']
    if all(col in df.columns for col in required):
        df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
        df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80
        df['x2_scaled'], df['y2_scaled'] = df['x2'] * 120, df['y2'] * 80
        
        # اختيار اللاعب
        player_col = 'Player' if 'Player' in df.columns else df.columns[0]
        players = ["All Players"] + sorted(df[player_col].dropna().unique().tolist())
        selected_player = st.sidebar.selectbox("👤 PLAYER:", players)
        
        temp_df = df if selected_player == "All Players" else df[df[player_col] == selected_player]
        
        # تصنيف الأكشن
        conds = [
            temp_df['Action'].str.contains('Pass|تمرير', case=False),
            temp_df['Action'].str.contains('Tackle|تدخل', case=False),
            temp_df['Action'].str.contains('Aerial|Air|هوائي', case=False),
            temp_df['Action'].str.contains('Shot|تسديد', case=False),
            temp_df['Action'].str.contains('Clearance|تشتيت', case=False)
        ]
        choices = ["Pass", "Tackle", "Aerial Duel", "Shot", "Clearance"]
        temp_df['Type'] = np.select(conds, choices, default="Other")
        
        # اختيار الأكشن
        selected_actions = st.sidebar.multiselect("Select Actions:", options=choices, default=choices)
        filtered_df = temp_df[temp_df['Type'].isin(selected_actions)]
        
        # الرسم
        fig, ax = draw_pitch()
        for act in selected_actions:
            sub = filtered_df[filtered_df['Type'] == act]
            if sub.empty: continue
            if act == "Pass":
                pitch.arrows(sub['x_scaled'], sub['y_scaled'], sub['x2_scaled'], sub['y2_scaled'], color='#00ffcc', ax=ax)
            else:
                pitch.scatter(sub['x_scaled'], sub['y_scaled'], s=150, ax=ax, label=act)
        
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5, facecolor='#222222', labelcolor='white')
        plot_placeholder.pyplot(fig)
    else:
        st.error(f"خطأ: الملف يجب أن يحتوي على الأعمدة: {required}")
