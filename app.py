import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# إعداد الصفحة
st.set_page_config(layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# رفع الملف
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV", type=['csv'])

if uploaded_file is not None:
    try:
        # قراءة الملف
        df = pd.read_csv(uploaded_file)
        
        # التأكد من وجود الأعمدة المطلوبة
        required_cols = ['X Start', 'Y Start', 'X End', 'Y End', 'Action', 'Player']
        if not all(col in df.columns for col in required_cols):
            st.error(f"⚠️ الملف يجب أن يحتوي على الأعمدة التالية: {required_cols}")
            st.stop()

        # تجهيز البيانات
        df['x_scaled'] = df['X Start'] * 1.2
        df['y_scaled'] = df['Y Start'] * 0.8
        df['x_end_scaled'] = df['X End'] * 1.2
        df['y_end_scaled'] = df['Y End'] * 0.8

        st.success("✅ تم قراءة البيانات بنجاح، جاري رسم الخريطة...")

        # رسم الملعب
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black')
        pitch.draw(ax=ax)
        
        # رسم الباصات
        pitch.arrows(df['x_scaled'], df['y_scaled'], df['x_end_scaled'], df['y_end_scaled'], 
                     width=2, color='green', ax=ax, label='Passes')

        # ضبط الـ Legend بخلفية بيضاء ونصوص سوداء
        leg = ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), 
                        facecolor='white', framealpha=1, edgecolor='black')
        for text in leg.get_texts():
            text.set_color('black')
            
        st.pyplot(fig)

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {e}")
else:
    st.info("👋 من فضلك ارفع ملف الـ CSV الخاص بالمباراة للبدء.")
