import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Professional Match Analysis")

# 1. إعداد الملعب
st.sidebar.header("📁 DATA LOAD & ANALYSIS")
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    df['x_s'], df['y_s'] = df['x1'] * 120, df['y1'] * 80
    
    # 2. تصنيف الأكشن الذكي (بما في ذلك Extra Actions)
    def classify_action(row):
        act = str(row['Action']).lower()
        tags = str(row['Tags']).lower() if 'Tags' in row else ""
        
        # تصنيف العرضيات والكورنر
        if 'cross' in act or 'عرضية' in act: return "Cross"
        if 'corner' in act or 'كورنر' in act: return "Corner"
        
        # تصنيف الـ Extra Actions (تشتيت، تدخل، اعتراض)
        if 'extra' in act or 'tackle' in act or 'تدخل' in act: return "Tackle"
        if 'clearance' in act or 'تشتيت' in act or 'تخليص' in act: return "Clearance"
        if 'interception' in act or 'قطع' in act or 'اعتراض' in act: return "Interception"
        
        # تصنيف التسديدات
        if 'shot' in act or 'تسديد' in act:
            if 'block' in tags: return "Shot: Blocked"
            if 'on target' in tags: return "Shot: On Target"
            return "Shot: Off Target"
        
        # تصنيف الالتحامات
        if 'aerial' in act or 'ground' in act or 'duel' in act:
            return "Duel: Successful" if ('success' in tags or 'won' in tags) else "Duel: Failed"
            
        return "Other"

    df['Detailed_Type'] = df.apply(classify_action, axis=1)

    # 3. الفلاتر
    players = ["All Players"] + sorted(df['Player'].dropna().unique().tolist())
    selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players)
    
    all_types = [t for t in df['Detailed_Type'].unique() if t != "Other"]
    selected_types = st.sidebar.multiselect("Select Actions:", options=all_types, default=all_types)
    
    filtered_df = df if selected_player == "All Players" else df[df['Player'] == selected_player]
    filtered_df = filtered_df[filtered_df['Detailed_Type'].isin(selected_types)]

    # 4. الرسم
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
    pitch.draw(ax=ax)
    fig.patch.set_facecolor('#1a1a1a')
    
    # إضافة اسم اللاعب كعلامة مائية
    ax.text(60, 40, selected_player, color='#D4AF37', fontsize=50, fontweight='bold', ha='center', va='center', alpha=0.1)

    # إعدادات الألوان والرموز
    configs = {
        "Cross": {"color": "#ffff00", "marker": "v"},
        "Corner": {"color": "#00f0ff", "marker": "D"},
        "Interception": {"color": "#FFD700", "marker": "*"},
        "Tackle": {"color": "#ff00ff", "marker": "X"},
        "Clearance": {"color": "#ffffff", "marker": "s"},
        "Shot: On Target": {"color": "#00ff00", "marker": "o"},
        "Shot: Off Target": {"color": "#ff3366", "marker": "o"},
        "Shot: Blocked": {"color": "#ff9900", "marker": "x"},
        "Duel: Successful": {"color": "#3399ff", "marker": "^"},
        "Duel: Failed": {"color": "#888888", "marker": "v"}
    }

    legend_elements = []
    for t in selected_types:
        if t in configs:
            sub = filtered_df[filtered_df['Detailed_Type'] == t]
            if not sub.empty:
                pitch.scatter(sub['x_s'], sub['y_s'], color=configs[t]['color'], marker=configs[t]['marker'], s=150, ax=ax)
                legend_elements.append(Line2D([0], [0], marker=configs[t]['marker'], color='none', markerfacecolor=configs[t]['color'], label=t, markersize=10))

    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, facecolor='#222222', labelcolor='white')
    st.pyplot(fig)
