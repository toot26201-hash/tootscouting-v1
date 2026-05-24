import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines

# Set page config
st.set_page_config(layout="wide")
st.title("🔬 TootScouting | Final Fixed Dashboard")

uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV", type=['csv'])

if uploaded_file is not None:
    try:
        # قراءة الملف
        df = pd.read_csv(uploaded_file)
        
        # استخدام أسماء الأعمدة الفعلية من صورتك
        required_cols = ['X Start', 'Y Start', 'X End', 'Y End', 'Action', 'Player']
        if not all(col in df.columns for col in required_cols):
            st.error(f"⚠️ الملف لا يحتوي على الأعمدة المطلوبة. تأكد من وجود: {required_cols}")
            st.stop()

        # إعداد البيانات للرسم (مع تحويل الإحداثيات)
        df['x_scaled'] = df['X Start'] * 1.2
        df['y_scaled'] = df['Y Start'] * 0.8
        df['x_end_scaled'] = df['X End'] * 1.2
        df['y_end_scaled'] = df['Y End'] * 0.8

        st.success("✅ البيانات جاهزة! جاري رسم الخريطة...")

        # إنشاء الملعب
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black')
        pitch.draw(ax=ax)
        
        # رسم الباصات (مثال)
        pitch.arrows(df['x_scaled'], df['y_scaled'], df['x_end_scaled'], df['y_end_scaled'], 
                     width=2, color='green', ax=ax, label='Passes')

        # ضبط الـ Legend بخلفية بيضاء
        leg = ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), 
                        facecolor='white', framealpha=1, edgecolor='black')
        for text in leg.get_texts():
            text.set_color('black')
            
        st.pyplot(fig)

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
else:
    st.info("👋 ارفع ملف الـ CSV لبدء التحليل.")
