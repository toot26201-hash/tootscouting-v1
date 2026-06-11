import streamlit as st
import pandas as pd

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
    # إزالة أي مسافات زائدة من أطراف أسماء الأعمدة (مثل "X Start " تصبح "X Start")
    df.columns = df.columns.str.strip()
    
    # قاموس لربط المسميات الحالية في ملفك بالمسميات المتوقعة في الكود
    column_mapping = {
        'X Start': 'x1',
        'Y Start': 'y1',
        'X End': 'x2',
        'Y End': 'y2'
    }
    
    # إعادة تسمية الأعمدة تلقائياً
    df = df.rename(columns=column_mapping)
    
    # -------------------------------------------------------------
    # 3. العمليات الحسابية وتغيير الأبعاد (Scaling)
    # -------------------------------------------------------------
    # التأكد من وجود الأعمدة المطلوبة قبل إجراء الحسابات
    required_columns = ['x1', 'y1', 'x2', 'y2']
    if all(col in df.columns for col in required_columns):
        
        # تحجيم الإحداثيات لتتناسب مع أبعاد الملعب (120x80)
        df['x_scaled'] = df['x1'] * 120
        df['y_scaled'] = df['y1'] * 80
        df['x2_scaled'] = df['x2'] * 120
        df['y2_scaled'] = df['y2'] * 80
        
        # عرض البيانات بعد التعديل للتأكد من سلامتها
        st.subheader("معاينة البيانات الحالية (الأعمدة المُعدلة):")
        st.write(df[['Player', 'Action', 'x_scaled', 'y_scaled']].head())
        
        # -------------------------------------------------------------
        # 4. هنا يمكنك وضع كود رسم الملعب (mplsoccer) والتحليلات الخاصة بك
        # -------------------------------------------------------------
        st.subheader("التحليلات والرسوم البيانية:")
        # كود رسم الخرائط الحرارية أو شبكات التمرير يوضع هنا باستخدام الأبعاد الجديدة (scaled)
        st.info("جاهز لرسم التمريرات وتحليل البيانات...")

    else:
        # رسالة تحذيرية واضحة في حال رُفع ملف مختلف تماماً ولا يحتوي على الإحداثيات
        st.error("عذراً، لم نتمكن من العثور على أعمدة الإحداثيات المطلوبة (X Start, Y Start).")
        st.write("الأعمدة المتوفرة في ملفك الحالي هي:")
        st.write(list(df.columns))

else:
    st.info("يرجى رفع ملف البيانات لبدء التحليل.")
