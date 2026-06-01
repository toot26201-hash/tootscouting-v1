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
    
    # 1. قوائم الاختيار في الـ Sidebar
    st.sidebar.markdown("### 🔍 فلترة العمليات")
    
    # قائمة الأكشن الهجومي
    attack_options = ["Pass", "Shot", "Cross", "Key Pass"]
    selected_attack = st.sidebar.multiselect("⚽ الأكشن الهجومي:", attack_options, default=["Pass"])
    
    # قائمة الأكشن الدفاعي
    defense_options = ["Tackle", "Clearance", "Duel", "Interception"]
    selected_defense = st.sidebar.multiselect("🛡️ الأكشن الدفاعي:", defense_options, default=["Tackle"])
    
    # --- التابات ---
    tab_player, tab_team_heat, tab_attack, tab_defense = st.tabs([
        "👤 اللاعب", "👥 الفريق (Heatmap)", "⚽ الأكشن الهجومي", "🛡️ الأكشن الدفاعي"
    ])
    
    # تابة الهجوم (تستخدم الفلتر)
    with tab_attack:
        st.write("### تصفية الأكشن الهجومي")
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # إنشاء فلتر ديناميكي
        pattern = '|'.join(selected_attack)
        atk_df = team_df[team_df['Action'].str.contains(pattern, case=False, na=False)]
        
        for _, row in atk_df.iterrows():
            pitch.arrows(row['x_scaled'], row['y_scaled'], row['x_end_scaled'], row['y_end_scaled'], ax=ax, color='blue', alpha=0.5)
        st.pyplot(fig)
        
    # تابة الدفاع (تستخدم الفلتر)
    with tab_defense:
        st.write("### تصفية الأكشن الدفاعي")
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        
        pattern = '|'.join(selected_defense)
        def_df = team_df[team_df['Action'].str.contains(pattern, case=False, na=False)]
        
        pitch.scatter(def_df['x_scaled'], def_df['y_scaled'], ax=ax, color='red', marker='x', s=100)
        st.pyplot(fig)
