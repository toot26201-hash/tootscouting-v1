import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
import numpy as np
import base64
import os
import matplotlib.colors as mcolors

# 1. إعداد الصفحة
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# 2. الدوال البرمجية (تم دمجها)
def get_base64_logo():
    # تأكد من وجود ملف اللوجو في نفس المجلد
    return None

def draw_premium_kde_heatmap(dataframe, ax):
    scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
    scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
    sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.04, alpha=0.85, bw_method=0.28, zorder=1, ax=ax)

# [هنا ضع دالة parse_action_metrics الخاصة بك بالكامل]
# تأكد أنها تستخدم dataframe['x_scaled'] و dataframe['y_scaled']

# 3. المعالجة الذكية (هذا الجزء يحل مشكلة الـ KeyError)
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip()
    
    # تحويل أسماء أعمدة ملفك
    rename_dict = {'Action': 'Action', 'Player': 'Player', 'Tags': 'Tags', 
                   'X1': 'x_start', 'Y1': 'y_start', 'X2': 'x_end', 'Y2': 'y_end'}
    df = df.rename(columns=rename_dict)
    
    # تحويل الإحداثيات (ضرب الكسور في 120 و 80)
    for col in ['x_start', 'y_start', 'x_end', 'y_end']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['x_scaled'] = df['x_start'] * 120
    df['y_scaled'] = df['y_start'] * 80
    df['x_end_scaled'] = df['x_end'] * 120
    df['y_end_scaled'] = df['y_end'] * 80
    
    return df.dropna(subset=['Action', 'Player'])

# 4. التنفيذ الرئيسي
st.title("🔬 TootScouting | Tactical Analysis Pro Lab")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    # المعالجة تتم هنا مرة واحدة
    team_df = process_data(uploaded_file)
    
    # الآن team_df تحتوي على x_scaled و y_scaled بشكل مؤكد
    # [بقية الكود الخاص بك بالـ Tabs والـ Sidebar يوضع هنا...]
    
    st.success("✅ البيانات جاهزة - يمكنك الآن استخدام التابات")
    
else:
    st.info("👋 Please upload a match CSV file.")
