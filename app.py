import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import seaborn as sns

st.set_page_config(page_title="TootScouting Tactical Dashboard", layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro")

uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تحويل الإحداثيات
    df = df.rename(columns={'X1': 'x1', 'Y1': 'y1'})
    df['x_scaled'] = df['x1'] * 120
    df['y_scaled'] = df['y1'] * 80
    
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df['Player'] = df['Player'].fillna('Unknown').astype(str)
    df['Tags'] = df['Tags'].fillna('').astype(str)

    # الأدوات
    players = sorted(df['Player'].dropna().unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", players)
    
    # اختيار الأكشن
    att_choices = st.sidebar.multiselect("⚽ الأكشن الهجومي:", ["Pass", "Shot", "Cross", "Goal"])
    def_choices = st.sidebar.multiselect("🛡️ الأكشن الدفاعي:", ["pressing", "extraction", "Tackle", "Foul", "Ground Duel", "Aerial Duel"])

    p_df = df[df['Player'] == sel_player].copy()
    
    tab1, tab2 = st.tabs(["🔥 Heatmap", "🗺️ Action Maps"])
    
    with tab1:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
        fig1, ax1 = pitch.draw(figsize=(10, 7))
        sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, ax=ax1, cmap='viridis')
        st.pyplot(fig1)
        
    with tab2:
        pitch, fig2, ax2 = pitch.draw(figsize=(10, 7))
        
        # دالة لتحديد اللون والرمز
        for _, row in p_df.iterrows():
            act = str(row['Action'])
            tag = str(row['Tags'])
            
            # منطق الأكشن الهجومي
            if 'Pass' in act:
                color = '#2ecc71' if 'Success' in tag else '#e74c3c'
                pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='>', s=100)
            elif 'Shot' in act:
                color = '#2563eb' if 'On Target' in tag else '#dc2626'
                pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='*', s=200)
            elif 'Goal' in act:
                pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color='gold', marker='*', s=300)
            
            # منطق الأكشن الدفاعي
            elif 'Foul' in act:
                pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color='red', marker='x', s=150)
            elif 'pressing' in act:
                pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color='#2ecc71', marker='#', s=150) # شباك
            elif 'Aerial' in act:
                color = '#2ecc71' if 'Won' in tag else '#e74c3c'
                pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='^', s=150)
            elif 'Ground' in act:
                color = '#2ecc71' if 'Won' in tag else '#e74c3c'
                pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='s', s=150)
            elif 'Tackle' in act or 'extraction' in act:
                pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color='purple', marker='d', s=150)

        st.pyplot(fig2)

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
