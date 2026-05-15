import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="TootScouting Dashboard", layout="wide")

st.title("⚽ TootScouting | منصة تحليل اللاعبين")

# 1. رفع الملف
uploaded_file = st.sidebar.file_uploader("ارفع ملف الـ Actions (CSV)", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # تنظيف مسميات الأعمدة عشان لو فيها مسافات أو حروف كبيرة
    df.columns = df.columns.str.strip().str.lower()
    
    # 2. إضافة قائمة اختيار اللاعبين (ده الفلتر اللي سألت عليه)
    # بيفترض إن عندك عمود في الإكسيل اسمه 'player'
    if 'player' in df.columns:
        player_list = df['player'].unique().tolist() # بيطلع كل الأسماء اللي في الملف
        selected_player = st.sidebar.selectbox("اختر اللاعب", player_list)
        
        # هنا بنقول للموقع: "خلي البيانات للاعب اللي اخترناه بس"
        player_df = df[df['player'] == selected_player]
    else:
        st.sidebar.error("ملحوظة: عمود 'player' غير موجود في الملف")
        player_df = df

    # 3. عرض النتائج للاعب المختار
    tab1, tab2 = st.tabs(["📌 ملخص الأداء", "🏟️ الخرائط التكتيكية"])

    with tab1:
        st.subheader(f"بيانات اللاعب: {selected_player if 'player' in df.columns else 'العامة'}")
        st.dataframe(player_df) # هيعرض جدول فيه تاقات اللاعب ده بس

    with tab2:
        st.subheader("خريطة التمركز (Heatmap)")
        if 'x' in df.columns and 'y' in df.columns:
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
            fig, ax = pitch.draw(figsize=(10, 7))
            
            # رسم تحركات اللاعب المختار بس
            pitch.kdeplot(player_df.x, player_df.y, ax=ax, fill=True, cmap='hot', alpha=0.5)
            st.pyplot(fig)
        else:
            st.warning("الملف لا يحتوي على إحداثيات x و y")
else:
    st.info("ارفع ملف الـ Actions عشان تبدأ تختار اللاعبين وتشوف خرائطهم.")
