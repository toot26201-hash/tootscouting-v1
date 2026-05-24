import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors

# إعداد الصفحة
st.set_page_config(page_title="TootScouting | Tactical Analysis Pro", layout="wide")

# تنسيق CSS للخلفية البيضاء
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3 { color: #1e293b !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Lab")

uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

# دالة رسم الأحداث المحدثة
def parse_action_metrics(dataframe, ax, pitch_obj):
    for _, row in dataframe.iterrows():
        act = str(row['Action']).lower()
        x, y = row['x_scaled'], row['y_scaled']
        
        # التمريرات
        if 'pass' in act:
            color = '#22c55e' if 'success' in act else '#dc2626'
            pitch_obj.arrows(x, y, row.get('x_end_scaled', x), row.get('y_end_scaled', y), 
                             color=color, width=2, headwidth=5, ax=ax)
        # التسديدات
        elif 'shot' in act:
            color = '#1e40af' if 'goal' in act or 'target' in act else '#b91c1c'
            pitch_obj.scatter(x, y, marker='*', s=300, color=color, edgecolors='black', ax=ax)
        # الالتحامات
        elif 'duel' in act:
            color = '#15803d' if 'won' in act else '#b91c1c'
            pitch_obj.scatter(x, y, marker='s', s=150, color=color, ax=ax)
        # التدخلات
        elif 'tackle' in act:
            pitch_obj.scatter(x, y, marker='x', s=200, color='#1d4ed8', linewidth=2, ax=ax)
        # التشتيت
        elif 'clearance' in act:
            pitch_obj.scatter(x, y, marker='d', s=150, color='#7e22ce', ax=ax)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    # اكتشاف الأعمدة الذكي
    col_map = {c.lower().replace('_', ' ').strip(): c for c in df.columns}
    x_col = col_map.get('x start') or col_map.get('x')
    y_col = col_map.get('y start') or col_map.get('y')

    if x_col and y_col:
        df['x_scaled'] = df[x_col] * 120 if df[x_col].max() <= 1 else df[x_col]
        df['y_scaled'] = df[y_col] * 80 if df[y_col].max() <= 1 else df[y_col]
        df['x_end_scaled'] = df.get('x_end', df['x_scaled'])
        df['y_end_scaled'] = df.get('y_end', df['y_scaled'])
        
        # رسم الملعب
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linewidth=1.5)
        fig, ax = pitch.draw(figsize=(10, 7))
        fig.patch.set_facecolor('#ffffff') 
        
        # رسم الأحداث
        parse_action_metrics(df, ax, pitch)
        
        st.pyplot(fig)
    else:
        st.error(f"⚠️ تعذر العثور على الإحداثيات. الأعمدة المتاحة: {list(df.columns)}")
else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
