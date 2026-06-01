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
    
    # إصلاح الأعمدة
    df = df.rename(columns={'X1': 'x1', 'Y1': 'y1'})
    df['x_scaled'] = df['x1'] * 120
    df['y_scaled'] = df['y1'] * 80
    
    df = df.rename(columns={c: 'Action' for c in df.columns if 'action' in c.lower() or 'event' in c.lower()})
    df = df.rename(columns={c: 'Player' for c in df.columns if 'player' in c.lower()})
    df = df.rename(columns={c: 'Tags' for c in df.columns if 'tag' in c.lower()})
    df['Player'] = df['Player'].fillna('Unknown').astype(str)
    df['Tags'] = df['Tags'].fillna('').astype(str)

    # الأدوات
    players = sorted(df['Player'].dropna().unique().tolist())
    sel_player = st.sidebar.selectbox("🎯 اختر اللاعب:", players)
    
    # القوائم التفاعلية
    att_choices = st.sidebar.multiselect("⚽ الأكشن الهجومي:", ["Pass", "Shot", "Cross", "Goal", "Corner", "Progressive Pass"])
    def_choices = st.sidebar.multiselect("🛡️ الأكشن الدفاعي:", ["pressing", "extraction", "Tackle", "Foul", "Ground Duel", "Aerial Duel"])

    # نموذج الملعب
    def draw_toot_pitch(player_name):
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', linewidth=1, goal_linestyle='-', positional=True, positional_color='#e2e8f0')
        fig, ax = pitch.draw(figsize=(10, 7))
        ax.text(60, 40, player_name, fontsize=30, color='#1e293b', alpha=0.15, fontweight='bold', ha='center', va='center', zorder=1)
        return pitch, fig, ax

    # التبويبات
    tab1, tab2 = st.tabs(["🔥 Heatmap", "🗺️ Action Maps"])
    
    # فلترة البيانات بناءً على اختيارات اللاعب والأكشن
    p_df = df[df['Player'] == sel_player].copy()
    
    with tab1:
        pitch, fig1, ax1 = draw_toot_pitch(sel_player)
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout", ["#3b82f6", "#10b981", "#7f1d1d"], N=256)
        sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], cmap=scout_cmap, fill=True, ax=ax1, zorder=2)
        st.pyplot(fig1)
        
    with tab2:
        pitch, fig2, ax2 = draw_toot_pitch(sel_player)
        
        # --- الجزء الديناميكي: التصفية هنا هي السر ---
        selected_actions = att_choices + def_choices
        
        if selected_actions:
            # فلترة البيانات لتشمل فقط ما تم اختياره
            filtered_df = p_df[p_df['Action'].str.contains('|'.join(selected_actions), case=False, na=False) | 
                              p_df['Tags'].str.contains('|'.join(selected_actions), case=False, na=False)]
            
            for _, row in filtered_df.iterrows():
                act = str(row['Action'])
                tag = str(row['Tags'])
                
                # الهجوم
                if any(c in act for c in ["Pass", "Cross", "Corner", "Progressive Pass"]):
                    color = '#2ecc71' if 'Success' in tag else '#e74c3c'
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='>', s=100, zorder=3)
                elif 'Shot' in act:
                    color = '#2563eb' if 'On Target' in tag else '#dc2626'
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='*', s=200, zorder=3)
                elif 'Goal' in act:
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color='gold', marker='*', s=300, zorder=3)
                
                # الدفاع
                elif 'Foul' in act:
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color='red', marker='x', s=150, zorder=3)
                elif 'pressing' in act:
                    ax2.text(row['x_scaled'], row['y_scaled'], '#', color='#2ecc71', fontsize=20, fontweight='bold', ha='center', va='center', zorder=3)
                elif 'Aerial' in act:
                    color = '#2ecc71' if 'Won' in tag else '#e74c3c'
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='^', s=150, zorder=3)
                elif 'Ground' in act:
                    color = '#2ecc71' if 'Won' in tag else '#e74c3c'
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='s', s=150, zorder=3)
                elif 'Tackle' in act or 'extraction' in act:
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color='purple', marker='d', s=150, zorder=3)
        else:
            st.info("اختر نوع الأكشن من القائمة الجانبية للبدء.")
        
        st.pyplot(fig2)

else:
    st.info("👋 يرجى رفع ملف الـ CSV للبدء.")
