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
    
    # التابات
    tab_player, tab_team_heat, tab_attack, tab_defense = st.tabs([
        "👤 اللاعب (تفصيلي)", 
        "👥 الفريق (Heatmap)", 
        "⚽ الأكشن الهجومي", 
        "🛡️ الأكشن الدفاعي"
    ])
    
    # 1. تابة اللاعب
    with tab_player:
        sel_player = st.selectbox("🎯 اختر اللاعب:", sorted(team_df['Player'].unique()))
        p_df = team_df[team_df['Player'] == sel_player]
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, cmap='viridis', ax=ax)
        st.pyplot(fig)
        
    # 2. تابة الفريق
    with tab_team_heat:
        st.write("### خريطة الفريق الحرارية")
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        sns.kdeplot(x=team_df['x_scaled'], y=team_df['y_scaled'], fill=True, cmap='magma', ax=ax)
        st.pyplot(fig)
        
    # 3. تابة الهجوم
    with tab_attack:
        st.write("### الأكشن الهجومي (تمريرات وتسديدات)")
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        atk_df = team_df[team_df['Action'].str.contains('Pass|Shot|Cross', case=False, na=False)]
        for _, row in atk_df.iterrows():
            pitch.arrows(row['x_scaled'], row['y_scaled'], row['x_end_scaled'], row['y_end_scaled'], ax=ax, color='blue', alpha=0.3)
        st.pyplot(fig)
        
    # 4. تابة الدفاع
    with tab_defense:
        st.write("### الأكشن الدفاعي (تدخلات وقطع كرات)")
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        def_df = team_df[team_df['Action'].str.contains('Tackle|Clearance|Duel', case=False, na=False)]
        pitch.scatter(def_df['x_scaled'], def_df['y_scaled'], ax=ax, color='red', marker='x')
        st.pyplot(fig)
