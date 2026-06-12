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
        
        temp_df = df if selected_player == "All Players" else df[df['Player'].astype(str) == selected_player]
        filtered_df = temp_df[temp_df['Type'].isin(selected_actions)]

        col1, col2 = st.columns(2)

        # --- ملعب الأكشنات (في العمود الأول) ---
        with col1:
            st.subheader("📍 Tactical Actions Map")
            fig1, ax1 = plt.subplots(figsize=(10, 7))
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
            pitch.draw(ax=ax1)
            fig1.patch.set_facecolor('#1a1a1a')
            
            for index, row in filtered_df.iterrows():
                # رسم الأكشن
                if 'pass' in row['Type'].lower() or 'dribble' in row['Type'].lower() or 'progressive' in row['Type'].lower():
                    pitch.arrows(row['x_scaled'], row['y_scaled'], row['x2_scaled'], row['y2_scaled'], color='#00ffcc', width=2, ax=ax1)
                else:
                    color = '#0000FF' if row['Type'] == "Interception" else '#ffffff'
                    pitch.scatter(row['x_scaled'], row['y_scaled'], color=color if row['Type'] != "Interception" else 'none', 
                                  edgecolors=color if row['Type'] == "Interception" else None, s=150, ax=ax1)
                
                # إضافة اسم اللاعب بجانب كل أكشن
                ax1.text(row['x_scaled'], row['y_scaled'] + 2, str(row['Player']), color='white', 
                         fontsize=8, ha='center', alpha=0.7)
            st.pyplot(fig1)

        # --- ملعب الخريطة الحرارية (في العمود الثاني) ---
        with col2:
            st.subheader("🔥 Activity Heatmap")
            fig2, ax2 = plt.subplots(figsize=(10, 7))
            pitch.draw(ax=ax2)
            fig2.patch.set_facecolor('#1a1a1a')
            
            if not filtered_df.empty:
                pitch.kdeplot(filtered_df['x_scaled'], filtered_df['y_scaled'], ax=ax2, fill=True, levels=100, cmap='inferno', alpha=0.6)
            st.pyplot(fig2)
