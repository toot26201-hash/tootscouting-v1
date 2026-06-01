import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import os
import matplotlib.colors as mcolors
import base64
import numpy as np

# --- إعداد الصفحة ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# --- الدوال الأساسية ---
def process_data(uploaded_file):
    # محاولة قراءة الملف
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
    except Exception as e:
        st.error(f"خطأ في قراءة ملف CSV: {e}")
        return None

    # تنظيف أسماء الأعمدة من المسافات
    df.columns = df.columns.str.strip()

    # التعامل مع الأعمدة المكررة (إضافة رقم تكراري)
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [f"{dup}_{i}" if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols

    # إعادة التسمية التلقائية (Mapping)
    mapping = {}
    for col in df.columns:
        c = col.lower()
        if 'action' in c or 'event' in c: mapping[col] = 'Action'
        elif 'player' in c: mapping[col] = 'Player'
        elif 'tag' in c: mapping[col] = 'Tags'
        elif c == 'x': mapping[col] = 'x_start'
        elif c == 'y': mapping[col] = 'y_start'
    
    df = df.rename(columns=mapping)
    return df

# --- واجهة التطبيق ---
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = process_data(uploaded_file)
    
    if df is not None:
        # فحص وجود الأعمدة الأساسية
        if 'Action' in df.columns and 'Player' in df.columns:
            df = df.dropna(subset=['Action', 'Player'])
            
            # معالجة الإحداثيات (بأمان)
            if 'x_start' in df.columns and 'y_start' in df.columns:
                df['x_scaled'] = df['x_start'].apply(lambda x: x if x > 1 else x * 120)
                df['y_scaled'] = df['y_start'].apply(lambda y: y if y > 1 else y * 80)
            
            st.success("✅ البيانات جاهزة للتحليل")
            
            # قائمة اللاعبين
            player_list = df['Player'].unique()
            sel_player = st.sidebar.selectbox("🎯 اختر لاعباً:", player_list)
            p_df = df[df['Player'] == sel_player]
            
            # الرسم البياني
            if 'x_scaled' in p_df.columns and len(p_df) > 1:
                fig, ax = plt.subplots(figsize=(10, 7))
                pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
                pitch.draw(ax=ax)
                sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, cmap='viridis', ax=ax)
                st.pyplot(fig)
            else:
                st.warning("⚠️ لا توجد بيانات كافية لهذا اللاعب لرسم الخريطة.")
        else:
            st.error(f"❌ لم يتم العثور على أعمدة 'Action' أو 'Player'. الأعمدة الموجودة: {df.columns.tolist()}")
            st.write("تأكد أن ملف الـ CSV يحتوي على هذه الأعمدة.")
else:
    st.info("👋 الرجاء رفع ملف CSV للبدء.")
