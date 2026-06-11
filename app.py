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
        
        with st.expander("معاينة جدول البيانات المُعدلة"):
            st.write(df[['Player', 'Action', 'Event Type', 'x_scaled', 'y_scaled']].head(10))
        
        # -------------------------------------------------------------
        # 4. تقسيم الفلاتر (القوائم المنسدلة للأحداث الهجومية والدفاعية)
        # -------------------------------------------------------------
        st.subheader("📊 فلاتر الخريطة التكتيكية")
        
        # فلترة البيانات التي تحتوي على إحداثيات صالحة فقط للرسم
        valid_events_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()]
        
        # تحديد الكلمات الدلالية لتصنيف الأحداث (يمكنك تعديلها حسب مسميات ملفك)
        attacking_keywords = ['Pass', 'Shot', 'Cross', 'Dribble', 'Kick-off', 'Corner', 'Free-kick']
        defensive_keywords = ['Tackle', 'Interception', 'Clearance', 'Block', 'Recovery', 'Foul Committed', 'Challenge']
        
        # استخراج الأحداث المتاحة فعلياً في الملف بناءً على التصنيف
        available_actions = valid_events_df['Action'].dropna().unique()
        
        actual_attacking = [act for act in available_actions if any(key.lower() in act.lower() for key in attacking_keywords)]
        actual_defensive = [act for act in available_actions if any(key.lower() in act.lower() for key in defensive_keywords)]
        
        # إنشاء الأعمدة في Streamlit لوضع القوائم المنسدلة بجانب بعضها
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # قائمة اختيار نوع التحليل الرئيسي
            analysis_type = st.radio("اختر نوع التحليل:", ["كل الأحداث", "أكشن هجومي ⚔️", "أكشن دفاعي 🛡️"])
        
        filtered_df = valid_events_df.copy()
        color_theme = '#00ffcc' # اللون الافتراضي (الفسفوري)
        
        if analysis_type == "أكشن هجومي ⚔️":
            with col2:
                selected_attack = st.selectbox("اختر الأكشن الهجومي:", ["كل الهجوم"] + actual_attacking)
            if selected_attack != "كل الهجوم":
                filtered_df = filtered_df[filtered_df['Action'] == selected_attack]
            else:
                filtered_df = filtered_df[filtered_df['Action'].isin(actual_attacking)]
            color_theme = '#00ffcc' # لون مميز للهجوم (أخضر/فسفوري)
            
        elif analysis_type == "أكشن دفاعي 🛡️":
            with col3:
                selected_defense = st.selectbox("اختر الأكشن الدفاعي:", ["كل الدفاع"] + actual_defensive)
            if selected_defense != "كل الدفاع":
                filtered_df = filtered_df[filtered_df['Action'] == selected_defense]
            else:
                filtered_df = filtered_df[filtered_df['Action'].isin(actual_defensive)]
            color_theme = '#ff3366' # لون مميز للدفاع (أحمر/وردي)

        # فلتر إضافي لاختيار اللاعب (اختياري لزيادة التحكم)
        players_list = ["كل اللاعبين"] + list(filtered_df['Player'].dropna().unique())
        selected_player = st.selectbox("فلترة بحسب اللاعب (اختياري):", players_list)
        if selected_player != "كل اللاعبين":
            filtered_df = filtered_df[filtered_df['Player'] == selected_player]

        # -------------------------------------------------------------
        # 5. رسم الملعب والأحداث المفلترة
        # -------------------------------------------------------------
        st.subheader(f"🏟️ خريطة الفاعلية: {analysis_type}")
        
        if not filtered_df.empty:
            # رسم الملعب
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
            fig, ax = pitch.draw(figsize=(12, 8))
            
            # التحقق إذا كان الحدث له نقطة نهاية (مثل التمريرات والعرضيات) لرسم سهم
            # أو مجرد نقطة ثابتة (مثل قطع الكرة أو التاكل) لرسم نقطة فقط
            has_end_coords = filtered_df['x2_scaled'].notna() & filtered_df['y2_scaled'].notna() & (filtered_df['x_scaled'] != filtered_df['x2_scaled'])
            
            arrows_df = filtered_df[has_end_coords]
            scatters_df = filtered_df[~has_end_coords]
            
            # 1. رسم الأحداث التي بها حركة (أسهم)
            if not arrows_df.empty:
                pitch.arrows(
                    arrows_df['x_scaled'], arrows_df['y_scaled'],
                    arrows_df['x2_scaled'], arrows_df['y2_scaled'],
                    width=2, headwidth=3, headlength=3,
                    color=color_theme, alpha=0.7, ax=ax
                )
                pitch.scatter(
                    arrows_df['x_scaled'], arrows_df['y_scaled'],
                    color=color_theme, s=40, edgecolors='#ffffff', zorder=3, ax=ax
                )
            
            # 2. رسم الأحداث الثابتة (نقاط فقط مثل التاكل وقطع الكرة)
            if not scatters_df.empty:
                pitch.scatter(
                    scatters_df['x_scaled'], scatters_df['y_scaled'],
                    color=color_theme, s=80, edgecolors='#ffffff', marker='X' if analysis_type == "أكشن دفاعي 🛡️" else 'o', zorder=3, ax=ax
                )
            
            fig.patch.set_facecolor('#1a1a1a')
            st.pyplot(fig)
            st.caption(f"تم عرض {len(filtered_df)} حدث على الخريطة بنجاح.")
        else:
            st.warning("لا توجد بيانات متاحة تطابق الفلاتر المحددة.")

    else:
        st.error("عذراً، لم نتمكن من العثور على أعمدة الإحداثيات المطلوبة (X Start, Y Start).")

else:
    st.info("يرجى رفع ملف البيانات لبدء التحليل.")
