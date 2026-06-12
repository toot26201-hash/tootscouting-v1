import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Full Tactical Report")

uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    # تحويل الإحداثيات
    df['x_s'], df['y_s'] = df['x1'] * 120, df['y1'] * 80
    df['x2_s'], df['y2_s'] = df['x2'] * 120, df['y2'] * 80
    
    # 1. فلتر اللاعبين
    players = ["All Players"] + sorted(df['Player'].dropna().unique().tolist())
    selected_player = st.sidebar.selectbox("👤 PLAYER:", players)
    
    # 2. الفلترة الأساسية
    filtered_df = df if selected_player == "All Players" else df[df['Player'] == selected_player]
    
    # 3. قائمة اختيار الأكشن بناءً على ما هو موجود فعلياً في الملف (مستحيل يمسح حاجة)
    available_actions = sorted(filtered_df['Action'].dropna().unique().tolist())
    selected_actions = st.sidebar.multiselect("Select Actions:", options=available_actions, default=available_actions)
    
    filtered_df = filtered_df[filtered_df['Action'].isin(selected_actions)]

    # 4. الرسم
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
    pitch.draw(ax=ax)
    fig.patch.set_facecolor('#1a1a1a')
    
    # قاموس مرن للألوان (إذا وجد أكشن غير معروف، سيعطيه لوناً افتراضياً)
    def get_config(action_name):
        act = str(action_name).lower()
        if 'pass' in act: return {'color': '#00ffcc', 'marker': None, 'is_arrow': True}
        if 'cross' in act: return {'color': '#ffff00', 'marker': 'v'}
        if 'shot' in act: return {'color': '#00ff00', 'marker': '*'}
        if 'corner' in act: return {'color': '#00f0ff', 'marker': 'D'}
        if 'tackle' in act or 'extra' in act: return {'color': '#ff00ff', 'marker': 'X'}
        if 'clearance' in act: return {'color': '#ffffff', 'marker': 's'}
        if 'interception' in act: return {'color': '#FFD700', 'marker': 'P'}
        return {'color': '#ff3300', 'marker': 'o'} # افتراضي

    legend_elements = []
    for act in selected_actions:
        cfg = get_config(act)
        sub = filtered_df[filtered_df['Action'] == act]
        if sub.empty: continue
        
        if cfg.get('is_arrow'):
            pitch.arrows(sub['x_s'], sub['y_s'], sub['x2_s'], sub['y2_s'], color=cfg['color'], width=2, ax=ax)
        else:
            pitch.scatter(sub['x_s'], sub['y_s'], color=cfg['color'], marker=cfg['marker'], s=150, ax=ax)
            
        legend_elements.append(Line2D([0], [0], marker=cfg.get('marker', 'o'), color='none', 
                                     markerfacecolor=cfg['color'], label=act, markersize=10))

    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, facecolor='#222222', labelcolor='white')
    st.pyplot(fig)
