import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import os

st.set_page_config(page_title="TootScouting Tactical Master", layout="wide")

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    # 1. قراءة الملف مع معالجة الأعمدة
    try:
        # قراءة الملف وإجبار التنسيق على التعرف على الفواصل
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip() # إزالة أي مسافات من أسماء الأعمدة

        # 2. خطوة الإصلاح الجوهري: ربط أعمدة ملفك بما يتوقعه الكود
        # نقوم بإنشاء الأعمدة المطلوبة مباشرة من بياناتك الحقيقية
        if 'X1' in df.columns and 'Y1' in df.columns:
            df['x_scaled'] = df['X1'] * 120
            df['y_scaled'] = df['Y1'] * 80
            
            if 'X2' in df.columns and 'Y2' in df.columns:
                df['x_end_scaled'] = df['X2'] * 120
                df['y_end_scaled'] = df['Y2'] * 80
            else:
                df['x_end_scaled'] = df['x_scaled']
                df['y_end_scaled'] = df['y_scaled']
        
        # التأكد من أسماء الأعمدة (Action, Player, Tags)
        rename_map = {c: 'Action' for c in df.columns if 'action' in c.lower()}
        rename_map.update({c: 'Player' for c in df.columns if 'player' in c.lower()})
        rename_map.update({c: 'Tags' for c in df.columns if 'tag' in c.lower()})
        df = df.rename(columns=rename_map)
        
        st.sidebar.success("✅ تم تحميل البيانات ومعالجة الإحداثيات بنجاح!")

        # 3. واجهة العرض البسيطة للتأكد من العمل
        players = df['Player'].dropna().unique().tolist()
        sel_player = st.sidebar.selectbox("🎯 اختر اللاعب", players)
        p_df = df[df['Player'] == sel_player].copy()

        # الرسم
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # التأكد من أن الأعمدة موجودة قبل الرسم
        if 'x_scaled' in p_df.columns:
            sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, ax=ax, cmap='viridis')
            st.pyplot(fig)
        else:
            st.error("لم يتم العثور على إحداثيات (X1, Y1). تحقق من ملف الـ CSV.")

    except Exception as e:
        st.error(f"خطأ غير متوقع: {e}")
else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
