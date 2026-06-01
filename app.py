import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors

st.set_page_config(page_title="TootScouting Tactical Dashboard", layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro")

uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 1. إصلاح الأعمدة (ربط X1, Y1 بما يتوقعه الكود)
    df = df.rename(columns={'X1': 'x start', 'Y1': 'y start'})
    df['x_scaled'] = df['x start'] * 120
    df['y_scaled'] = df['y start'] * 80
    
    # تنظيف البيانات
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df['Player'] = df['Player'].fillna('Unknown').astype(str)

    # 2. القائمة الجانبية (الأزرار)
    st.sidebar.markdown("---")
    players = sorted(df['Player'].unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", players)
    
    st.sidebar.markdown("### 🛠️ التحكم بالخريطة")
    map_type = st.sidebar.radio("اختر نوع العرض:", 
                                ["🔥 خريطة الحرارة (Heatmap)", 
                                 "⚽ الأكشن الهجومي", 
                                 "🛡️ الأكشن الدفاعي", 
                                 "🌐 الأكشن المدمج (الكل)"])

    # فلترة البيانات
    p_df = df[df['Player'] == sel_player].copy()
    
    # 3. رسم الملعب
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
    fig, ax = pitch.draw(figsize=(10, 7))

    # 4. منطق الرسم بناءً على الزر المختار
    if map_type == "🔥 خريطة الحرارة (Heatmap)":
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout", ["#3b82f6", "#10b981", "#7f1d1d"], N=256)
        sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], cmap=scout_cmap, fill=True, ax=ax)

    elif map_type == "⚽ الأكشن الهجومي":
        pass_df = p_df[p_df['Action'].str.contains('Pass|Shot|Cross', case=False, na=False)]
        pitch.scatter(pass_df['x_scaled'], pass_df['y_scaled'], ax=ax, color='blue', s=100)

    elif map_type == "🛡️ الأكشن الدفاعي":
        def_df = p_df[p_df['Action'].str.contains('pressing|extraction|Tackle', case=False, na=False)]
        pitch.scatter(def_df['x_scaled'], def_df['y_scaled'], ax=ax, color='red', marker='x', s=100)

    elif map_type == "🌐 الأكشن المدمج (الكل)":
        pitch.scatter(p_df['x_scaled'], p_df['y_scaled'], ax=ax, color='green', s=50)

    st.pyplot(fig)

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
