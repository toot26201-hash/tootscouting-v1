import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. إعداد الملعب
fig, ax = plt.subplots(figsize=(12, 8))
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
pitch.draw(ax=ax)
fig.patch.set_facecolor('#1a1a1a')
plot_placeholder = st.empty()

# 2. Sidebar
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    df['x_s'], df['y_s'] = df['x1'] * 120, df['y1'] * 80
    
    # 3. التصنيف (تم التعديل للتمييز بين العرضيات، التسديدات، والكورنر)
    def classify(row):
        act = str(row['Action']).lower()
        if 'cross' in act or 'عرضية' in act: return "Cross"
        if 'shot' in act or 'تسديد' in act: return "Shot"
        if 'corner' in act or 'كورنر' in act: return "Corner"
        return "Other"
    
    df['Type'] = df.apply(classify, axis=1)

    # 4. اختيار اللاعبين والأكشن
    players = ["All Players"] + sorted(df['Player'].dropna().unique().tolist())
    selected_player = st.sidebar.selectbox("👤 PLAYER:", players)
    filtered_df = df if selected_player == "All Players" else df[df['Player'] == selected_player]

    # 5. الرسم مع تمييز الألوان
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch.draw(ax=ax)
    
    # تعريف الألوان والرموز لكل نوع
    type_configs = {
        "Cross": {"color": "#ffff00", "marker": "v"},  # أصفر
        "Shot": {"color": "#00ff00", "marker": "*"},   # أخضر
        "Corner": {"color": "#00f0ff", "marker": "D"}  # سماوي
    }

    for t, cfg in type_configs.items():
        sub = filtered_df[filtered_df['Type'] == t]
        if not sub.empty:
            pitch.scatter(sub['x_s'], sub['y_s'], color=cfg['color'], marker=cfg['marker'], s=200, ax=ax, label=t)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3, facecolor='#222222', labelcolor='white')
    plot_placeholder.pyplot(fig)
