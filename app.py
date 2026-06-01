import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import base64

# 1. الإعدادات
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# 2. دالة معالجة بيانات LongoMatch المخصصة لملفك
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] # حذف الأعمدة الفارغة
    df.columns = df.columns.str.strip()
    
    # ربط أعمدة ملفك بأسماء الكود
    rename_dict = {'Action': 'Action', 'Player': 'Player', 'X1': 'x_start', 'Y1': 'y_start', 'X2': 'x_end', 'Y2': 'y_end', 'Tags': 'Tags'}
    df = df.rename(columns=rename_dict)
    
    # تحويل الإحداثيات (ضرب الكسور في 120 و 80)
    for col in ['x_start', 'y_start', 'x_end', 'y_end']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['x_scaled'] = df['x_start'] * 120
    df['y_scaled'] = df['y_start'] * 80
    df['x_end_scaled'] = df['x_end'] * 120
    df['y_end_scaled'] = df['y_end'] * 80
    
    return df.dropna(subset=['Action', 'Player'])

# 3. واجهة التطبيق
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    try:
        team_df = process_data(uploaded_file)
        st.success("✅ تم تحميل بيانات المباراة بنجاح!")
        
        # اختيار اللاعب
        player_list = sorted(team_df['Player'].unique())
        sel_player = st.sidebar.selectbox("🎯 اختر لاعباً:", player_list)
        p_df = team_df[team_df['Player'] == sel_player]
        
        # التابات
        tab1, tab2 = st.tabs(["🔥 الخريطة الحرارية", "🏃‍♂️ خريطة العمليات"])
        
        with tab1:
            st.write(f"### Heatmap for {sel_player}")
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
            fig, ax = pitch.draw(figsize=(10, 7))
            if len(p_df) > 1:
                sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], fill=True, cmap='viridis', ax=ax)
            st.pyplot(fig)
            
        with tab2:
            st.write(f"### Actions Map for {sel_player}")
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
            fig, ax = pitch.draw(figsize=(10, 7))
            # رسم التمريرات (مثال)
            for _, row in p_df.iterrows():
                if 'Pass' in str(row['Action']):
                    pitch.arrows(row['x_scaled'], row['y_scaled'], row['x_end_scaled'], row['y_end_scaled'], ax=ax, color='green')
            st.pyplot(fig)
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء العرض: {e}")
else:
    st.info("👋 يرجى رفع ملف CSV الخاص بك للبدء.")
