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
        # 7. رسم الملعب التكتيكي (يُرسم دائماً وتظهر الأحداث فوقه)
        # -------------------------------------------------------------
        st.subheader(f"🏟️ خريطة الفاعلية")
        
        # إنشاء الرسم البياني للملعب (يتم إنشاؤه في كل الأحوال حتى لو البيانات فارغة)
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        fig, ax = pitch.draw(figsize=(12, 8))
        fig.patch.set_facecolor('#1a1a1a')
        
        if not filtered_df.empty:
            # التحقق من وجود إحداثيات نهاية لرسم الأسهم (مثل التمريرات والعرضيات)
            # إذا كانت إحداثيات النهاية موجودة وتختلف عن البداية، نرسم سهماً
            has_end = filtered_df['x2_scaled'].notna() & filtered_df['y2_scaled'].notna() & (filtered_df['x2_scaled'] != 0)
            
            arrows_df = filtered_df[has_end]
            dots_df = filtered_df[~has_end]
            
            # 1. رسم الأسهم للأحداث المتحركة (تمريرات، عرضيات)
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
            
            # 2. رسم النقاط الثابتة (تسديدات، أهداف، أحداث بدون إحداثيات نهاية)
            if not dots_df.empty:
                pitch.scatter(
                    dots_df['x_scaled'], dots_df['y_scaled'],
                    color='#ff3366', s=100, marker='o', edgecolors='#ffffff', zorder=4, ax=ax
                )
                
            st.pyplot(fig)
            st.success(f"تم عرض {len(filtered_df)} حدث على الملعب بنجاح.")
            
        else:
            # في حال كانت الفلترة فارغة، يُرسم الملعب فارغاً مع رسالة تحذيرية بدلاً من الاختفاء
            st.pyplot(fig)
            st.warning(f"الملعب معروض بالأعلى، لكن لا توجد أحداث مطابقة للفلتر الحالي: [{selected_main}] لهذا اللاعب.")

    else:
        st.error("عذراً، لم نتمكن من العثور على أعمدة الإحداثيات المطلوبة (X Start, Y Start).")

else:
    st.info("يرجى رفع ملف البيانات لبدء التحليل الهجومي.")
