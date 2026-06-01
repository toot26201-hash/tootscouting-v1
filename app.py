import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors

st.set_page_config(page_title="TootScouting Tactical Dashboard", layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Pro")

# تحميل البيانات
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # إصلاح الإحداثيات
    df = df.rename(columns={'X1': 'x1', 'Y1': 'y1'})
    df['x_scaled'] = df['x1'] * 120
    df['y_scaled'] = df['y1'] * 80
    
    # تنظيف الأسماء
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df['Player'] = df['Player'].fillna('Unknown').astype(str)

    # الأدوات في الـ Sidebar
    players = sorted(df['Player'].dropna().unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", players)
    
    att_choices = st.sidebar.multiselect("⚽ الأكشن الهجومي:", ["Pass", "Shot", "Cross", "Through Ball"])
    def_choices = st.sidebar.multiselect("🛡️ الأكشن الدفاعي:", ["pressing", "extraction", "Tackle", "Foul"])

    # نموذج الملعب مع كتابة اسم اللاعب
    def draw_toot_pitch(player_name):
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', 
                      linestyle='--', linewidth=1, goal_linestyle='-', positional=True, positional_color='#e2e8f0')
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # إضافة اسم اللاعب كعلامة مائية في منتصف الملعب
        ax.text(60, 40, player_name, fontsize=30, color='#1e293b', 
                alpha=0.15, fontweight='bold', ha='center', va='center', zorder=1)
        return pitch, fig, ax

    p_df = df[df['Player'] == sel_player].copy()
    
    tab1, tab2 = st.tabs(["🔥 Heatmap", "🗺️ Action Maps"])
    
    with tab1:
        pitch, fig1, ax1 = draw_toot_pitch(sel_player)
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout", ["#3b82f6", "#10b981", "#7f1d1d"], N=256)
        sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], cmap=scout_cmap, fill=True, ax=ax1, zorder=2)
        st.pyplot(fig1)
        
    with tab2:
        pitch, fig2, ax2 = draw_toot_pitch(sel_player)
        selected_actions = att_choices + def_choices
        if selected_actions:
            for act in att_choices:
                subset = p_df[p_df['Action'].str.contains(act, case=False, na=False)]
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], ax=ax2, color='blue', s=150, label=act, zorder=3)
            for act in def_choices:
                subset = p_df[p_df['Action'].str.contains(act, case=False, na=False)]
                pitch.scatter(subset['x_scaled'], subset['y_scaled'], ax=ax2, color='red', marker='x', s=150, label=act, zorder=3)
            ax2.legend()
        st.pyplot(fig2)

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
