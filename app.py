%%writefile app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from math import pi

# 1. إعدادات الهوية البصرية (روح الهلال والاحترافية)
st.set_page_config(page_title="TootScouting Global Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #002D72; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌍 TootScouting | منصة تحليل الأداء العالمية")
st.sidebar.header("لوحة التحكم")

# 2. ميزة رفع الملفات (عشان تشتغل على أي دوري)
uploaded_file = st.sidebar.file_opener("ارفع ملف Summary (CSV)", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # تنظيف مسميات الأعمدة (عشان لو فيه مسافات زي 'extraction ')
    df['Action'] = df['Action'].str.strip()
    
    # استخراج البيانات ديناميكياً
    def get_val(action):
        try: return df[df['Action'] == action]['Count'].values[0]
        except: return 0

    pass_v = get_val('Pass')
    ext_v = get_val('extraction')
    cp_v = get_val('counter pressing')
    aerial_v = get_val('Aerial')
    dribble_v = get_val('Dribble')

    # --- عرض النتائج ---
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎯 ملخص الأداء")
        st.metric("إجمالي الإجراءات", get_val('Total'))
        
        # رسم الرادار
        categories = ['Pass', 'Extraction', 'C.Press', 'Aerial', 'Dribble']
        values = [pass_v/5, ext_v, cp_v*2, aerial_v*2, dribble_v*2]
        values += values[:1]
        angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        plt.xticks(angles[:-1], categories, color='#002D72', size=10)
        ax.plot(angles, values, color='#002D72', linewidth=2)
        ax.fill(angles, values, color='#0076CE', alpha=0.3)
        st.pyplot(fig)

    with col2:
        st.subheader("🔍 تفاصيل المؤشرات")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("التمريرات", pass_v)
        m_col2.metric("الاستخلاص", ext_v)
        m_col3.metric("ضغط عكسي", cp_v)
        
        st.markdown("### 📝 جدول البيانات الكامل")
        st.dataframe(df, use_container_width=True)
else:
    st.info("👋 مرحباً بك يا محمود. من فضلك ارفع ملف الـ Summary من القائمة الجانبية للبدء في التحليل.")