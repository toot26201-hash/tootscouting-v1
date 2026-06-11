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
        
        # حساب المسافة التقدمية للأمام
        valid_df['prog_distance'] = valid_df['x2_scaled'] - valid_df['x_scaled']

        # -------------------------------------------------------------
        # 5. القوائم المنسدلة الكاملة
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

        color_theme = '#00ffcc'
        
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
                filtered_df['Action'].str.contains('Through|Key|ثرو', case=False) | 
                filtered_df['Tags'].str.contains('through|key|Behind', case=False)
            ]
            color_theme = '#cc00ff'
            
        elif selected_action == "عرضية (Cross)":
            filtered_df = filtered_df[filtered_df['Action'].str.contains('Cross|عرضية', case=False)]
            color_theme = '#ffff00'
            
        elif selected_action == "كورنر (Corner)":
            filtered_df = filtered_df[filtered_df['Action'].str.contains('Corner|كورنر|ركنية', case=False)]
            color_theme = '#00f0ff'
            
        elif selected_action == "تسديدة (Shot)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Shot|تسديد|شوط', case=False) & 
                ~filtered_df['Tags'].str.contains('goal|Goal', case=False) &
                ~filtered_df['Action'].str.contains('Goal', case=False)
            ]
            color_theme = '#ff3366'
            
        elif selected_action == "هدف (Goal)":
            filtered_df = filtered_df[
                filtered_df['Action'].str.contains('Goal|هدف', case=False) | 
                filtered_df['Tags'].str.contains('goal', case=False)
            ]
            color_theme = '#00ff00'

        # -------------------------------------------------------------
        # 7. رسم الملعب التكتيكي (صياغة مبسطة ومحمية من الـ SyntaxError)
        # -------------------------------------------------------------
        st.subheader(f"🏟️ خريطة الفاعلية التكتيكية: {selected_action}")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        if not filtered_df.empty:
            movement_actions = ["Normal Pass", "Progressive Pass", "Through Ball", "Cross", "Corner"]
            is_movement = any(x in selected_action for x in movement_actions) or (selected_action == "كل التمريرات والأحداث")
            
            if is_movement:
                # فصلنا الداتا اللي فيها أسهم واضحة
                has_end = filtered_df['x2_scaled'].notna() & filtered_df['y2_scaled'].notna() & (filtered_df['x2_scaled'] != 0)
                arrows_df = filtered_df[has_end]
                dots_df = filtered_df[~has_end]
                
                if not arrows_df.empty:
                    pitch.arrows(arrows_df['x_scaled'], arrows_df['y_scaled'], arrows_df['x2_scaled'], arrows_df['y2_scaled'], width=2, headwidth=3, headlength=3, color=color_theme, alpha=0.8, ax=ax)
                    pitch.scatter(arrows_df['x_scaled'], arrows_df['y_scaled'], color=color_theme, s=40, edgecolors='#ffffff', zorder=3, ax=ax)
                
                if not dots_df.empty:
                    pitch.scatter(dots_df['x_scaled'], dots_df['y_scaled'], color=color_theme, s=60, edgecolors='#ffffff', zorder=3, ax=ax)
            else:
                # للتسديدات والأهداف: تحديد الماركر والحجم في متغيرات منفصلة تماماً
                is_goal = "Goal" in selected_action
                
                if is_goal:
                    pitch.scatter(filtered_df['x_scaled'], filtered_df['y_scaled'], color=color_theme, s=200, marker='*', edgecolors='#ffffff', zorder=4, ax=ax)
                else:
                    pitch.scatter(filtered_df['x_scaled'], filtered_df['y_scaled'], color=color_theme, s=100, marker='o', edgecolors='#ffffff', zorder=4, ax=ax)
            
            st.pyplot(fig)
            st.success(f"تم العثور على {len(filtered_df)} حدث وعرضه بنجاح.")
            plt.close(fig)
            
        else:
            st.pyplot(fig)
            st.warning(f"الملعب معروض بالأعلى، لكن لا توجد بيانات مسجلة في هذا الملف تحت تصنيف: {selected_action}")
            plt.close(fig)

    else:
        st.error("عذراً، لم نتمكن من العثور على أعمدة الإحداثيات المطلوبة (X Start, Y Start).")

else:
    st.info("يرجى رفع ملف البيانات لبدء التحليل الهجومي المتقدم.")
