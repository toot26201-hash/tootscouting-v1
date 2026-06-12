import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. إعداد الملعب
def draw_pitch():
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
    pitch.draw(ax=ax)
    fig.patch.set_facecolor('#1a1a1a')
    return fig, ax, pitch

# 2. Sidebar
st.sidebar.header("📁 DATA LOAD & ANALYSIS")
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel or CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    # تنظيف عمود الأكشن لضمان قراءة صحيحة
    df['Action'] = df['Action'].astype(str).str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    if all(col in df.columns for col in ['x1', 'y1', 'x2', 'y2']):
        df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80
        df['x2_scaled'], df['y2_scaled'] = df['x2'] * 120, df['y2'] * 80
        
        # 3. التصنيف (تم تحسينه لضمان التقاط الكلمات)
        def get_type(row):
            act = str(row['Action']).lower()
            if any(x in act for x in ['pass', 'تمرير']): return "Pass"
            if any(x in act for x in ['interception', 'قطع', 'اعتراض']): return "Interception"
            if any(x in act for x in ['aerial', 'air', 'هوائي']): return "Aerial Duel"
            if any(x in act for x in ['tackle', 'تدخل']): return "Tackle"
            if any(x in act for x in ['shot', 'تسديد']): return "Shot"
            if any(x in act for x in ['clearance', 'تشتيت']): return "Clearance"
            if any(x in act for x in ['ground', 'أرضي']): return "Ground Duel"
            if any(x in act for x in ['foul', 'خطأ']): return "Foul"
            if any(x in act for x in ['counter', 'ضغط']): return "Counterpress"
            return "Other"

        df['Type'] = df.apply(get_type, axis=1)

        # 4. الفلترة
        players_list = ["All Players"] + sorted(df['Player'].dropna().unique().tolist())
        selected_player = st.sidebar.selectbox("👤 PLAYER:", players_list)
        choices = ["Pass", "Interception", "Aerial Duel", "Tackle", "Shot", "Clearance", "Ground Duel", "Foul", "Counterpress"]
        selected_actions = st.sidebar.multiselect("Select Actions:", options=choices, default=choices)
        
        temp_df = df if selected_player == "All Players" else df[df['Player'] == selected_player]
        filtered_df = temp_df[temp_df['Type'].isin(selected_actions)]

        # 5. الرسم
        fig, ax, pitch = draw_pitch()
        ax.text(60, 40, selected_player, color='#D4AF37', fontsize=50, fontweight='bold', ha='center', va='center', alpha=0.1)

        configs = {
            "Pass": {"color": "#00ffcc", "marker": None, "is_arrow": True},
            "Interception": {"color": "#FFFF00", "marker": "P"},
            "Aerial Duel": {"color": "#3399ff", "marker": "^"},
            "Tackle": {"color": "#ff00ff", "marker": "X"},
            "Shot": {"color": "#00ff00", "marker": "*"},
            "Clearance": {"color": "#ffffff", "marker": "s"},
            "Ground Duel": {"color": "#8B4513", "marker": "v"},
            "Foul": {"color": "#ffcc00", "marker": "d"},
            "Counterpress": {"color": "#ff3300", "marker": "h"}
        }

        legend_elements = []
        for act in selected_actions:
            cfg = configs.get(act)
            if not cfg: continue
            
            subset = filtered_df[filtered_df['Type'] == act]
            if subset.empty: continue
            
            if cfg.get("is_arrow"):
                pitch.arrows(subset['x_scaled'], subset['y_scaled'], subset['x2_scaled'], subset['y2_scaled'], color=cfg['color'], width=2, ax=ax)
                legend_elements.append(Line2D([0], [0], color=cfg['color'], lw=2, label=act))
            else:
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color=cfg['color'], marker=cfg['marker'], s=150, ax=ax)
                legend_elements.append(Line2D([0], [0], marker=cfg['marker'], color='none', markerfacecolor=cfg['color'], label=act, markersize=10))

        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, facecolor='#222222', labelcolor='white')
        
        st.pyplot(fig)
