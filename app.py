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
        # 4. معالجة البيانات الصالحة التي تحتوي على إحداثيات
        # -------------------------------------------------------------
        # نأخذ فقط الصفوف التي تحتوي على إحداثيات بداية صحيحة (ليست فارغة) لضمان الرسم
        valid_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()].copy()
        
        valid_df['Action'] = valid_df['Action'].astype(str).str.strip()
        valid_df['Tags'] = valid_df['Tags'].fillna('').astype(str)
        
        # حساب المسافة التقدمية للأمام
        valid_df['prog_distance'] = valid_df['x2_scaled'] - valid_df['x_scaled']

        # -------------------------------------------------------------
        # 5. القوائم المنسدلة الذكية (تعتمد على المتاح في ملفك)
        # -------------------------------------------------------------
        st.subheader("🎯 فلاتر التحليل الهجومي المتقدم")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # القائمة الأساسية
            main_options = [
                "كل التمريرات والأحداث",
                "تمريرة تقديمية (Progressive Pass)",
                "ثرو باص (Through Ball)",
                "أكشن هجومي مخصص (من الملف)"
            ]
            selected_main = st.selectbox("اختر نوع التحليل الرئيسي:", main_options)
            
        with col2:
            players_list = ["كل اللاعبين"] + list(valid_df['Player'].dropna().unique())
            selected_player = st.selectbox("فلترة بحسب اللاعب:", players_list)

        # -------------------------------------------------------------
        # 6. تطبيق الفلترة الديناميكية لضمان عدم خروج جدول فارغ
        # -------------------------------------------------------------
        filtered_df = valid_df.copy()
        
        if selected_player != "كل اللاعبين":
            filtered_df = filtered_df[filtered_df['Player'] == selected_player]

        color_theme = '#00ffcc'  # اللون الافتراضي الفسفوري
        
        # تخصيص الفلترة بناءً على الاختيار
        if selected_main == "كل التمريرات والأحداث":
            # يعرض لك كل ما يحتوي على إحداثيات في الملف مباشرة لضمان ظهور الملعب فوراً
            color_theme = '#00ffcc'
            
        elif selected_main == "تمريرة تقديمية (Progressive Pass)":
            # فلترة برمجية بحتة تعتمد على المسافة المقطوعة للأمام (أكبر من 10 أمتار)
            filtered_df = filtered_df[filtered_df['prog_distance'] >= 10]
            color_theme = '#ff9900'
            
        elif selected_main == "ثرو باص (Through Ball)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Through|Key|ثرو', case=False) | 
                filtered_df['Tags'].str.contains('through|key|Behind', case=False)
            ]
            color_theme = '#cc00ff'
            
        elif selected_main == "أكشن هجومي مخصص (من الملف)":
            # هنا السحر! الكود يقرأ الكلمات الفعلية الموجودة في عمود Action في ملفك ويخليك تختار منها
            unique_actions = list(filtered_df['Action'].unique())
            with col1:
                selected_custom_action = st.selectbox("اختر الأكشن الفعلي الموجود بملفك:", unique_actions)
            filtered_df = filtered_df[filtered_df['Action'] == selected_custom_action]
            color_theme = '#ffff00'

        # -------------------------------------------------------------
        # 7. رسم المل
