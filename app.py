import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

        players_list = ["All Players"] + sorted(df['Player'].dropna().astype(str).unique().tolist())
        selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players_list)
        all_types = sorted(df['Type'].unique().tolist())
        selected_actions = st.sidebar.multiselect("Select Actions:", options=all_types, default=all_types)
        
        temp_df = df if selected_player == "All Players" else df[df['Player'].astype(str) == selected_player]
        filtered_df = temp_df[temp_df['Type'].isin(selected_actions)]

        col1, col2 = st.columns(2)

        # دالة لإضافة العلامة المائية
        def add_watermark(ax, name):
            ax.text(60, 40, name, color='#D4AF37', fontsize=50, fontweight='bold', 
                    ha='center', va='center', alpha=0.15, zorder=1)

        # --- ملعب الأكشنات ---
        with col1:
            st.subheader("📍 Tactical Actions Map")
            fig1, ax1 = plt.subplots(figsize=(10, 7))
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
            pitch.draw(ax=ax1)
            fig1.patch.set_facecolor('#1a1a1a')
            
            # إضافة العلامة المائية
            add_watermark(ax1, selected_player)

            # رسم الأكشنات (تم التبسيط للسرعة)
            for _, row in filtered_df.iterrows():
                # تلوين الأكشن
                col = '#00ffcc' if 'pass' in row['Type'].lower() or 'dribble' in row['Type'].lower() else '#ffffff'
                if row['Type'] == 'Interception': col = '#0000FF'
                
                if 'pass' in row['Type'].lower() or 'dribble' in row['Type'].lower() or 'progressive' in row['Type'].lower():
                    pitch.arrows(row['x_scaled'], row['y_scaled'], row['x2_scaled'], row['y2_scaled'], color=col, width=2, ax=ax1)
                else:
                    pitch.scatter(row['x_scaled'], row['y_scaled'], color=col, s=100, ax=ax1)
            st.pyplot(fig1)

        # --- ملعب الخريطة الحرارية ---
        with col2:
            st.subheader("🔥 Activity Heatmap")
            fig2, ax2 = plt.subplots(figsize=(10, 7))
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
            pitch.draw(ax=ax2)
            fig2.patch.set_facecolor('#1a1a1a')
            
            # إضافة العلامة المائية
            add_watermark(ax2, selected_player)

            if not filtered_df.empty:
                pitch.kdeplot(filtered_df['x_scaled'], filtered_df['y_scaled'], ax=ax2, fill=True, levels=100, cmap='inferno', alpha=0.6)
            st.pyplot(fig2)
