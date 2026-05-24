import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
from PIL import Image
import os
import matplotlib.colors as mcolors
import numpy as np
import base64

# دالة حساب xG الجديدة (مدمجة)
def calculate_xg(row):
    try:
        dist = np.sqrt((1.0 - row['X Start'])**2 + (0.5 - row['Y Start'])**2)
        return round(0.5 / (dist + 0.5), 2)
    except:
        return 0.0

# [هنا تضع باقي دوالك الأصلية: get_base64_logo, get_full_legend, إلخ...]

def parse_action_metrics(df, ax, pitch, layers, draw_mode=True, specific_type="all"):
    # دمج الـ xG داخل المعالجة
    if 'Shot' in df['Action'].values:
        df['xG'] = df.apply(calculate_xg, axis=1)
    
    # [باقي كود الدالة الخاص بك كما هو بالضبط دون أي تغيير]
    # ...
    # تأكد من عدم تعديل الـ handles أو الـ legend هنا
    pass

# عند استدعاء الـ legend في صفحتك، استخدمه كما كنت تستخدمه سابقاً:
# ax_all.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#0f172a', edgecolor='#334155')
