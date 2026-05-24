import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np

# إعدادات الصفحة
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# CSS المدمج (تنسيق TootScouting)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; }
    .stMarkdown, h1, h2, h3, p { color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

# 1. دالة حساب xG المدمجة
def calculate_xg(row):
    try:
        # حساب المسافة للمرمى
        dist = np.sqrt((1.0 - row['X Start'])**2 + (0.5 - row['Y Start'])**2)
        return round(0.5 / (dist + 0.5), 2)
    except:
        return 0.0

# 2. تحميل البيانات
@st.cache_data
def load_data():
    return pd.read_csv('EPS-honka-actions.csv')

df = load_data()

st.title("⚽ TootScouting Tactical Analysis")

# 3. إعداد الرسم (الملعب)
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#475569', linestyle='--')
fig, ax = pitch.draw(figsize=(10, 7))

# 4. معالجة البيانات وإضافة الـ xG
shots = df[df['Action'] == 'Shot'].copy()
if not shots.empty:
    shots['xG'] = shots.apply(calculate_xg, axis=1)
    # رسم التسديدات (حجم النقطة يعتمد على xG)
    pitch.scatter(shots['X Start'], shots['Y Start'], s=shots['xG']*500, 
                  c='#fbbf24', ax=ax, label='Shots (size by xG)')

# 5. ضبط الـ Legend (بألوان واضحة لا تخفي البيانات)
ax.legend(loc='upper left', 
          bbox_to_anchor=(1.01, 1), 
          facecolor='#1e293b', 
          edgecolor='#475569', 
          labelcolor='#f8fafc')

st.pyplot(fig)

# عرض إحصائيات سريعة
st.subheader("Match Metrics")
col1, col2 = st.columns(2)
col1.metric("Total Shots", len(shots))
col2.metric("Avg xG per Shot", round(shots['xG'].mean(), 2) if not shots.empty else 0)
