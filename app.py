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
        
        # 3. تصنيف الأكشن المحدث (يشمل المرواغات)
        def classify(val):
            val = val.lower()
            if 'pass' in val or 'تمرير' in val: return "Pass"
            if 'shot' in val or 'تسديد' in val: return "Shot"
            if 'tackle' in val or 'تدخل' in val or 'extra' in val: return "Tackle"
            if 'clearance' in val or 'تشتيت' in val or 'تخليص' in val: return "Clearance"
            if 'interception' in val or 'قطع' in val or 'اعتراض' in val: return "Interception"
            if 'aerial' in val or 'هوائي' in val: return "Aerial Duel"
            if 'ground' in val or 'أرضي' in val: return "Ground Duel"
            if 'foul' in val or 'خطأ' in val: return "Foul"
            if 'counter' in val or 'ضغط' in val: return "Counterpress"
            # إضافة تصنيف المرواغات
            if 'dribble' in val or 'مرواغة' in val or 'اختراق' in val: return "Dribble"
            return "Other"

        df['Type'] = df['Action'].apply(classify)

        # 4. الفلترة
        players_list = ["All Players"] + sorted(df['Player'].dropna().astype(str).unique().tolist())
        selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players_list)
        
        # ترتيب الأكشنات ليظهر الجديد في القائمة
        all_types = sorted(df['Type'].unique().tolist())
        selected_actions = st.sidebar.multiselect("Select Actions:", options=all_types, default=all_types)
        
        temp_df = df if selected_player == "All Players" else df[df['Player'].astype(str) == selected_player]
        filtered_df = temp_df[temp_df['Type'].isin(selected_actions)]

        # 5. الرسم
        fig, ax = plt.subplots(figsize=(12, 9))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        ax.text(60, 40, selected_player, color='#D4AF37', fontsize=60, fontweight='bold', 
                ha='center', va='center', alpha=0.1, zorder=1)

        # إضافة إعداد المرواغة (Dribble)
        configs = {
            "Pass": {"color": "#00ffcc", "marker": None, "is_arrow": True},
            "Aerial Duel": {"color": "#3399ff", "marker": "^"},
            "Tackle": {"color": "#ff00ff", "marker": "X"},
            "Shot": {"color": "#00ff00", "marker": "*"},
            "Clearance":
