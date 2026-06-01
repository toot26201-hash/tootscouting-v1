import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors

st.set_page_config(page_title="TootScouting Pro", layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro")

uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 1. إصلاح الإحداثيات (بناءً على ملفك)
    df = df.rename(columns={'X1': 'x1', 'Y1': 'y1'})
    df['x_scaled'] = df['x1'] * 120
    df['y_scaled'] = df['y1'] * 80
    
    # تنظيف مسميات الأكشن
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    
    # 2. القائمة الجانبية (الأدوات)
    st.sidebar.markdown("---")
    players = sorted(df['Player'].dropna().unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", players)
    
    # سيد بار للأكشن الهجومي
    att_choices = st.sidebar.multiselect("⚽ اختر الأكشن الهجومي:", 
                                         ["Pass", "Shot", "Cross", "Through Ball"])
    
    # سيد بار للأكشن الدفاعي
    def_choices = st.sidebar.multiselect("🛡️ اختر الأكشن الدفاعي:", 
                                         ["pressing", "extraction", "Tackle", "Foul"])

    # 3. الفلترة
    p_df = df[df['Player'] == sel_player].copy()
    
    # دمج الاختيارات
    selected_actions = att_choices + def_choices
    if selected_actions:
        p_df = p_df[p_df['Action'].str.contains('|'.join(selected_actions), case=False, na=False)]

    # 4. الرسم
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # Heatmap للمباريات الكلية أو Scatter للأكشن المحدد
    if not selected_actions:
        # إذا لم يختار شيئاً، نظهر الهيت ماب الأساسي
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout", ["#3b82f6", "#10b981", "#7f1d1d"], N=256)
        sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], cmap=scout_cmap, fill=True, ax=ax)
    else:
        # إظهار نقاط الأكشن المختار
        for act in att_choices:
            subset = p_df[p_df['Action'].str.contains(act, case=False, na=False)]
            pitch.scatter(subset['x_scaled'], subset['y_scaled'], ax=ax, color='blue', s=150, label=act)
        for act in def_choices:
            subset = p_df[p_df['Action'].str.contains(act, case=False, na=False)]
            pitch.scatter(subset['x_scaled'], subset['y_scaled'], ax=ax, color='red', marker='x', s=150, label=act)
        ax.legend()

    st.pyplot(fig)

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
