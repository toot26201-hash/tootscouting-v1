import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import io

# 1. إعدادات الصفحة الأساسية للتطبيق
st.set_page_config(
    page_title="TootScouting", 
    layout="wide"
)

# 2. القائمة الجانبية للتنقل (Sidebar)
st.sidebar.title("TootScouting 📊")

# خيارات التنقل بين واجهتك المعتادة واللوحة الجديدة
choice = st.sidebar.radio("القائمة الرئيسية:", ["الرئيسية وتحليل الأداء", "📊 لوحة تحليل لاعب (3 ملاعب)"])

# =========================================================================
# القسم الأول: لوحة الملاعب الثلاثة الاحترافية (الملعب الأبيض)
# =========================================================================
if choice == "📊 لوحة تحليل لاعب (3 ملاعب)":
    st.title("🎯 لوحة تحليل أداء اللاعب الإحصائية | Player Dashboard")
    st.markdown("تحليل بصري متكامل للأدوار الهجومية، الدفاعية، ومناطق استلام الكرة.")
    st.write("---")

    # أ. بيانات وهمية تحاكي تفاصيل أداء اللاعب (مثل Nuno Mendes)
    passes_df = pd.DataFrame({
        'x': [30, 45, 55, 65, 75, 80], 'y': [10, 15, 12, 20, 18, 25],
        'end_x': [50, 60, 70, 85, 92, 95], 'end_y': [12, 18, 15, 30, 22, 45],
        'type': ['Successful', 'Successful', 'Progressive', 'Progressive', 'Key Pass', 'Key Pass']
    })
    
    def defensive_df():
        return pd.DataFrame({
            'x': [35, 42, 50, 58, 25, 62], 'y': [15, 22, 18, 35, 12, 40],
            'action': ['Tackle (Succ.)', 'Tackle (Succ.)', 'Ball Recovery', 'Ball Recovery', 'Clearance', 'Pass Blocked']
        })
    df_def = defensive_df()
    
    # توليد نقاط عشوائية للمسات اللاعب
    np.random.seed(42)
    touches_df = pd.DataFrame({
        'x': np.random.uniform(30, 85, 35),
        'y': np.random.uniform(5, 35, 35)
    })

    # ب. تقسيم الصفحة إلى 3 أعمدة لعرض الملاعب بجانب بعضها
    col1, col2, col3 = st.columns(3)
    
    # 💡 هنا تم تعديل الملعب ليكون أبيض بالكامل (#ffffff) والخطوط رمادي داكن (#444444) ليفصل بوضوح
    pitch = Pitch(pitch_type='opta', pitch_color='#ffffff', line_color='#444444', orientation='vertical')

    # ---- العمود الأول: Offensive Actions ----
    with col1:
        st.subheader("⚔️ Offensive Actions")
        fig1, ax1 = pitch.draw(figsize=(5, 7))
        fig1.patch.set_facecolor('#ffffff') # 💡 تلوين خلفية الشكل الخارجي بالأبيض
        
        for _, row in passes_df.iterrows():
            if row['type'] == 'Successful': color = '#94a3b8'
            elif row['type'] == 'Progressive': color = '#0ea5e9'
            else: color = '#a855f7' # Key Pass
            pitch.arrows(row['x'], row['y'], row['end_x'], row['end_y'], color=color, width=2, headwidth=4, ax=ax1)
        st.pyplot(fig1)
        st.markdown("""
        * <span style='color:#94a3b8'>■</span> Successful Pass: **47**
        * <span style='color:#0ea5e9'>■</span> Progressive Pass: **8**
        * <span style='color:#a855f7'>■</span> Key Passes: **4**
        """, unsafe_allow_html=True)

    # ---- العمود الثاني: Defensive Actions ----
    with col2:
        st.subheader("🛡️ Defensive Actions")
        fig2, ax2 = pitch.draw(figsize=(5, 7))
        fig2.patch.set_facecolor('#ffffff') # 💡 تلوين خلفية الشكل الخارجي بالأبيض
        
        for _, row in df_def.iterrows():
            if 'Tackle' in row['action']: marker = 'x'
            elif 'Recovery' in row['action']: marker = 'o'
            else: marker = 's'
            pitch.scatter(row['x'], row['y'], marker=marker, s=150, color='#0284c7', edgecolors='#ffffff', ax=ax2)
        st.pyplot(fig2)
        st.markdown("""
        * **X** Tackle (Succ.): **2**
        * **O** Ball Recoveries: **3**
        * **■** Other Actions: **1**
        """, unsafe_allow_html=True)

    # ---- العمود الثالث: Touches & Pass Receiving ----
    with col3:
        st.subheader("📍 Touches & Pass Receiving")
        fig3, ax3 = pitch.draw(figsize=(5, 7))
        fig3.patch.set_facecolor('#ffffff') # 💡 تلوين خلفية الشكل الخارجي بالأبيض
        
        pitch.scatter(touches_df['x'], touches_df['y'], s=45, color='#ef4444', edgecolors='#444444', alpha=0.8, ax=ax3)
        pitch.kdeplot(touches_df['x'], touches_df['y'], ax=ax3, cmap='Blues', fill=True, alpha=0.4, zorder=0)
        st.pyplot(fig3)
        st.markdown("""
        * **Total Touches:** 70
        * **at Final Third:** 12
        * **at Penalty Box:** 0
        """, unsafe_allow_html=True)

# =========================================================================
# القسم الثاني: واجهتك القديمة المعتادة (تظهر تلقائياً عند فتح الموقع)
# =========================================================================
else:
    # ⚠️ اترك هذا الجزء كما هو وضع كودك القديم هنا ليعمل كالمعتاد ⚠️
    st.title("TootScouting Platform 📊")
    st.write("أهلاً بك في تطبيق التحليل الخاص بك.")
    
    st.info("قم باختيار '📊 لوحة تحليل لاعب (3 ملاعب)' من القائمة الجانبية لتجربة الأداة الجديدة المضافة.")
    
    st.subheader("مؤشرات تحليل الأداء الحالية")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['تمريرات خفيفة', 'صناعة فرص', 'تمريرات طولية'])
    st.line_chart(chart_data)
