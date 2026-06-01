import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import os
import matplotlib.colors as mcolors
import base64
import numpy as np

# --- الإعدادات الأساسية ---
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# --- تنظيف البيانات وإعدادها (الحل الجذري) ---
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file, sep=None, engine='python')
    
    # 1. حل مشكلة الأعمدة المتكررة
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [f"{dup}_{i}" if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols.str.strip()
    
    # 2. إعادة تسمية الأعمدة
    rename_dict = {}
    for col in df.columns:
        c = col.lower()
        if 'action' in c or 'event' in c: rename_dict[col] = 'Action'
        elif 'player' in c: rename_dict[col] = 'Player'
        elif 'tag' in c: rename_dict[col] = 'Tags'
        elif 'x start' in c or c == 'x': rename_dict[col] = 'x_start'
        elif 'y start' in c or c == 'y': rename_dict[col] = 'y_start'
        elif 'x end' in c: rename_dict[col] = 'x_end'
        elif 'y end' in c: rename_dict[col] = 'y_end'
    df = df.rename(columns=rename_dict)
    
    # 3. إنشاء أعمدة الإحداثيات بأمان
    if 'x_start' in df.columns and 'y_start' in df.columns:
        df['x_scaled'] = df['x_start'].apply(lambda x: x if x > 1 else x * 120)
        df['y_scaled'] = df['y_start'].apply(lambda y: y if y > 1 else y * 80)
    else:
        # إحداثيات افتراضية إذا لم توجد أعمدة (لتفادي الانهيار)
        df['x_scaled'] = 60
        df['y_scaled'] = 40
        
    df['Tags'] = df['Tags'].fillna('').astype(str)
    return df

# --- واجهة المستخدم ---
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file:
    df = process_data(uploaded_file)
    
    # التأكد من الأعمدة الأساسية
    if 'Action' in df.columns and 'Player' in df.columns:
        df = df.dropna(subset=['Action', 'Player'])
        
        # اختيار لاعب للعرض
        players = df['Player'].unique()
        sel_player = st.sidebar.selectbox("🎯 اختر لاعباً:", players)
        p_df = df[df['Player'] == sel_player]
        
        # عرض الخريطة الحرارية مع فحص الأمان
        if 'x_scaled' in p_df.columns and len(p_df) > 1:
            fig, ax = plt.subplots(figsize=(10, 7))
            pitch = Pitch(pitch_type='statsbomb')
            pitch.draw(ax=ax)
            sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, cmap='viridis', ax=ax)
            st.pyplot(fig)
        else:
            st.warning("⚠️ لا تتوفر بيانات كافية لرسم الخريطة الحرارية.")
    else:
        st.error(f"❌ الملف لا يحتوي على أعمدة 'Action' أو 'Player'. الأعمدة الموجودة: {df.columns.tolist()}")
else:
    st.info("👋 يرجى رفع ملف CSV.")
