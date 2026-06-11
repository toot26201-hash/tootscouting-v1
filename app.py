import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. Pitch Setup
fig, ax = plt.subplots(figsize=(12, 8))
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
pitch.draw(ax=ax)
fig.patch.set_facecolor('#1a1a1a')
plot_placeholder = st.empty()
plot_placeholder.pyplot(fig)
plt.close(fig)

# 2. Sidebar
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel or CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    if all(col in df.columns for col in ['x1', 'y1', 'x2', 'y2']):
        df['x1'], df['y1'] = df['x1'] * 120, df['y1'] * 80
        df['x2'], df['y2'] = df['x2'] * 120, df['y2'] * 80
        
        # التصنيف
        conds = [
            df['Action'].str.contains('Pass|تمرير', case=False),
            df['Action'].str.contains('Aerial|Air|هوائي', case=False),
            df['Action'].str.contains('Tackle|تدخل', case=False),
            df['Action'].str.contains('Goal|Shot', case=False)
        ]
        choices = ["Pass", "Aerial Duel", "Tackle", "Goal/Shot"]
        df['Type'] = np.select(conds, choices, default="Other")

        # الرسم
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')

        # 1. رسم التمريرات كأسهم
        passes = df[df['Type'] == "Pass"]
        pitch.arrows(passes['x1'], passes['y1'], passes['x2'], passes['y2'], 
                     color='#00ffcc', width=2, headwidth=4, headlength=4, ax=ax, label="Pass")
        
        # 2. رسم باقي الأكشن كنقط
        others = df[df['Type'] != "Pass"]
        colors = {"Aerial Duel": "#3399ff", "Tackle": "#ff00ff", "Goal/Shot": "#00ff00"}
        markers = {"Aerial Duel": "^", "Tackle": "X", "Goal/Shot": "*"}
        
        for t in ["Aerial Duel", "Tackle", "Goal/Shot"]:
            subset = others[others['Type'] == t]
            pitch.scatter(subset['x1'], subset['y1'], color=colors.get(t, 'white'), 
                          marker=markers.get(t, 'o'), s=150, ax=ax, label=t)

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, facecolor='#222222', labelcolor='white')
        plot_placeholder.pyplot(fig)
        plt.close(fig)
