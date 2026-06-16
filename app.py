import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
from matplotlib.lines import Line2D

# إعداد الصفحة
st.set_page_config(page_title="TootScouting Professional Maps", layout="wide")
st.title("🔬 TootScouting | Professional Tactical Maps")

# دالة الهيت ماب الاحترافية (بشفافية معدلة للوضوح)
def draw_professional_heatmap(p_df, player_name):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#c7d5cc', linewidth=1)
    fig, ax = pitch.draw(figsize=(8, 5))
    
    bin_statistic = pitch.bin_statistic(p_df.x_scaled, p_df.y_scaled, statistic='count', bins=(50, 50))
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], sigma=1.5)
    
    colors = ['#1d2d44', '#1f5f8b', '#3a9ad9', '#8ccb7e', '#fbd400']
    cmap = LinearSegmentedColormap.from_list('toot_cmap', colors, N=100)
    
    # شفافية 0.6 تسمح برؤية الأسماء والخطوط تحت الهيت ماب
    pitch.heatmap(bin_statistic, ax=ax, cmap=cmap, zorder=1, vmin=0, 
                  vmax=bin_statistic['statistic'].max() * 0.8, alpha=0.6)
    
    ax.text(60, 40, player_name, fontsize=20, color='#1e293b', 
            alpha=0.3, fontweight='bold', ha='center', va='center', zorder=2)
    return fig, ax

# تحميل البيانات
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'], key="main_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X1': 'x1', 'Y1': 'y1', 'X2': 'x2', 'Y2': 'y2'})
    df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80
    df['x2_scaled'], df['y2_scaled'] = df['x2'] * 120, df['y2'] * 80
    
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df['Player'] = df['Player'].fillna('Unknown').astype(str)
    
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", sorted(df['Player'].unique()))
    p_df = df[df['Player'] == sel_player].copy()
    att_choices = st.sidebar.multiselect("⚽ الأكشن:", ["Pass", "Shot", "Cross", "Corner", "Pressing", "Counter-press"])
    
    tab1, tab2 = st.tabs(["🔥 Heatmap", "🗺️ Tactical Maps"])
    
    with tab1:
        fig, ax = draw_professional_heatmap(p_df, sel_player)
        st.pyplot(fig)
        plt.close(fig)
        
    with tab2:
        cols = st.columns(2)
        for i, act in enumerate(att_choices):
            subset = p_df[p_df['Action'].str.contains(act, case=False, na=False)]
            with cols[i % 2]:
                if not subset.empty:
                    pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b')
                    fig, ax = pitch.draw(figsize=(8, 5))
                    ax.set_title(f"{act} Map - {sel_player}", fontsize=15, fontweight='bold')
                    
                    for _, row in subset.iterrows():
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
                    st.warning(f"لا توجد بيانات لـ {act}")
else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
