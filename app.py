import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.pyplot as plt

# إعداد الصفحة
st.set_page_config(page_title="TootScouting Professional Maps", layout="wide")
st.title("🔬 TootScouting | Tactical Analysis Maps")

# نموذج الملعب
def draw_toot_pitch(title):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', 
                  linestyle='--', linewidth=1, goal_linestyle='-', positional=True, positional_color='#e2e8f0')
    fig, ax = pitch.draw(figsize=(8, 5))
    ax.set_title(title, fontsize=15, fontweight='bold', color='#1e293b')
    return pitch, fig, ax

# تحميل البيانات (تم إضافة key لتجنب خطأ التكرار)
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'], key="match_data_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X1': 'x1', 'Y1': 'y1', 'X2': 'x2', 'Y2': 'y2'})
    df['x_scaled'] = df['x1'] * 120
    df['y_scaled'] = df['y1'] * 80
    df['x2_scaled'] = df['x2'] * 120
    df['y2_scaled'] = df['y2'] * 80
    
    # تحسين مسميات الأعمدة
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    
    # اختيار اللاعب
    players = sorted(df['Player'].dropna().unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", players)
    p_df = df[df['Player'] == sel_player].copy()
    
    # اختيار الأكشنات
    att_choices = st.sidebar.multiselect("⚽ الأكشن:", ["Pass", "Shot", "Cross", "Corner", "Pressing", "Counter-press"])
    
    # تقسيم الشاشة لأعمدة لعرض الخرائط
    cols = st.columns(2)
    
    for i, act in enumerate(att_choices):
        # تصفية البيانات
        subset = p_df[p_df['Action'].str.contains(act, case=False, na=False)]
        
        with cols[i % 2]:
            if not subset.empty:
                pitch, fig, ax = draw_toot_pitch(f"{act} Map - {sel_player}")
                
                for _, row in subset.iterrows():
                    # رسم الرموز حسب الأكشن
                    if act in ['Pass', 'Cross', 'Corner']:
                        pitch.arrows(row['x_scaled'], row['y_scaled'], row['x2_scaled'], row['y2_scaled'], ax=ax, color='green', width=2, headwidth=5)
                    elif act == 'Shot':
                        pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax, color='red', marker='*', s=200)
                    elif act == 'Pressing':
                        pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax, color='#2ecc71', marker='+', s=150)
                    elif act == 'Counter-press':
                        pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax, edgecolors='#f59e0b', facecolors='none', marker='o', s=200)
                
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.warning(f"لا توجد بيانات متاحة لـ {act}")
else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
