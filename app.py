import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# تحميل البيانات
st.sidebar.header("📁 DATA LOAD & ANALYSIS")
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel or CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df['Action'] = df['Action'].fillna('None').astype(str).str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    if all(col in df.columns for col in ['x1', 'y1', 'x2', 'y2']):
        df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80
        df['x2_scaled'], df['y2_scaled'] = df['x2'] * 120, df['y2'] * 80
        
        # 3. تصنيف الأكشن المحدث
        def classify(val):
            val = val.lower()
            if 'cross' in val or 'عرضية' in val: return "Cross"
            if 'corner' in val or 'ركنية' in val: return "Corner"
            if 'pass' in val or 'تمرير' in val: return "Pass"
            if 'shot' in val or 'تسديد' in val: return "Shot"
            if 'tackle' in val or 'تدخل' in val: return "Tackle"
            if 'interception' in val or 'قطع' in val: return "Interception"
            return "Other"

        df['Type'] = df['Action'].apply(classify)

        # 4. الفلترة
        players_list = ["All Players"] + sorted(df['Player'].dropna().astype(str).unique().tolist())
        selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players_list)
        
        all_types = sorted(df['Type'].unique().tolist())
        selected_actions = st.sidebar.multiselect("Select Actions:", options=all_types, default=all_types)
        
        temp_df = df if selected_player == "All Players" else df[df['Player'].astype(str) == selected_player]
        filtered_df = temp_df[temp_df['Type'].isin(selected_actions)]

        # 5. الرسم (الهيكل الذي طلبته)
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        ax.text(60, 40, selected_player, color='#D4AF37', fontsize=60, fontweight='bold', 
                ha='center', va='center', alpha=0.1, zorder=1)

        # قمنا بإضافة العرضيات (ذهبي) والركنيات (أزرق سماوي) هنا
        configs = {
            "Pass": {"color": "#00ffcc", "marker": None, "is_arrow": True},
            "Cross": {"color": "#FFD700", "marker": None, "is_arrow": True}, # ذهبي
            "Corner": {"color": "#00BFFF", "marker": "o", "is_arrow": False}, # أزرق
            "Shot": {"color": "#00ff00", "marker": "*", "is_arrow": False},
            "Tackle": {"color": "#ff00ff", "marker": "X", "is_arrow": False},
            "Interception": {"color": "#0000FF", "marker": "o", "is_arrow": False}
        }

        legend_elements = []
        for act in selected_actions:
            if act not in configs: continue
            cfg = configs[act]
            subset = filtered_df[filtered_df['Type'] == act]
            if subset.empty: continue
            
            if cfg.get("is_arrow"):
                pitch.arrows(subset['x_scaled'], subset['y_scaled'], subset['x2_scaled'], subset['y2_scaled'], 
                             color=cfg['color'], width=2, headwidth=4, headlength=4, ax=ax)
                legend_elements.append(Line2D([0], [0], color=cfg['color'], lw=2, label=act))
            else:
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color=cfg['color'], marker=cfg['marker'], s=150, ax=ax)
                legend_elements.append(Line2D([0], [0], marker=cfg['marker'], color='none', markeredgecolor=cfg['color'], 
                                              markerfacecolor=cfg['color'], label=act, markersize=10))

        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, facecolor='#222222', labelcolor='white')
        st.pyplot(fig)
        plt.close(fig)
