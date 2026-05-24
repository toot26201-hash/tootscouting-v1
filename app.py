import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
import matplotlib.colors as mcolors
import os
import base64

# Function to read and encode the club logo
def get_base64_logo():
    current_dir = os.path.dirname(__file__)
    logo_filename = 'espoon_palloseura_logo.png' 
    if os.path.exists(logo_filename):
        with open(logo_filename, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

# تخصيص الألوان للخلفية البيضاء
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; color: #1e293b !important; }
    h1, h2, h3 { color: #1e293b !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 TootScouting | Tactical Analysis Lab (White Mode)")

uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تحويل الإحداثيات
    x_col, y_col = 'x', 'y' # تأكد من مطابقة أسماء أعمدة ملفك
    df['x_scaled'] = df[x_col] if df[x_col].max() > 1 else df[x_col] * 120
    df['y_scaled'] = df[y_col] if df[y_col].max() > 1 else df[y_col] * 80

    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#22c55e', marker='>', linestyle='-', label='Pass Success', markersize=8),
            mlines.Line2D([], [], color='#dc2626', marker='>', linestyle='-', label='Pass Failed', markersize=8),
            mlines.Line2D([], [], color='#0284c7', marker='>', linestyle='-', label='Cross Success', markersize=8),
            mlines.Line2D([], [], color='#991b1b', marker='>', linestyle='--', label='Cross Failed', markersize=8),
            mlines.Line2D([], [], color='#db2777', marker='>', linestyle='-', label='Through Ball', markersize=8),
            mlines.Line2D([], [], color='#ca8a04', marker='>', linestyle='-', label='Key Pass 🔑', markersize=10),
            mlines.Line2D([], [], color='#1e40af', marker='*', label='Shot On-Target', linestyle='None', markersize=12),
            mlines.Line2D([], [], color='#b91c1c', marker='*', label='Shot Off-Target', linestyle='None', markersize=12),
            mlines.Line2D([], [], color='#1d4ed8', marker='x', label='Tackle', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#7e22ce', marker='d', label='Clearance', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#15803d', marker='s', label='Ground Duel Won', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#b91c1c', marker='s', label='Ground Duel Lost', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#000000', marker='o', label='Counterpress (#)', linestyle='None', markersize=8)
        ]

    def draw_premium_kde_heatmap(dataframe, ax):
        # تدرج لوني فاتح للخلفية البيضاء
        scout_lab_colors = ["#f1f5f9", "#bae6fd", "#38bdf8", "#0284c7", "#1e3a8a"]
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("white_mode", scout_lab_colors, N=256)
        sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.05, alpha=0.6, ax=ax)

    # مثال لرسم الملعب
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linewidth=1.5)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.patch.set_facecolor('#ffffff') # ضبط خلفية الشكل
    
    # تفعيل الرسم
    # هنا تضع استدعاءات دالة parse_action_metrics التي تستخدم ألواناً داكنة
    
    st.pyplot(fig)

else:
    st.info("يرجى رفع ملف البيانات للبدء.")
