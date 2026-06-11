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
plot_placeholder.pyplot(fig)
plt.close(fig)

# 2. تحميل البيانات
uploaded_file = st.sidebar.file_uploader("Upload Data", type=["csv", "xlsx"])
if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    # تحويل الإحداثيات
    df['x1'], df['y1'] = df['x1'] * 120, df['y1'] * 80
    df['x2'], df['y2'] = df['x2'] * 120, df['y2'] * 80
    
    # 3. محرك التصنيف
    conds = [
        df['Action'].str.contains('Pass|تمرير', case=False),
        df['Action'].str.contains('Aerial|Air|هوائي', case=False),
        df['Action'].str.contains('Tackle|تدخل', case=False),
        df['Action'].str.contains('Goal|Shot|تسديد', case=False),
        df['Action'].str.contains('Clearance|تشتيت', case=False)
    ]
    choices = ["Pass", "Aerial Duel", "Tackle", "Goal/Shot", "Clearance"]
    df['Type'] = np.select(conds, choices, default="Other")

    # 4. إعداد الألوان والرموز (دليل ثابت في الكود)
    action_configs = {
        "Pass": {"color": "#00ffcc", "marker": None, "is_arrow": True},
        "Aerial Duel": {"color": "#3399ff", "marker": "^", "is_arrow": False},
        "Tackle": {"color": "#ff00ff", "marker": "X", "is_arrow": False},
        "Goal/Shot": {"color": "#00ff00", "marker": "*", "is_arrow": False},
        "Clearance": {"color": "#ffffff", "marker": "s", "is_arrow": False}
    }

    # 5. الرسم
    fig, ax = plt.subplots(figsize=(12, 9))
    pitch.draw(ax=ax)
    fig.patch.set_facecolor('#1a1a1a')
    
    legend_handles = []

    for action, cfg in action_configs.items():
        subset = df[df['Type'] == action]
        if subset.empty: continue
            
        if cfg["is_arrow"]:
            pitch.arrows(subset['x1'], subset['y1'], subset['x2'], subset['y2'], color=cfg['color'], width=2, ax=ax)
            legend_handles.append(Line2D([0], [0], color=cfg['color'], lw=2, label="Pass"))
        else:
            pitch.scatter(subset['x1'], subset['y1'], color=cfg['color'], marker=cfg['marker'], s=150, ax=ax)
            legend_handles.append(Line2D([0], [0], marker=cfg['marker'], color='none', markerfacecolor=cfg['color'], label=action, markersize=10))

    # إضافة الدليل للكود
    ax.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, -0.05), 
              ncol=5, facecolor='#222222', labelcolor='white', fontsize=12)
    
    plot_placeholder.pyplot(fig)
    plt.close(fig)
