import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

# --- المعالجة ---
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
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

# --- الواجهة ---
st.set_page_config(layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV", type=['csv'])

if uploaded_file is not None:
    team_df = process_data(uploaded_file)
    
    # اختيار اللاعب
    player_list = sorted([str(p) for p in team_df['Player'].unique() if str(p).strip() not in ['nan', '']])
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب للتحليل:", player_list)
    p_df = team_df[team_df['Player'] == sel_player].copy()
    
    # التابات
    tab_player, tab_team = st.tabs(["👤 تحليل اللاعب", "👥 تحليل الفريق"])
    
    # --- تابة اللاعب (الخرائط الثلاث) ---
    with tab_player:
        st.subheader(f"📊 التحليل التكتيكي لـ: {sel_player}")
        c1, c2, c3 = st.columns(3)
        
        # 1. الخريطة الهجومية
        with c1:
            st.write("⚽ الأكشن الهجومي")
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
            fig, ax = pitch.draw()
            atk = p_df[p_df['Action'].str.contains('Pass|Shot|Cross', case=False, na=False)]
            pitch.arrows(atk.x_scaled, atk.y_scaled, atk.x_end_scaled, atk.y_end_scaled, ax=ax, color='blue', alpha=0.4)
            st.pyplot(fig)
            
        # 2. الخريطة الدفاعية
        with c2:
            st.write("🛡️ الأكشن الدفاعي")
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
            fig, ax = pitch.draw()
            def_df = p_df[p_df['Action'].str.contains('Tackle|Clearance|Duel', case=False, na=False)]
            pitch.scatter(def_df.x_scaled, def_df.y_scaled, ax=ax, color='red', marker='x', s=100)
            st.pyplot(fig)
            
        # 3. الخريطة المكس (كاملة)
        with c3:
            st.write("🔄 الخريطة الشاملة (Mix)")
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
            fig, ax = pitch.draw()
            sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, cmap='viridis', alpha=0.3, ax=ax)
            st.pyplot(fig)

    # تابة الفريق (كما كانت)
    with tab_team:
        st.write("### خريطة الفريق الحرارية")
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw()
        sns.kdeplot(x=team_df['x_scaled'], y=team_df['y_scaled'], fill=True, cmap='magma', ax=ax)
        st.pyplot(fig)

else:
    st.info("👋 يرجى رفع ملف CSV للبدء.")
