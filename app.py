import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. إعداد الـ Sidebar
st.sidebar.header("📁 DATA LOAD & ANALYSIS")
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    # تحويل الإحداثيات
    df['x1'], df['y1'] = df['x1'] * 120, df['y1'] * 80
    df['x2'], df['y2'] = df['x2'] * 120, df['y2'] * 80
    
    # 2. التصنيف الشامل
    conds = [
        df['Action'].str.contains('Pass|تمرير', case=False) & ((df['x2']-df['x1']).abs() > 15), # تمريرات
        df['Action'].str.contains('Aerial|Air|هوائي', case=False), # التحام هوائي
        df['Action'].str.contains('Tackle|تدخل', case=False),
        df['Action'].str.contains('Shot|تسديد', case=False),
        df['Action'].str.contains('Clearance|تشتيت', case=False)
    ]
    choices = ["Pass", "Aerial Duel", "Tackle", "Shot", "Clearance"]
    df['Type'] = np.select(conds, choices, default="Other")

    # 3. الفلترة
    players = ["All Players"] + sorted(df['Player'].dropna().unique().tolist())
    selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players)
    
    # الفلترة الفعلية
    filtered_df = df if selected_player == "All Players" else df[df['Player'] == selected_player]
    
    # 4. الرسم
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
    pitch.draw(ax=ax)
    fig.patch.set_facecolor('#1a1a1a')
    
    # إضافة اسم اللاعب في منتصف الملعب
    ax.text(60, 40, selected_player, color='#D4AF37', fontsize=50, fontweight='bold', 
            ha='center', va='center', alpha=0.2, zorder=1)

    # رسم التمريرات (أسهم)
    passes = filtered_df[filtered_df['Type'] == "Pass"]
    pitch.arrows(passes['x1'], passes['y1'], passes['x2'], passes['y2'], 
                 color='#00ffcc', width=2, headwidth=4, headlength=4, ax=ax, label="Pass")
    
    # رسم باقي الأكشن (نقط)
    configs = {
        "Aerial Duel": {"color": "#3399ff", "marker": "^"},
        "Tackle": {"color": "#ff00ff", "marker": "X"},
        "Shot": {"color": "#00ff00", "marker": "*"},
        "Clearance": {"color": "#ffffff", "marker": "s"}
    }
    
    for t, cfg in configs.items():
        sub = filtered_df[filtered_df['Type'] == t]
        pitch.scatter(sub['x1'], sub['y1'], color=cfg['color'], marker=cfg['marker'], s=150, ax=ax, label=t)

    # الدليل
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5, 
              facecolor='#222222', labelcolor='white', fontsize=12)
    
    st.pyplot(fig)
