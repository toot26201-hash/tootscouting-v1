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
        
        # معالجة البيانات الصالحة
        valid_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()].copy()
        valid_df['Action'] = valid_df['Action'].astype(str).str.strip()
        valid_df['Player'] = valid_df['Player'].astype(str).str.strip()

        # -------------------------------------------------------------
        # 4. الفلاتر الذكية (متعددة الاختيارات وقراءة مباشرة من ملفك)
        # -------------------------------------------------------------
        st.subheader("🎯 فلاتر التحليل الهجومي المتقدم")
        col1, col2 = st.columns(2)
        
        with col2:
            # فلتر اللاعبين
            players_list = ["كل اللاعبين"] + list(valid_df['Player'].dropna().unique())
            selected_player = st.selectbox("فلترة بحسب اللاعب:", players_list)
            
        # تطبيق فلتر اللاعب أولاً لتحديث قائمة الأكشن المتاحة له
        temp_df = valid_df.copy()
        if selected_player != "كل اللاعبين":
            temp_df = temp_df[temp_df['Player'] == selected_player]
            
        with col1:
            # هنا الميزة الأولى: الكود بيجيب المسميات الفعلية من ملفك عشان تضمن إنها تسمع
            available_actions = list(temp_df['Action'].dropna().unique())
            
            # الميزة الثانية: استخدام multiselect لاختيار أكثر من أكشن معاً
            selected_actions = st.multiselect(
                "اختر الأكشنز الهجومية (يمكنك اختيار أكثر من نوع):", 
                options=available_actions,
                default=available_actions[:2] if available_actions else [] # يختار أول عنصرين تلقائياً كبداية
            )

        # -------------------------------------------------------------
        # 5. تطبيق الفلترة النهائية بناءً على الاختيارات
        # -------------------------------------------------------------
        filtered_df = temp_df.copy()
        
        if selected_actions:
            filtered_df = filtered_df[filtered_df['Action'].isin(selected_actions)]
        else:
            # لو المستخدم قفل كل الاختيارات، بنخلي الداتا فارغة عشان يظهر ملعب نظيف
            filtered_df = pd.DataFrame(columns=filtered_df.columns)

        # -------------------------------------------------------------
        # 6. رسم الملعب التكتيكي والأحداث
        # -------------------------------------------------------------
        st.subheader("🏟️ خريطة الفاعلية التكتيكية المحدثة")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        if not filtered_df.empty:
            # الكود هنا بذكاء هيفصل الأحداث اللي ليها نقطة نهاية (تمريرات، عرضيات) عن الأحداث الثابتة (تسديدات، أهداف)
            # الشرط: إذا كان x2 موجود ولا يساوي 0 أو نفس نقطة البداية
            has_end = filtered_df['x2_scaled'].notna() & (filtered_df['x2_scaled'] != 0) & (filtered_df['x2_scaled'] != filtered_df['x_scaled'])
            
            arrows_df = filtered_df[has_end]
            dots_df = filtered_df[~has_end]
            
            # 1. رسم الأحداث المتحركة بأسهم (تمريرات، عرضيات، إلخ)
            if not arrows_df.empty:
                pitch.arrows(
                    arrows_df['x_scaled'], arrows_df['y_scaled'],
                    arrows_df['x2_scaled'], arrows_df['y2_scaled'],
                    width=2, headwidth=3, headlength=3,
                    color='#00ffcc', alpha=0.8, ax=ax
                )
                pitch.scatter(
                    arrows_df['x_scaled'], arrows_df['y_scaled'],
                    color='#00ffcc', s=40, edgecolors='#ffffff', zorder=3, ax=ax
                )
            
            # 2. رسم الأحداث الثابتة بنقاط مميزة (تسديدات، أهداف، إلخ)
            if not dots_df.empty:
                # لو الأكشن مكتوب فيه هدف هنخليه نجمة خضراء، غير كده نقطة حمراء
                for idx, row in dots_df.iterrows():
                    is_goal = 'goal' in str(row['Action']).lower() or 'هدف' in str(row['Action'])
                    marker_style = '*' if is_goal else 'o'
                    marker_color = '#00ff00' if is_goal else '#ff3366'
                    marker_size = 250 if is_goal else 120
                    
                    pitch.scatter(
                        row['x_scaled'], row['y_scaled'],
                        color=marker_color, s=marker_size, 
                        marker=marker_style, edgecolors='#ffffff', zorder=4, ax=ax
                    )
            
            st.pyplot(fig)
            st.success(f"تم عرض {len(filtered_df)} حدث على الملعب بناءً على الفلاتر المختارة.")
            plt.close(fig)
            
        else:
            st.pyplot(fig)
            st.warning("الملعب فارغ حالياً، يرجى اختيار أكشن واحد على الأقل من القائمة ليظهر على الملعب.")
            plt.close(fig)

    else:
        st.error("عذراً، لم نتمكن من العثور على أعمدة الإحداثيات المطلوبة (X Start, Y Start).")

else:
    st.info("يرجى رفع ملف البيانات لبدء التحليل الهجومي المتقدم.")
