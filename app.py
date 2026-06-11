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
        
        # معالجة البيانات وتحويل الأعمدة لنصوص
        valid_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()].copy()
        valid_df['Action_raw'] = valid_df['Action'].astype(str).str.strip()
        valid_df['Tags'] = valid_df['Tags'].fillna('').astype(str)
        valid_df['Player'] = valid_df['Player'].astype(str).str.strip()
        
        # حساب المسافة التقدمية للأمام
        valid_df['prog_distance'] = valid_df['x2_scaled'] - valid_df['x_scaled']

        # -------------------------------------------------------------
        # 4. تصنيف الأرقام والمسميات إلى أسماء أكشنز واضحة
        # -------------------------------------------------------------
        conditions = [
            valid_df['Action_raw'].str.contains('Goal|هدف', case=False) | valid_df['Tags'].str.contains('goal', case=False),
            valid_df['Action_raw'].str.contains('Shot|تسديد|شوط', case=False),
            valid_df['Action_raw'].str.contains('Corner|كورنر|ركنية', case=False),
            valid_df['Action_raw'].str.contains('Cross|عرضية', case=False),
            valid_df['Action_raw'].str.contains('Through|Key|ثرو', case=False) | valid_df['Tags'].str.contains('through|key|Behind', case=False),
            (valid_df['Action_raw'].str.contains('Pass|تمرير', case=False) | valid_df['Action_raw'].str.isnumeric()) & (valid_df['prog_distance'] >= 12),
            valid_df['Action_raw'].str.contains('Pass|تمرير', case=False) | valid_df['Action_raw'].str.isnumeric()
        ]
        
        choices = [
            "هدف (Goal)",
            "تسديدة (Shot)",
            "كورنر (Corner)",
            "عرضية (Cross)",
            "ثرو باص (Through Ball)",
            "تمريرة تقديمية (Progressive Pass)",
            "تمريرة عادية (Normal Pass)"
        ]
        
        valid_df['Clean_Action'] = np.select(conditions, choices, default="أحداث أخرى (Other)")

        # -------------------------------------------------------------
        # 5. القوائم المنسدلة (اختيار الأسماء بـ Multiselect)
        # -------------------------------------------------------------
        st.subheader("🎯 فلاتر التحليل الهجومي المتقدم")
        col1, col2 = st.columns(2)
        
        with col2:
            players_list = ["كل اللاعبين"] + list(valid_df['Player'].dropna().unique())
            selected_player = st.selectbox("فلترة بحسب اللاعب:", players_list)
            
        temp_df = valid_df.copy()
        if selected_player != "كل اللاعبين":
            temp_df = temp_df[temp_df['Player'] == selected_player]
            
        with col1:
            display_actions = list(temp_df['Clean_Action'].unique())
            selected_actions = st.multiselect(
                "اختر الأكشنز الهجومية المطلوبة (يمكنك اختيار أكثر من نوع):", 
                options=display_actions,
                default=display_actions if display_actions else []
            )

        # -------------------------------------------------------------
        # 6. تطبيق الفلترة النهائية بناءً على الاختيارات
        # -------------------------------------------------------------
        if selected_actions:
            filtered_df = temp_df[temp_df['Clean_Action'].isin(selected_actions)]
        else:
            filtered_df = pd.DataFrame(columns=temp_df.columns)

        # -------------------------------------------------------------
        # 7. رسم الملعب التكتيكي والأحداث
        # -------------------------------------------------------------
        st.subheader("🏟️ خريطة الفاعلية التكتيكية")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        if not filtered_df.empty:
            movement_labels = [
                "تمريرة عادية (Normal Pass)", 
                "تمريرة تقديمية (Progressive Pass)", 
                "ثرو باص (Through Ball)", 
                "عرضية (Cross)", 
                "كورنر (Corner)"
            ]
            
            arrows_df = filtered_df[filtered_df['Clean_Action'].isin(movement_labels)]
            dots_df = filtered_df[~filtered_df['Clean_Action'].isin(movement_labels)]
            
            # 1. رسم الأسهم (التمريرات، العرضيات، الكورنرات)
            if not arrows_df.empty:
                for act in arrows_df['Clean_Action'].unique():
                    sub_arrow = arrows_df[arrows_df['Clean_Action'] == act]
                    
                    if "Normal" in act: color = '#00ffcc'
                    elif "Progressive" in act: color = '#ff9900'
                    elif "Through" in act: color = '#cc00ff'
                    elif "Cross" in act: color = '#ffff00'
                    else: color = '#00f0ff'
                    
                    pitch.arrows(
                        sub_arrow['x_scaled'], sub_arrow['y_scaled'], 
                        sub_arrow['x2_scaled'], sub_arrow['y2_scaled'], 
                        width=2, headwidth=3, headlength=3, 
                        color=color, alpha=0.8, ax=ax
                    )
                    pitch.scatter(
                        sub_arrow['x_scaled'], sub_arrow['y_scaled'], 
                        color=color, s=40, edgecolors='#ffffff', zorder=3, ax=ax
                    )
            
            # 2. رسم النقاط الثابتة (التسديدات والأهداف) - تم تبسيط الأسطر تماماً هنا لمنع القطع
            if not dots_df.empty:
                for idx, row in dots_df.iterrows():
                    if "Goal" in row['Clean_Action']:
                        m_color = '#00ff00'
                        m_style = '*'
                        m_size = 250
                    else:
                        m_color = '#ff3366'
                        m_style = 'o'
                        m_size = 120
                        
                    pitch.scatter(
                        row['x_scaled'], 
                        row['y_scaled'], 
                        color=m_color, 
                        s=m_size, 
                        marker=m_style, 
                        edgecolors='#ffffff', 
                        zorder=4, 
                        ax=ax
                    )
            
            st.pyplot(fig)
            st.success(f"تم عرض {len(filtered_df)} حدث بنجاح على الملعب بناءً على الفلاتر.")
            plt.close(fig)
            
        else:
            st.pyplot(fig)
            st.warning("الملعب فارغ حالياً، يرجى اختيار مسمى أكشن واحد على الأقل ليتم رسمه.")
            plt.close(fig)

    else:
        st.error("عذراً، لم نتمكن من العثور على أعمدة الإحداثيات المطلوبة (X Start, Y Start).")

else:
    st.info("يرجى رفع ملف البيانات لبدء التحليل الهجومي المتقدم.")
