import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np

# إعداد الصفحة
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# CSS المحدث (تنسيق ألوان TootScouting)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; }
    .stMarkdown, h1, h2, h3, p { color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

# دالة حساب xG
def calculate_xg(row):
    try:
        goal_x, goal_y = 1.0, 0.5
        dist = np.sqrt((goal_x - row['X Start'])**2 + (goal_y - row['Y Start'])**2)
        return round(0.5 / (dist + 0.5), 2)
    except:
        return 0.0

# تحميل البيانات (تأكد من وجود الملف في نفس المجلد)
@st.cache_data
def load_data():
    return pd.read_csv('EPS-honka-actions.csv')

df = load_data()

st.title("⚽ TootScouting Tactical Analysis")

# جزء الرسم
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#475569', linestyle='--')
fig, ax = pitch.draw(figsize=(10, 7))

# إضافة مثال لرسم التسديدات مع حساب xG
shots = df[df['Action'] == 'Shot'].copy()
if not shots.empty:
    shots['xG'] = shots.apply(calculate_xg, axis=1)
    # رسم التسديدات
    sc = pitch.scatter(shots['X Start'], shots['Y Start'], s=shots['xG']*500, 
                       c='#fbbf24', ax=ax, label='Shots (size by xG)')

# إعداد الـ Legend بألوان واضحة
ax.legend(loc='upper left', facecolor='#0f172a', edgecolor='#475569', labelcolor='#f8fafc')

st.pyplot(fig)

# عرض إحصائية بسيطة
st.subheader("Match Metrics")
col1, col2 = st.columns(2)
col1.metric("Total Shots", len(shots))
col2.metric("Avg xG per Shot", round(shots['xG'].mean(), 2) if not shots.empty else 0)
