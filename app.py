import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="TootScouting Pro Analysis", layout="wide")

st.title("⚽ TootScouting | منصة التحليل الاحترافي المتقدمة")

uploaded_file = st.sidebar.file_uploader("ارفع ملف الـ Actions (CSV)", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()
    
    # تحويل الإحداثيات لمقياس الملعب
    if 'x start' in df.columns:
        df['x_scaled'] = df['x start'] * 120
        df['y_scaled'] = df['y start'] * 80
        df['x_end_scaled'] = df['x end'] * 120
        df['y_end_scaled'] = df['y end'] * 80

    # --- القائمة الجانبية للفلترة ---
    st.sidebar.header("لوحة التحكم في الفلاتر")
    
    # 1. فلتر اللاعب
    player_list = sorted(df['player'].dropna().unique().tolist())
    selected_player = st.sidebar.selectbox("اختر اللاعب", player_list)
    player_df = df[df['player'] == selected_player].copy()

    # 2. فلتر نوع الإجراء (الالتحامات، الفاولات، الدريبل...)
    action_list = sorted(player_df['action'].unique().tolist())
    selected_action = st.sidebar.multiselect("اختر نوع الإجراء (Actions)", action_list, default=["pass"])

    # فلترة البيانات بناءً على الاختيارات
    filtered_df = player_df[player_df['action'].isin(selected_action)]

    # --- تبويبات العرض ---
    tab1, tab2 = st.tabs(["📊 الإحصائيات المفلترة", "🏟️ التحليل التكتيكي (الخرائط)"])

    with tab1:
        st.subheader(f"تحليل أداء: {selected_player}")
        st.write(f"عدد الإجراءات المختارة: {len(filtered_df)}")
        st.dataframe(filtered_df)

    with tab2:
        # رسم الملعب بالتنسيق اللي طلبته
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc', 
                      linestyle='--', linewidth=1, goal_linestyle='-')
        fig, ax = pitch.draw(figsize=(12, 8))

        # --- رسم التمريرات (أسهم ملونة) ---
        passes = filtered_df[filtered_df['action'].str.contains('pass', case=False, na=False)]
        
        for i, row in passes.iterrows():
            # تحديد اللون بناءً على الكلمة الموجودة في Tags (success أو failed)
            color = 'green' if 'success' in str(row['tags']).lower() else 'red'
            
            # رسم السهم
            pitch.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, 
                         width=2, headwidth=3, headlength=3, color=color, ax=ax, alpha=0.8)

        # --- رسم الإجراءات الأخرى (نقط ملونة) ---
        # التحامات هوائية، أرضية، فاولات، دريبل
        others = filtered_df[~filtered_df['action'].str.contains('pass', case=False, na=False)]
        
        if not others.empty:
            pitch.scatter(others.x_scaled, others.y_scaled, s=150, edgecolors='white', 
                          c='#f39c12', marker='o', ax=ax, label='Other Actions')

        st.pyplot(fig)
        st.write("💡 **مفتاح الخريطة:** الأسهم الخضراء (تمريرة صحيحة)، الأسهم الحمراء (تمريرة خاطئة)، النقاط الصفراء (إجراءات أخرى).")

else:
    st.info("👋 ارفع ملف الـ Actions للبدء في التحليل التفاعلي.")
