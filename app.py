import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

# --- 1. معالجة البيانات ---
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    rename_dict = {'Action': 'Action', 'Player': 'Player', 'Tags': 'Tags', 
                   'X1': 'x_start', 'Y1': 'y_start', 'X2': 'x_end', 'Y2': 'y_end'}
    df = df.rename(columns=rename_dict)
    for col in ['x_start', 'y_start', 'x_end', 'y_end']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['x_scaled'] = df['x_start'] * 120
    df['y_scaled'] = df['y_start'] * 80
    df['x_end_scaled'] = df['x_end'] * 120
    df['y_end_scaled'] = df['y_end'] * 80
    return df

# --- 2. الإعدادات ---
st.set_page_config(layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV", type=['csv'])

if uploaded_file is not None:
    full_df = process_data(uploaded_file)
    
    # اختيار اللاعب
    players = sorted([str(p) for p in full_df['Player'].unique() if str(p).strip() not in ['nan', '']])
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", players)
    p_df = full_df[full_df['Player'] == sel_player].copy()
    
    # تعريف التابات
    tab1, tab2, tab3, tab4 = st.tabs(["👤 تحليل اللاعب", "👥 الفريق (Heatmap)", "⚽ الهجوم", "🛡️ الدفاع"])
    
    # --- 3. محتوى التابات (استخدام subplots لضمان الاستقلالية) ---
    
    with tab1: # تحليل اللاعب (هجوم + دفاع + مكس)
        st.subheader(f"تحليل اللاعب: {sel_player}")
        cols = st.columns(3)
        for i, (title, color, action_filter) in enumerate([
            ("هجومي", "blue", "Pass|Shot|Cross"), 
            ("دفاعي", "red", "Tackle|Clearance|Duel"), 
            ("شامل (Mix)", "green", ".*")
        ]):
            with cols[i]:
                st.write(f"**{title}**")
                fig, ax = plt.subplots(figsize=(6, 4))
                pitch = Pitch(pitch_type='statsbomb')
                pitch.draw(ax=ax)
                df_sub = p_df[p_df['Action'].str.contains(action_filter, case=False, na=False)]
                if title == "شامل (Mix)":
                    sns.kdeplot(x=df_sub.x_scaled, y=df_sub.y_scaled, fill=True, cmap='viridis', ax=ax)
                else:
                    pitch.scatter(df_sub.x_scaled, df_sub.y_scaled, ax=ax, color=color)
                st.pyplot(fig)

    with tab2: # الفريق
        st.write("### خريطة الفريق الحرارية")
        fig, ax = plt.subplots(figsize=(10, 7))
        Pitch(pitch_type='statsbomb').draw(ax=ax)
        sns.kdeplot(x=full_df.x_scaled, y=full_df.y_scaled, fill=True, cmap='magma', ax=ax)
        st.pyplot(fig)

    with tab3: # الهجوم
        st.write("### الأكشن الهجومي")
        fig, ax = plt.subplots(figsize=(10, 7))
        Pitch(pitch_type='statsbomb').draw(ax=ax)
        df_atk = full_df[full_df['Action'].str.contains('Pass|Shot|Cross|Goal', case=False, na=False)]
        for _, r in df_atk.iterrows():
            plt.arrow(r.x_scaled, r.y_scaled, r.x_end_scaled-r.x_scaled, r.y_end_scaled-r.y_scaled, color='blue', alpha=0.3)
        st.pyplot(fig)

    with tab4: # الدفاع
        st.write("### الأكشن الدفاعي")
        fig, ax = plt.subplots(figsize=(10, 7))
        Pitch(pitch_type='statsbomb').draw(ax=ax)
        df_def = full_df[full_df['Action'].str.contains('Tackle|Clearance|Duel', case=False, na=False)]
        plt.scatter(df_def.x_scaled, df_def.y_scaled, color='red', marker='x')
        st.pyplot(fig)

else:
    st.info("👋 يرجى رفع ملف الـ CSV.")
