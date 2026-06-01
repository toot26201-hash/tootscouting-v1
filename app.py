import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors

# إعداد الصفحة
st.set_page_config(page_title="TootScouting Dashboard", layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro")

# تحميل البيانات
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 1. تصحيح الأعمدة (إصلاح الـ KeyError)
    df = df.rename(columns={'X1': 'x start', 'Y1': 'y start', 'X2': 'x end', 'Y2': 'y end'})
    df['x_scaled'] = df['x start'] * 120
    df['y_scaled'] = df['y start'] * 80
    
    # تنظيف الأسماء
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df['Player'] = df['Player'].fillna('Unknown').astype(str)

    # 2. القائمة الجانبية (Sidebar)
    st.sidebar.markdown("---")
    
    # Dropdown لاختيار اللاعب
    players = sorted(df['Player'].unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", players)
    
    # Sidebar للأكشن الهجومي
    st.sidebar.markdown("### ⚽ الأكشن الهجومي")
    att_actions = st.sidebar.multiselect("اختر الأكشن الهجومي:", ["Pass", "Cross", "Shot", "Through Ball"])
    
    # Sidebar للأكشن الدفاعي
    st.sidebar.markdown("### 🛡️ الأكشن الدفاعي")
    def_actions = st.sidebar.multiselect("اختر الأكشن الدفاعي:", ["pressing", "extraction", "Tackle"])

    # 3. الفلترة والرسم
    p_df = df[df['Player'] == sel_player].copy()
    
    # تصفية البيانات بناءً على اختيارات المستخدم
    active_layers = att_actions + def_actions
    if active_layers:
        p_df = p_df[p_df['Action'].isin(active_layers)]

    # رسم الملعب
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # رسم الهيت ماب
    if not p_df.empty:
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout", ["#3b82f6", "#10b981", "#7f1d1d"], N=256)
        sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], cmap=scout_cmap, fill=True, ax=ax)
    else:
        st.warning("لا توجد بيانات تطابق الفلاتر المختارة.")

    st.pyplot(fig)

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
