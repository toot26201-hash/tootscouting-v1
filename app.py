import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors
import numpy as np

# --- 1. المعالجة الأساسية (تُطبق على كل شيء) ---
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    # ربط أعمدة ملفك
    rename_dict = {'Action': 'Action', 'Player': 'Player', 'Tags': 'Tags', 
                   'X1': 'x_start', 'Y1': 'y_start', 'X2': 'x_end', 'Y2': 'y_end'}
    df = df.rename(columns=rename_dict)
    for col in ['x_start', 'y_start', 'x_end', 'y_end']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # الحساب الإجباري لضمان عدم حدوث KeyError
    df['x_scaled'] = df['x_start'] * 120
    df['y_scaled'] = df['y_start'] * 80
    df['x_end_scaled'] = df['x_end'] * 120
    df['y_end_scaled'] = df['y_end'] * 80
    return df.dropna(subset=['Action', 'Player'])

# --- 2. إعداد الصفحة ---
st.set_page_config(layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV", type=['csv'])

if uploaded_file is not None:
    # المعالجة تتم هنا وتنتج الـ DataFrame الكامل
    full_df = process_data(uploaded_file)
    
    # الفلاتر
    st.sidebar.markdown("### 🔍 الفلاتر")
    atk_list = st.sidebar.multiselect("⚽ هجوم:", ["Pass", "Shot", "Cross", "Goal"], default=["Pass"])
    def_list = st.sidebar.multiselect("🛡️ دفاع:", ["Tackle", "Clearance", "Duel"], default=["Tackle"])
    
    # اختيار اللاعب
    player_list = sorted([str(p) for p in full_df['Player'].unique() if str(p).strip() not in ['nan', '']])
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", player_list)
    p_df = full_df[full_df['Player'] == sel_player].copy()
    
    # --- التابات ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 اللاعب", "👥 الفريق (Heatmap)", "⚽ الهجوم", "🛡️ الدفاع", "📊 إحصائيات"])
    
    # 1. تابة اللاعب (مكس)
    with tab1:
        st.subheader(f"تحليل اللاعب: {sel_player}")
        cols = st.columns(3)
        # خريطة هجومية
        with cols[0]:
            fig, ax = plt.subplots()
            Pitch(pitch_type='statsbomb').draw(ax=ax)
            atk = p_df[p_df['Action'].str.contains('Pass|Shot|Cross', case=False, na=False)]
            pitch_arrows = Pitch(pitch_type='statsbomb')
            pitch_arrows.arrows(atk.x_scaled, atk.y_scaled, atk.x_end_scaled, atk.y_end_scaled, ax=ax, color='blue', alpha=0.4)
            st.pyplot(fig)
        # خريطة دفاعية
        with cols[1]:
            fig, ax = plt.subplots()
            Pitch(pitch_type='statsbomb').draw(ax=ax)
            df_def = p_df[p_df['Action'].str.contains('Tackle|Clearance|Duel', case=False, na=False)]
            ax.scatter(df_def.x_scaled, df_def.y_scaled, color='red', marker='x', s=100)
            st.pyplot(fig)
        # خريطة حرارية
        with cols[2]:
            fig, ax = plt.subplots()
            Pitch(pitch_type='statsbomb').draw(ax=ax)
            sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, cmap='viridis', ax=ax)
            st.pyplot(fig)
            
    # 2. تابة الفريق
    with tab2:
        fig, ax = plt.subplots()
        Pitch(pitch_type='statsbomb').draw(ax=ax)
        sns.kdeplot(x=full_df['x_scaled'], y=full_df['y_scaled'], fill=True, cmap='magma', ax=ax)
        st.pyplot(fig)
        
    # 3. تابة الهجوم
    with tab3:
        fig, ax = plt.subplots()
        Pitch(pitch_type='statsbomb').draw(ax=ax)
        pattern = '|'.join(atk_list)
        df_atk = full_df[full_df['Action'].str.contains(pattern, case=False, na=False)]
        for _, r in df_atk.iterrows():
            plt.arrow(r.x_scaled, r.y_scaled, r.x_end_scaled-r.x_scaled, r.y_end_scaled-r.y_scaled, color='blue', alpha=0.3)
        st.pyplot(fig)

    # 4. تابة الدفاع
    with tab4:
        fig, ax = plt.subplots()
        Pitch(pitch_type='statsbomb').draw(ax=ax)
        pattern = '|'.join(def_list)
        df_def = full_df[full_df['Action'].str.contains(pattern, case=False, na=False)]
        plt.scatter(df_def.x_scaled, df_def.y_scaled, color='red', marker='x', s=100)
        st.pyplot(fig)
        
    # 5. تابة الإحصائيات
    with tab5:
        st.write(p_df)

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
