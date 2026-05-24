import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines

st.set_page_config(page_title="TootScouting Final", layout="wide")
st.title("🔬 TootScouting | Final Fixed Dashboard")

uploaded_file = st.sidebar.file_uploader("📥 Upload CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Mapping الأعمدة بناءً على الـ detected columns اللي ظهرت عندك
    df = df.rename(columns={
        'Action': 'Action',
        'Player': 'Player',
        'Tags': 'Tags',
        'X Start': 'x_start',
        'Y Start': 'y_start',
        'X End': 'x_end',
        'Y End': 'y_end'
    })
    
    # التأكد من الإحداثيات
    df['x_scaled'] = df['x_start'] * 1.2
    df['y_scaled'] = df['y_start'] * 0.8
    df['x_end_scaled'] = df['x_end'] * 1.2
    df['y_end_scaled'] = df['y_end'] * 0.8

    st.success("✅ الملف اتقرأ صح! جاري الرسم...")

    # رسم الملعب
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black')
    pitch.draw(ax=ax)
    
    # رسم باصات بسيطة كمثال
    pitch.arrows(df['x_scaled'], df['y_scaled'], df['x_end_scaled'], df['y_end_scaled'], ax=ax, color='green')
    
    # إضافة الـ Legend بخلفية بيضاء
    leg = ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), facecolor='white', edgecolor='black')
    for text in leg.get_texts():
        text.set_color('black')
        
    st.pyplot(fig)
else:
    st.info("👋 ارفع ملف الـ CSV عشان نبدأ.")
