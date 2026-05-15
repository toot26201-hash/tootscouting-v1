import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np

st.set_page_config(page_title="TootScouting Pro Dashboard", layout="wide")

st.title("⚽ TootScouting | منصة التحليل المتقدمة")

uploaded_file = st.sidebar.file_uploader("ارفع ملف البيانات (CSV)", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['Action'] = df['Action'].str.strip().str.lower()

    # إنشاء تبويبات داخل الموقع
    tab1, tab2, tab3 = st.tabs(["📊 ملخص الأداء", "🏹 خريطة التمريرات", "🛡️ المنطقة الدفاعية"])

    with tab1:
        st.subheader("إحصائيات اللاعب العامة")
        st.dataframe(df)

    with tab2:
        st.subheader("Pass Map - خريطة التمريرات")
        # رسم ملعب كرة القدم
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # فلترة التمريرات (بافتراض وجود أعمدة x, y في ملفك)
        # لو ملفك الحالي summary بس، هنحتاج ملف الـ Actions الكامل عشان نرسم النقط
        st.write("ملاحظة: لرسم الخريطة بدقة، تأكد أن ملفك يحتوي على إحداثيات (x, y)")
        st.pyplot(fig)

    with tab3:
        st.subheader("Defensive Map - الخريطة الدفاعية")
        pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f0f0f0', line_color='#22312b')
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # هنا بنرسم أماكن الاستخلاص والتدخلات
        st.info("سيتم تحديد أماكن التدخلات الدفاعية بناءً على إحداثيات ملف الـ Tagging")
        st.pyplot(fig)

else:
    st.info("👋 ارفع ملف البيانات (CSV) لبدء تحليل الخرائط التكتيكية.")
