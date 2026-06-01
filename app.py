import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import numpy as np
import matplotlib.colors as mcolors

# --- إعداد المعالجة ---
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
    return df.dropna(subset=['Action', 'Player'])

# --- واجهة التطبيق ---
st.set_page_config(layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV", type=['csv'])

if uploaded_file is not None:
    team_df = process_data(uploaded_file)
    player_list = sorted(team_df['Player'].unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 Select Player:", player_list)
    p_df = team_df[team_df['Player'] == sel_player].copy()
    
    # --- تعريف التابات ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔥 Heatmap", "🏃‍♂️ Actions", "📊 Stats", "👥 Team Heat", "🛡️ Team Defense"])
    
    # 1. تابة الهيت ماب
    with tab1:
        st.write("### Player Heatmap")
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        if len(p_df) > 1:
            sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, cmap='viridis', ax=ax)
        st.pyplot(fig)
        
    # 2. تابة الأكشن
    with tab2:
        st.write("### Player Actions Map")
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        for _, row in p_df.iterrows():
            pitch.arrows(row['x_scaled'], row['y_scaled'], row['x_end_scaled'], row['y_end_scaled'], ax=ax, color='green')
        st.pyplot(fig)

    # 3. تابة الإحصائيات (مثال بسيط)
    with tab3:
        st.write("### Performance Statistics")
        st.dataframe(p_df[['Action', 'Player', 'Tags']])

    # 4. تابة الفريق (Heatmap)
    with tab4:
        st.write("### Team Heatmap")
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        sns.kdeplot(x=team_df['x_scaled'], y=team_df['y_scaled'], fill=True, cmap='viridis', ax=ax)
        st.pyplot(fig)

    # 5. تابة الدفاع
    with tab5:
        st.write("### Team Defensive Actions")
        pitch = Pitch(pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(10, 7))
        def_df = team_df[team_df['Action'].str.contains('Tackle|Clearance', case=False, na=False)]
        pitch.scatter(def_df['x_scaled'], def_df['y_scaled'], ax=ax, color='red')
        st.pyplot(fig)

else:
    st.info("👋 يرجى رفع ملف CSV للبدء.")
