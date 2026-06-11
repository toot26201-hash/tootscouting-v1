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

# 2. تحميل البيانات
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    # تحويل الإحداثيات
    df['x1'], df['y1'] = df['x1'] * 120, df['y1'] * 80
    df['x2'], df['y2'] = df['x2'] * 120, df['y2'] * 80
    
    # 3. التصنيف الشامل (هجومي ودفاعي)
    conds = [
        df['Action'].str.contains('Pass|تمرير', case=False) & ((df['x2']-df['x1']) > 20), # تمريرات تقدمية
        df['Action'].str.contains('Cross|عرضية', case=False),
        df['Action'].str.contains('Shot|تسديد', case=False),
        df['Action'].str.contains('Corner|كورنر', case=False),
        df['Action'].str.contains('Through|ثرو', case=False),
        df['Action'].str.contains('Dribble|مراوغة', case=False),
        df['Action'].str.contains('Tackle|تدخل', case=False),
        df['Action'].str.contains('Clearance|تشتيت', case=False),
        df['Action'].str.contains('Aerial|هوائي', case=False),
        df['Action'].str.contains('Ground|أرضي', case=False),
        df['Action'].str.contains('Foul|خطأ', case=False),
        df['Action'].str.contains('Counter|ضغط', case=False)
    ]
    choices = ["Prog. Pass", "Cross", "Shot", "Corner", "Through Ball", "Dribble", "Tackle", "Clearance", "Aerial Duel", "Ground Duel", "Foul", "Counterpress"]
    df['Type'] = np.select(conds, choices, default="Other")

    # 4. الفلترة
    all_actions = choices
    selected_actions = st.sidebar.multiselect("Select Actions to View:", options=all_actions, default=all_actions)
    filtered_df = df[df['Type'].isin(selected_actions)]

    # 5. الرسم (الأسهم للتحركات، النقط للالتحامات)
    fig, ax = plt.subplots(figsize=(12, 9))
    pitch.draw(ax=ax)
    fig.patch.set_facecolor('#1a1a1a')
    
    # إعدادات الألوان والرموز
    configs = {
        "Prog. Pass": {"color": "#ff9900", "marker": None, "is_arrow": True},
        "Cross": {"color": "#ffff00", "marker": None, "is_arrow": True},
        "Through Ball": {"color": "#cc00ff", "marker": None, "is_arrow": True},
        "Corner": {"color": "#00f0ff", "marker": None, "is_arrow": True},
        "Shot": {"color": "#00ff00", "marker": "*", "is_arrow": False},
        "Dribble": {"color": "#ffffff", "marker": "P", "is_arrow": False},
        "Tackle": {"color": "#ff00ff", "marker": "X", "is_arrow": False},
        "Clearance": {"color": "#aaaaaa", "marker": "s", "is_arrow": False},
        "Aerial Duel": {"color": "#3399ff", "marker": "^", "is_arrow": False},
        "Ground Duel": {"color": "#8B4513", "marker": "v", "is_arrow": False},
        "Foul": {"color": "#ffcc00", "marker": "d", "is_arrow": False},
        "Counterpress": {"color": "#ff3300", "marker": "h", "is_arrow": False}
    }

    legend_elements = []
    for act in selected_actions:
        cfg = configs[act]
        subset = filtered_df[filtered_df['Type'] == act]
        if subset.empty: continue
        
        if cfg["is_arrow"]:
            pitch.arrows(subset['x1'], subset['y1'], subset['x2'], subset['y2'], color=cfg['color'], width=2, headwidth=4, ax=ax)
            legend_elements.append(Line2D([0], [0], color=cfg['color'], lw=2, label=act))
        else:
            pitch.scatter(subset['x1'], subset['y1'], color=cfg['color'], marker=cfg['marker'], s=150, ax=ax)
            legend_elements.append(Line2D([0], [0], marker=cfg['marker'], color='none', markerfacecolor=cfg['color'], label=act, markersize=10))

    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=6, facecolor='#222222', labelcolor='white')
    plot_placeholder.pyplot(fig)
    plt.close(fig)
