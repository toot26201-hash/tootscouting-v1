import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(layout="wide") # لجعل واجهة التطبيق عريضة ومناسبة للتحليل
st.title("TootScouting - Match Analysis Dashboard")

# 1. رفع ملف البيانات (CSV أو Excel)
uploaded_file = st.file_uploader("قم برفع ملف البيانات (Excel أو CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # قراءة الملف بناءً على امتداده
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    st.success("تم رفع الملف بنجاح!")
    
    # -------------------------------------------------------------
    # 2. معالجة وتجهيز أسماء الأعمدة لمنع الـ KeyError
    # -------------------------------------------------------------
    df.columns = df.columns.str.strip()
    
    column_mapping = {
        'X Start': 'x1',
        'Y Start': 'y1',
        'X End': 'x2',
        'Y End': 'y2'
    }
    
    df = df.rename(columns=column_mapping)
    
    # -------------------------------------------------------------
    # 3. العمليات الحسابية وتغيير الأبعاد (Scaling)
    # -------------------------------------------------------------
    required_columns = ['x1', 'y1', 'x2', 'y2']
    if all(col in df.columns for col in required_columns):
        
        # تحجيم الإحداثيات لتتناسب مع أبعاد الملعب (120x80)
        df['x_scaled'] = df['x1'] * 120
        df['y_scaled'] = df['y1'] * 80
        df['x2_scaled'] = df['x2'] * 120
        df['y2_scaled'] = df['y2'] * 80
        
        # معاينة البيانات في قائمة جانبية أو تبويب اختياري لتوفير مساحة
        with st.expander("معاينة جدول البيانات المُعدلة"):
            st.write(df[['Player', 'Action', 'x_scaled', 'y_scaled', 'x2_scaled', 'y2_scaled']].head(10))
        
        # -------------------------------------------------------------
        # 4. فلترة التمريرات وتجهيز رسم الملعب
        # -------------------------------------------------------------
        st.subheader("📊 خريطة التمريرات (Pass Map)")
        
        # فلترة التمريرات الناجحة فقط والتي تحتوي على إحداثيات (حذف الـ None)
        # ملاحظة: يمكنك تغيير كلمة 'Pass' حسب المسمى الموجود في عمود Event Type أو Action لديك
        passes_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()]
        
        # خيار إضافي: تصفية التمريرات بحسب اللاعب
        players_list = ["الكل"] + list(passes_df['Player'].dropna().unique())
        selected_player = st.selectbox("اختر اللاعب لتحليل تمريراته:", players_list)
        
        if selected_player != "الكل":
            passes_df = passes_df[passes_df['Player'] == selected_player]
            
        if not passes_df.empty:
            # رسم الملعب باستخدام mplsoccer
            # التموضع العمودي أو الأفقي (هنا أفقي pitch_type='statsbomb' بأبعاد 120x80)
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
            fig, ax = pitch.draw(figsize=(12, 8))
            
            # رسم أسهم التarguments (من نقطة البداية إلى نقطة النهاية)
            pitch.arrows(
                passes_df['x_scaled'], passes_df['y_scaled'],
                passes_df['x2_scaled'], passes_df['y2_scaled'],
                width=2, headwidth=3, headlength=3,
                color='#00ffcc', alpha=0.7, ax=ax, label='Passes'
            )
            
            # رسم نقاط بداية التمريرة
            pitch.scatter(
                passes_df['x_scaled'], passes_df['y_scaled'],
                color='#00ffcc', s=40, edgecolors='#ffffff', zorder=3, ax=ax
            )
            
            # تحسين شكل الرسم الخلفي
            fig.patch.set_facecolor('#1a1a1a')
            st.pyplot(fig)
            
            st.caption(f"تم رسم {len(passes_df)} تمريرة بنجاح للاعبين المحددين.")
        else:
            st.warning("لا توجد تمريرات تحتوي على إحداثيات صالحة للرسم بناءً على الفلتر المختار.")

    else:
        st.error("عذراً، لم نتمكن من العثور على أعمدة الإحداثيات المطلوبة (X Start, Y Start).")
        st.write("الأعمدة المتوفرة في ملفك الحالي هي:")
        st.write(list(df.columns))

else:
    st.info("يرجى رفع ملف البيانات لبدء التحليل.")
