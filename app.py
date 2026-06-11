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
        # 4. معالجة وتصنيف التمريرات والأكشن الهجومي
        # -------------------------------------------------------------
        valid_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()].copy()
        
        valid_df['Action'] = valid_df['Action'].astype(str)
        valid_df['Tags'] = valid_df['Tags'].fillna('').astype(str)
        
        # حساب المسافة التقدمية للأمام (الفرق على محور X)
        valid_df['prog_distance'] = valid_df['x2_scaled'] - valid_df['x_scaled']

        # -------------------------------------------------------------
        # 5. القوائم المنسدلة (تأكيد السطر السليم لفلتر اللاعبين)
        # -------------------------------------------------------------
        st.subheader("🎯 فلاتر التحليل الهجومي المتقدم")
        
        col1, col2 = st.columns(2)
        
        with col1:
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
            # تم تأكيد السطر كاملاً هنا لمنع الـ SyntaxError
            players_list = ["كل اللاعبين"] + list(valid_df['Player'].dropna().unique())
            selected_player = st.selectbox("فلترة بحسب اللاعب:", players_list)

        # -------------------------------------------------------------
        # 6. تطبيق الفلترة الصارمة بناءً على اختيارك
        # -------------------------------------------------------------
        filtered_df = valid_df.copy()
        
        if selected_player != "كل اللاعبين":
            filtered_df = filtered_df[filtered_df['Player'] == selected_player]

        # فلترة نوع الأكشن المطلوب
        if selected_action == "تمريرة عادية (Normal Pass)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Pass', case=False) & 
                ~filtered_df['Action'].str.contains('Cross|Corner', case=False) &
                ~filtered_df['Tags'].str.contains('through|key', case=False) &
                (filtered_df['prog_distance'] < 12)
            ]
            color_theme = '#00ffcc'
            
        elif selected_action == "تمريرة تقديمية (Progressive Pass)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Pass', case=False) & 
                ~filtered_df['Action'].str.contains('Corner', case=False) &
                (filtered_df['prog_distance'] >= 12)
            ]
            color_theme = '#ff9900'
            
        elif selected_action == "ثرو باص (Through Ball)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Through|Key', case=False) | 
                filtered_df['Tags'].str.contains('through|key|Behind', case=False)
            ]
            color_theme = '#cc00ff'
            
        elif selected_action == "عرضية (Cross)":
            filtered_df = filtered_df[filtered_df['Action'].str.contains('Cross', case=False)]
            color_theme = '#ffff00'
            
        elif selected_action == "كورنر (Corner)":
            filtered_df = filtered_df[filtered_df['Action'].str.contains('Corner', case=False)]
            color_theme = '#00f0ff'
            
        elif selected_action == "تسديدة (Shot)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Shot', case=False) & 
                ~filtered_df['Tags'].str.contains('goal|Goal', case=False)
            ]
            color_theme = '#ff3366'
            
        elif selected_action == "هدف (Goal)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Goal', case=False) | 
                filtered_df['Tags'].str.contains('goal', case=False)
            ]
            color_theme = '#00ff00'

        # -------------------------------------------------------------
        # 7. رسم
