import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Pro Analysis Dashboard")

# تحميل البيانات
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    df['x_s'], df['y_s'] = df['x1'] * 120, df['y1'] * 80
    
    # 1. تصنيف التسديدات والالتحامات بالتفصيل
    def classify_action(row):
        act = str(row['Action']).lower()
        tags = str(row['Tags']).lower()
        
        if 'shot' in act or 'تسديد' in act:
            if 'block' in tags: return "Shot: Blocked"
            if 'on target' in tags: return "Shot: On Target"
            return "Shot: Off Target"
        
        if 'aerial' in act or 'ground' in act or 'duel' in act or 'هوائي' in act or 'ارضي' in act:
            if 'success' in tags or 'won' in tags: return "Duel: Successful"
            return "Duel: Failed"
            
        return "Other"

    df['Detailed_Type'] = df.apply(classify_action, axis=1)

    # 2. الفلترة
    players = ["All Players"] + sorted(df['Player'].dropna().unique().tolist())
    selected_player = st.sidebar.selectbox("👤 PLAYER:", players)
    
    # 3. الرسم
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
    pitch.draw(ax=ax)
    
    # ألوان ورموز دقيقة
    colors = {
        "Shot: On Target": "#00ff00", "Shot: Off Target": "#ff3366", "Shot: Blocked": "#ff9900",
        "Duel: Successful": "#3399ff", "Duel: Failed": "#888888"
    }
    markers = {
        "Shot: On Target": "*", "Shot: Off Target": "o", "Shot: Blocked": "x",
        "Duel: Successful": "^", "Duel: Failed": "v"
    }

    filtered_df = df if selected_player == "All Players" else df[df['Player'] == selected_player]

    for type_name, color in colors.items():
        sub = filtered_df[filtered_df['Detailed_Type'] == type_name]
        if not sub.empty:
            pitch.scatter(sub['x_s'], sub['y_s'], color=color, marker=markers[type_name], s=150, ax=ax, label=type_name)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5, facecolor='#222222', labelcolor='white')
    st.pyplot(fig)
