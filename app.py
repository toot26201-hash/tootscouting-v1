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

# 2. Sidebar
st.sidebar.header("📁 DATA LOAD & ANALYSIS")
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    if all(col in df.columns for col in ['x1', 'y1', 'x2', 'y2']):
        df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80
        df['x2_scaled'], df['y2_scaled'] = df['x2'] * 120, df['y2'] * 80
        
        # 3. الفلترة
        players_list = ["All Players"] + sorted(df['Player'].dropna().unique().tolist())
        selected_player = st.sidebar.selectbox("👤 PLAYER:", players_list)
        all_actions = sorted(df['Action'].dropna().unique().tolist())
        selected_actions = st.sidebar.multiselect("Select Actions:", options=all_actions, default=all_actions)
        
        temp_df = df if selected_player == "All Players" else df[df['Player'] == selected_player]
        filtered_df = temp_df[temp_df['Action'].isin(selected_actions)]

        # 4. الرسم
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        # اسم اللاعب كعلامة مائية
        ax.text(60, 40, selected_player, color='#D4AF37', fontsize=60, fontweight='bold', 
                ha='center', va='center', alpha=0.15, zorder=1)

        # 5. حلقة الرسم مع الدليل (Legend)
        legend_elements = []
        drawn_actions = set()

        for act in selected_actions:
            subset = filtered_df[filtered_df['Action'] == act]
            if subset.empty: continue
            
            # تحديد الخصائص (لون ورمز)
            act_lower = act.lower()
            if 'pass' in act_lower:
                c, m, is_arrow = '#00ffcc', None, True
            elif 'shot' in act_lower:
                c, m, is_arrow = '#00ff00', '*', False
            elif 'interception' in act_lower or 'قطع' in act_lower:
                c, m, is_arrow = '#FFFF00', 'P', False
            else:
                c, m, is_arrow = '#ff9900', 'o', False
            
            # الرسم
            if is_arrow:
                pitch.arrows(subset['x_scaled'], subset['y_scaled'], subset['x2_scaled'], subset['y2_scaled'], color=c, width=2, ax=ax)
            else:
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color=c, marker=m, s=150, ax=ax)
            
            # إضافة الدليل
            if act not in drawn_actions:
                legend_elements.append(Line2D([0], [0], marker=m if not is_arrow else None, color='none', 
                                             markerfacecolor=c, label=act, markersize=10, linewidth=2 if is_arrow else 0))
                drawn_actions.add(act)

        # إظهار الدليل
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), 
                  ncol=4, facecolor='#222222', labelcolor='white', fontsize=10)

        plot_placeholder.pyplot(fig)
        plt.close(fig)
