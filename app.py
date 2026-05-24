import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np
import os

# إعدادات الصفحة
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# CSS المدمج لتنسيق TootScouting
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; }
    .stMarkdown, h1, h2, h3, p { color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

# 1. دالة حساب xG المدمجة
def calculate_xg(row):
    try:
        # حساب المسافة للمرمى (إحداثيات Statsbomb المرمى عند 1.0, 0.5)
        dist = np.sqrt((1.0 - row['X Start'])**2 + (0.5 - row['Y Start'])**2)
        return round(0.5 / (dist + 0.5), 2)
    except:
        return 0.0

# 2. تحميل البيانات (مع تحديد المسار بدقة)
@st.cache_data
def load_data():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'EPS-honka-actions.csv')
    return pd.read_csv(file_path)

df = load_data()

st.title("⚽ TootScouting Tactical Analysis")

# 3. إعداد الرسم (الملعب)
# حافظنا على إعداداتك الأصلية مع تغيير خلفية الـ Legend فقط
pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', 
              linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
fig, ax = pitch.draw(figsize=(10, 7))
fig.patch.set_facecolor('#1e293b')

# 4. معالجة البيانات وإضافة الـ xG
shots = df[df['Action'] == 'Shot'].copy()
if not shots.empty:
    shots['xG'] = shots.apply(calculate_xg, axis=1)
    # رسم التسديدات (الحجم يعتمد على قيمة xG)
    pitch.scatter(shots['X Start'], shots['Y Start'], s=shots['xG']*500, 
                  c='#fbbf24', ax=ax, label='Shots (xG weighted)')

# 5. ضبط الـ Legend (تنسيق احترافي لا يخفي البيانات)
ax.legend(loc='upper left', 
          bbox_to_anchor=(1.01, 1), 
          facecolor='#1e293b', 
          edgecolor='#475569', 
          labelcolor='#f8fafc')

st.pyplot(fig)

# 6. عرض إحصائيات سريعة
st.subheader("Match Metrics")
col1, col2 = st.columns(2)
col1.metric("Total Shots", len(shots))
col2.metric("Avg xG per Shot", round(shots['xG'].mean(), 2) if not shots.empty else 0)
