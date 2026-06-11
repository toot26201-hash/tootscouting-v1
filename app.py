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
        # 4. معالجة البيانات الصالحة
        # -------------------------------------------------------------
        valid_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()].copy()
        valid_df['Action'] = valid_df['Action'].astype(str).str.strip()
        valid_df['Tags'] = valid_df['Tags'].fillna('').astype(str)
        
        # حساب المسافة التقدمية للأمام (الفرق على محور X)
        valid_df['prog_distance'] = valid_df['x2_scaled'] - valid_df['x_scaled']

        # -------------------------------------------------------------
        # 5. القوائم المنسدلة الكاملة (كل طلباتك هنا)
        # -------------------------------------------------------------
        st.subheader("🎯 فلاتر التحليل الهجومي المتقدم")
        col1, col2 = st.columns(2)
        
        with col1:
            attack_options = [
                "كل التمريرات والأحداث",
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
            players_list = ["كل اللاعبين"] + list(valid_df['Player'].dropna().unique())
            selected_player = st.selectbox("فلترة بحسب اللاعب:", players_list)

        # -------------------------------------------------------------
        # 6. تطبيق الفلترة الذكية بناءً على اختيارك
        # -------------------------------------------------------------
        filtered_df = valid_df.copy()
        
        if selected_player != "كل اللاعبين":
            filtered_df = filtered_df[filtered_df['Player'] == selected_player]

        # تحديد اللون الافتراضي (فسفوري)
        color_theme = '#00ffcc'
        
        # شروط الفلترة لكل خيار
        if selected_action == "تمريرة عادية (Normal Pass)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Pass', case=False) & 
                ~filtered_df['Action'].str.contains('Cross|Corner', case=False) &
                ~filtered_df['Tags'].str.contains('through|key', case=False) &
                (filtered_df['prog_distance'] < 12)
            ]
            color_theme = '#00ffcc' # فسفوري
            
        elif selected_action == "تمريرة تقديمية (Progressive Pass)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Pass', case=False) & 
                ~filtered_df['Action'].str.contains('Corner', case=False) &
                (filtered_df['prog_distance'] >= 12)
            ]
            color_theme = '#ff9900' # برتقالي ناري
            
        elif selected_action == "ثرو باص (Through Ball)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Through|Key|ثرو', case=False) | 
                filtered_df['Tags'].str.contains('through|key|Behind', case=False)
            ]
            color_theme = '#cc00ff' # بنفسجي
            
        elif selected_action == "عرضية (Cross)":
            filtered_df = filtered_df[filtered_df['Action'].str.contains('Cross|عرضية', case=False)]
            color_theme = '#ffff00' # أصفر للعرضيات
            
        elif selected_action == "كورنر (Corner)":
            filtered_df = filtered_df[filtered_df['Action'].str.contains('Corner|كورنر|ركنية', case=False)]
            color_theme = '#00f0ff' # أزرق سماوي
            
        elif selected_action == "تسديدة (Shot)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Shot|تسديد|شوط', case=False) & 
                ~filtered_df['Tags'].str.contains('goal|Goal', case=False) &
                ~filtered_df['Action'].str.contains('Goal', case=False)
            ]
            color_theme = '#ff3366' # أحمر للتسديدات
            
        elif selected_action == "هدف (Goal)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Goal|هدف', case=False) | 
                filtered_df['Tags'].str.contains('goal', case=False)
            ]
            color_theme = '#00ff00' # أخضر صريح للأهداف

        # -------------------------------------------------------------
        # 7. رسم الملعب التكتيكي (يُرسم دائماً وتظهر الأحداث فوقه)
        # -------------------------------------------------------------
        st.subheader(f"🏟️ خريطة الفاعلية التكتيكية: {selected_action}")
        
        # توليد خطوط الملعب بشكل ثابت وصحيح أولاً لضمان الظهور
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        if not filtered_df.empty:
            # نحدد الأحداث التي تحتاج سهم حركة (تمريرات، عرضيات، كورنر)
            movement_actions = ["كل التمريرات", "Normal Pass", "Progressive Pass", "Through Ball", "Cross", "Corner"]
            is_movement = any(x in selected_action for x in movement_actions) or (selected_action == "كل التمريرات والأحداث")
            
            if is_movement:
                # التحقق من وجود إحداثيات نهاية صالحة لرسم السهم
                has_end = filtered_df['x2_scaled'].notna() & filtered_df['y2_scaled'].notna() & (filtered_df['x2_scaled'] != 0)
                arrows_df = filtered_df[has_end]
                dots_df = filtered_df[~has_end]
                
                # رسم الأسهم للتمريرات والعرضيات
                if not arrows_df.empty:
                    pitch.arrows(
                        arrows_df['x_scaled'], arrows_df['y_scaled'],
                        arrows_df['x2_scaled'], arrows_df['y2_scaled'],
                        width=2, headwidth=3, headlength=3,
                        color=color_theme, alpha=0.8, ax=ax
                    )
                    pitch.scatter(
                        arrows_df['x_scaled'], arrows_df['y_scaled'],
                        color=color_theme, s=40, edgecolors='#ffffff', zorder=3, ax=ax
                    )
                
                # إذا كان هناك أحداث حركة لكن بدون إحداثيات نهاية بالملف
                if not dots_df.empty:
                    pitch.scatter(
                        dots_df['x_scaled'], dots_df['y_scaled'],
                        color=color_theme, s=60, edgecolors='#ffffff', zorder=3, ax=ax
                    )
            else:
                # للتسديدات والأهداف: رسم مكان الحدث بشكل مميز وثابت
                marker_type = '*' if "Goal" in selected_action else 'o'
                size_type = 200 if "Goal" in selected_action else 100
                
                pitch.scatter(
                    filtered_df['x_scaled'], filtered_df
