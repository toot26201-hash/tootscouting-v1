import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors

st.set_page_config(page_title="TootScouting Dashboard", layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro")

# تحميل البيانات
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تصحيح الأعمدة (X1, Y1)
    df = df.rename(columns={'X1': 'x1', 'Y1': 'y1'})
    df['x_scaled'] = df['x1'] * 120
    df['y_scaled'] = df['y1'] * 80
    
    # تنظيف الأسماء
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df['Player'] = df['Player'].fillna('Unknown').astype(str)

    # القائمة الجانبية
    players = sorted(df['Player'].dropna().unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", players)
    
    att_choices = st.sidebar.multiselect("⚽ الأكشن الهجومي:", ["Pass", "Shot", "Cross", "Through Ball"])
    def_choices = st.sidebar.multiselect("🛡️ الأكشن الدفاعي:", ["pressing", "extraction", "Tackle", "Foul"])

    # التقسيم إلى تبويبات (فصل الملاعب)
    tab1, tab2 = st.tabs(["🔥 تبويب خريطة الحرارة (Heatmap)", "🗺️ تبويب خرائط الأكشن (Action Maps)"])
    
    p_df = df[df['Player'] == sel_player].copy()

    with tab1:
        st.subheader(f"خريطة تحركات: {sel_player}")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
        fig1, ax1 = pitch.draw(figsize=(10, 7))
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout", ["#3b82f6", "#10b981", "#7f1d1d"], N=256)
        sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], cmap=scout_cmap, fill=True, ax=ax1)
        st.pyplot(fig1)

    with tab2:
        st.subheader(f"خرائط الأكشن لـ: {sel_player}")
        fig2, ax2 = pitch.draw(figsize=(10, 7))
        
        selected_actions = att_choices + def_choices
        if selected_actions:
            for act in att_choices:
                subset = p_df[p_df['Action'].str.contains(act, case=False, na=False)]
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], ax=ax2, color='blue', s=150, label=act)
            for act in def_choices:
                subset = p_df[p_df['Action'].str.contains(act, case=False, na=False)]
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], ax=ax2, color='red', marker='x', s=150, label=act)
            ax2.legend()
        else:
            st.info("يرجى اختيار أكشن من القائمة الجانبية لعرضه على هذا الملعب.")
        st.pyplot(fig2)

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
