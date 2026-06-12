import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 2. تحميل البيانات
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
        
        # تصنيف الأكشن
        def classify(val):
            val = val.lower()
            if 'pass' in val or 'تمرير' in val: return "Pass"
            if 'shot' in val or 'تسديد' in val: return "Shot"
            if 'tackle' in val or 'تدخل' in val or 'extra' in val: return "Tackle"
            if 'clearance' in val or 'تشتيت' in val: return "Clearance"
            if 'interception' in val or 'قطع' in val: return "Interception"
            if 'aerial' in val or 'هوائي' in val: return "Aerial Duel"
            if 'ground' in val or 'أرضي' in val: return "Ground Duel"
            if 'foul' in val or 'خطأ' in val: return "Foul"
            if 'counter' in val or 'ضغط' in val: return "Counterpress"
            if 'dribble' in val or 'مرواغة' in val: return "Dribble"
            if 'miscontrol' in val or 'سوء تحكم' in val: return "Miscontrol"
            if 'progressive' in val or 'تقدم' in val: return "Progressive Run"
            return "Other"

        df['Type'] = df['Action'].apply(classify)

        # 4. الفلترة
        players_list = ["All Players"] + sorted(df['Player'].dropna().astype(str).unique().tolist())
        selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players_list)
        all_types = sorted(df['Type'].unique().tolist())
        selected_actions = st.sidebar.multiselect("Select Actions:", options=all_types, default=all_types)
        
        st.sidebar.markdown("### 🗺️ DISPLAY OPTIONS")
        show_heatmap = st.sidebar.checkbox("Show Heatmap in Separate Pitch", value=False)
        
        temp_df = df if selected_player == "All Players" else df[df['Player'].astype(str) == selected_player]
        filtered_df = temp_df[temp_df['Type'].isin(selected_actions)]

        # 5. الرسم
        # ننشئ متغير لعدد الملاعب بناءً على اختيارك
        num_plots = 2 if show_heatmap else 1
        fig, axes = plt.subplots(1, num_plots, figsize=(12 * num_plots, 8))
        if num_plots == 1: axes = [axes]
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')

        # ملعب الأكشنات (دائماً يظهر)
        pitch.draw(ax=axes[0])
        fig.patch.set_facecolor('#1a1a1a')
        axes[0].set_title("Tactical Actions", color='white', fontsize=15)
        
        configs = {
            "Pass": {"color": "#00ffcc", "marker": None, "is_arrow": True},
            "Aerial Duel": {"color": "#3399ff", "marker": "^"},
            "Tackle": {"color": "#ff00ff", "marker": "X"},
            "Shot": {"color": "#00ff00", "marker": "*"},
            "Clearance": {"color": "#ffffff", "marker": "s"},
            "Interception": {"color": "#0000FF", "marker": "o"},
            "Ground Duel": {"color": "#8B4513", "marker": "v"},
            "Foul": {"color": "#ffcc00", "marker": "d"},
            "Counterpress": {"color": "#ff3300", "marker": "h"},
            "Dribble": {"color": "#A020F0", "marker": None, "is_arrow": True},
            "Miscontrol": {"color": "#8B0000", "marker": "x"},
            "Progressive Run": {"color": "#32CD32", "marker": None, "is_arrow": True}
        }

        for act in selected_actions:
            if act not in configs: continue
            cfg = configs[act]
            subset = filtered_df[filtered_df['Type'] == act]
            if subset.empty: continue
            if cfg.get("is_arrow"):
                pitch.arrows(subset['x_scaled'], subset['y_scaled'], subset['x2_scaled'], subset['y2_scaled'], color=cfg['color'], width=2, ax=axes[0])
            else:
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], color=cfg['color'] if act != "Interception" else 'none', 
                              edgecolors=cfg['color'] if act == "Interception" else None, marker=cfg['marker'], s=150, ax=axes[0])

        # ملعب الخريطة الحرارية (يظهر عند التفعيل)
        if show_heatmap and not filtered_df.empty:
            pitch.draw(ax=axes[1])
            axes[1].set_title("Activity Heatmap", color='white', fontsize=15)
            pitch.kdeplot(filtered_df['x_scaled'], filtered_df['y_scaled'], ax=axes[1], fill=True, levels=100, cmap='inferno', alpha=0.6)

        st.pyplot(fig)
        plt.close(fig)
