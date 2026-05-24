import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np
import base64
import os

# Function to read and encode the club logo to Base64
def get_base64_logo():
    # تعديل المسارات حسب احتياجك
    return None 

# Page Config & Theme
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# CSS المحدث (إزالة الأسود وتوحيد الدرجات)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; }
    
    /* جعل الـ Legend متناغمة مع الخلفية الزرقاء الداكنة */
    .legend {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        color: #f1f5f9 !important;
    }
    
    .stMarkdown, h1, h2, h3, p { color: #f1f5f9 !important; }
    </style>
""", unsafe_allow_html=True)

# دالة حساب xG
def calculate_xg(row):
    goal_x, goal_y = 1.0, 0.5
    dist = np.sqrt((goal_x - row['X Start'])**2 + (goal_y - row['Y Start'])**2)
    # نموذج مبسط (عكس المسافة)
    return round(0.5 / (dist + 0.5), 2)

# تحليل البيانات
def parse_action_metrics(df, ax, pitch, layers, draw_mode=True, specific_type="all"):
    # معالجة التسديدات وإضافة xG
    shots = df[df['Action'] == 'Shot'].copy()
    if not shots.empty:
        shots['xG'] = shots.apply(calculate_xg, axis=1)
        # يمكنك هنا رسم الـ xG على الملعب إذا أردت
    
    # [بقية كود الرسم الخاص بك يوضع هنا...]
    pass

# المثال التوضيحي للرسم مع التعديل المطلوب
st.markdown(f"<h3 style='text-align: center; color: #a47e3c;'>⚽ Tactical Analysis Board</h3>", unsafe_allow_html=True)
pitch_all = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
fig_all, ax_all = pitch_all.draw(figsize=(12, 9))
fig_all.patch.set_facecolor('#1e293b') # خلفية الرسم نفسها

# تحديث الـ Legend ليكون أزرق داكن
ax_all.legend(
    loc='upper left', 
    bbox_to_anchor=(1.01, 1), 
    fontsize='small', 
    framealpha=1, 
    facecolor='#1e293b', 
    edgecolor='#475569',
    labelcolor='#f1f5f9'
)

st.pyplot(fig_all)
