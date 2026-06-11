import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. رفع ملف البيانات (CSV أو Excel)
uploaded_file = st.file_uploader("قم برفع ملف البيانات (Excel أو CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
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
        'X Start': 'x1', 'Y Start': 'y1',
        'X End': 'x2', 'Y End': 'y2'
    }
    df = df.rename(columns=column_mapping)
    
    # -------------------------------------------------------------
    # 3. العمليات الحسابية وتغيير الأبعاد (Scaling)
    # -------------------------------------------------------------
    required_columns = ['x1', 'y1', 'x2', 'y2']
    if all(col in df.columns for col in required_columns):
        
        df['x_scaled'] = df['x1'] * 120
        df['y_scaled'] = df['y1'] * 80
        df['x2_scaled'] = df['x2'] * 120
        df['y2_scaled'] = df['y2'] * 80
        
        # -------------------------------------------------------------
        # 4. الذكاء الاصطناعي الداخلي لتصنيف التمريرات والأكشن الهجومي
        # -------------------------------------------------------------
        # فلترة الأحداث التي تحتوي على إحداثيات صالحة
        valid_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()].copy()
        
        # التأكد من تحويل الأعمدة إلى نصوص لتجنب الأخطاء
        valid_df['Action'] = valid_df['Action'].astype(str)
        valid_df['Tags'] = valid_df['Tags'].fillna('').astype(str)
        
        # حساب المسافة العمودية التي قطعتها التمريرة للأمام (x2 - x1)
        # التمريرة التقدمية (Progressive) هي التي تتقدم بالكرة مسافة معينة للأمام (مثلاً أكثر من 15 متر في ثلثي الملعب)
        valid_df['prog_distance'] = valid_df['x2_scaled'] - valid_df['x_scaled']

        # -------------------------------------------------------------
        # 5. القوائم المنسدلة المطلوبة
        # -------------------------------------------------------------
        st.subheader("🎯 فلاتر التحليل الهجومي المتقدم")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # قائمة الأكشن الهجومي الرئيسي المطلوبة بالكامل
            attack_options = [
                "تمريرة عادية (Normal Pass)",
                "تمريرة تقديمية (Progressive Pass)",
                "ثرو باص (Through Ball)",
                "عرضية (Cross)",
                "كورنر (Corner)",
                "تسديدة (Shot)",
                "هدف (Goal)"
            ]
            selected_action = st.selectbox("اختر الأكشن الهجومي بدقة:", attack_options)
            
        with col2:
            # فلتر اللاعبين لزيادة التحكم
            players_list =
