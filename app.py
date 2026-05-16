import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
from PIL import Image
import os

# 1. Page Config & Strict Dark Premium Theme (TootScouting Global Style)
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

st.markdown("""
    <style>
    /* Global Background and Text Color */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: #f8fafc !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #334155;
    }
    
    /* Text Typography Upgrades */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #f8fafc !important;
    }
    
    /* Custom Navigation Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #0f172a;
        padding: 8px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        color: #94a3b8 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #a47e3c !important; 
        color: #ffffff !important;
        border-color: #a47e3c !important;
    }

    /* Player Performance Summary Table Theme with Progress Bars */
    .summary-table-container {
        background: #1e293b;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
        border: 1px solid #a47e3c;
    }
    .summary-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 16px;
        border-bottom: 2px solid #a47e3c;
        padding-bottom: 8px;
    }
    .player-summary-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
    }
    .player-summary-table th {
        background-color: #0f172a;
        color: #94a3b8;
        font-weight: 600;
        padding: 14px;
        font-size: 0.9rem;
        border-bottom: 2px solid #334155;
    }
    .player-summary-table td {
        padding: 14px;
        font-size: 0.95rem;
        color: #e2e8f0;
        border-bottom: 1px solid #334155;
    }
    .player-summary-table tr:hover {
        background-color: rgba(164, 126, 60, 0.1);
    }
    .stat-badge {
        background-color: #334155;
        color: #38bdf8;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    /* Progress Bar Styling */
    .progress-bar-bg {
        background-color: #334155;
        border-radius: 4px;
        width: 100px;
        height: 8px;
        display: inline-block;
        margin-left: 10px;
        vertical-align: middle;
        overflow: hidden;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #a47e3c, #38bdf8);
        height: 100%;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# دالة دمج لوجو النادي الشفاف في سنتر الملعب
def add_club_logo(ax):
    logo_filename = 'Espoon_Palloseura_logo.png'
    if os.path.exists(logo_filename):
        try:
            img = Image.open(logo_filename)
            ax.imshow(img, extent=[45, 75, 25, 55], alpha=0.18, zorder=2)
        except:
            pass

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- Sidebar Controls ---
st.sidebar.markdown("## 🛠️ Tactical Control Unit")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    df = df.dropna(subset=['Action', 'Team'])
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("📋 Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    with st.sidebar.expander("🎯 Passing Filters", expanded=True):
        selected_passes = st.multiselect("Pass Types:", ["Normal Passes", "Crosses", "Through Balls", "Corners", "Free Kicks"], default=["Normal Passes", "Crosses"])
        
    with st.sidebar.expander("🛡️ Defensive Filters", expanded=True):
        selected_defense = st.multiselect("Actions:", ["Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Counterpress", "Goals"], default=["Tackles", "Ground Duels", "Clearances"])

    all_selected_layers = selected_passes + selected_defense

    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', label='Pass Success', markersize=8),
            mlines.Line2D([], [], color='#e74c3c', marker='>', linestyle='-', label='Pass Failed', markersize=8),
            mlines.Line2D([], [], color='blue', marker='>', linestyle='-', label='Cross Success', markersize=8),
            mlines.Line2D([], [], color='red', marker='>', linestyle='--', label='Cross Failed', markersize=8),
            mlines.Line2D([], [], color='#FF69B4', marker='>', linestyle='-', label='Through Ball', markersize=8),
            mlines.Line2D([], [], color='blue', marker='x', label='Tackle (Blue X)', linestyle='None', markersize=10, markeredgewidth=2),
            mlines.Line2D([], [], color='purple', marker='d', label='Clearance', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#2ecc71', marker='s', label='Ground Duel Won', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='red', marker='s', label='Ground Duel Lost', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#2ecc71', marker='^', label='Aerial Won', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='red', marker='^', label='Aerial Lost', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='gold', marker='*', label='Goal', linestyle='None', markersize=12)
        ]

    # دالة رسم الإجراءات الدفاعية والهجومية فقط
    def draw_defensive_actions(dataframe, ax, pitch_obj, layers):
        counts = {
            "total_passes": 0, "success_passes": 0, "crosses": 0, "success_crosses": 0,
            "through_balls": 0, "tackles": 0, "clearances": 0, "ground_duels_won": 0,
            "aerial_duels_won": 0, "goals": 0
        }
        
        for i, row in dataframe.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'ناجح' in tag
            drawn_action = False
            
            if 'pass' in act or 'تمرير' in act:
                if 'cross' in tag and "Crosses" in layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax, zorder=4)
                    counts["crosses"] += 1
                    if is_success: counts["success_crosses"] += 1
                    drawn_action = True
                elif 'through' in tag and "Through Balls" in layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax, zorder=4)
                    counts["through_balls"] += 1
                    drawn_action = True
                elif 'corner' in tag and "Corners" in layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange' if is_success else 'red', ax=ax, zorder=4)
                    drawn_action = True
                elif "Normal Passes" in layers and not any(k in tag for k in ['cross', 'through', 'corner', 'free kick']):
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.5, zorder=3)
                    drawn_action = True
                
                if drawn_action:
                    counts["total_passes"] += 1
                    if is_success: counts["success_passes"] += 1

            elif any(word in act for word in ['tackle', 'inter', 'تدخل', 'قطع', 'clear', 'تشتيت', 'duel', 'التحام']):
                if any(w in act for w in ['tackle', 'inter', 'تدخل', 'قطع']) and "Tackles" in layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=240, color='blue', linewidth=3, ax=ax, zorder=5)
                    counts["tackles"] += 1
                elif 'clear' in act and "Clearances" in layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='d', s=200, color='purple', ax=ax, zorder=5)
                    counts["clearances"] += 1
                elif 'aerial' in act and "Aerial Duels" in layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='^', s=220, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax, zorder=5)
                    if is_success: counts["aerial_duels_won"] += 1
                elif 'duel' in act and 'aerial' not in act and "Ground Duels" in layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color='#2ecc71' if is_success else 'red', ax=ax, zorder=5)
                    if is_success: counts["ground_duels_won"] += 1
            
            if ('goal' in tag or 'هدف' in tag) and "Goals" in layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=650, color='gold', edgecolors='black', ax=ax, zorder=6)
                counts["goals"] += 1
                
        return counts

    # دالة حساب الإحصائيات في الخلفية للجدول
    def get_stats_only(dataframe, layers):
        counts = {"total_passes": 0, "success_passes": 0, "crosses": 0, "success_crosses": 0, "through_balls": 0, "tackles": 0, "clearances": 0, "ground_duels_won": 0, "aerial_duels_won": 0, "goals": 0}
        for i, row in dataframe.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'ناجح' in tag
            if 'pass' in act or 'تمرير' in act:
                if 'cross' in tag and "Crosses" in layers:
                    counts["crosses"] += 1
                    if is_success: counts["success_crosses"] += 1
                elif 'through' in tag and "Through Balls" in layers: counts["through_balls"] += 1
                elif "Normal Passes" in layers and not any(k in tag for k in ['cross', 'through', 'corner', 'free kick']):
                    counts["total_passes"] += 1
                    if is_success: counts["success_passes"] += 1
            elif any(w in act for w in ['tackle', 'inter', 'تدخل', 'قطع']) and "Tackles" in layers: counts["tackles"] += 1
            elif 'clear' in act and "Clearances" in layers: counts["clearances"] += 1
            elif 'aerial' in act and "Aerial Duels" in layers and is_success: counts["aerial_duels_won"] += 1
            elif 'duel' in act and 'aerial' not in act and "Ground Duels" in layers and is_success: counts["ground_duels_won"] += 1
            if ('goal' in tag or 'هدف' in tag) and "Goals" in layers: counts["goals"] += 1
        return counts

    def render_player_summary_table(player_name, stats):
        p_pct = (stats['success_passes']/stats['total_passes'])*100 if stats['total_passes'] > 0 else 0
        c_pct = (stats['success_crosses']/stats['crosses'])*100 if stats['crosses'] > 0 else 0
        st.markdown(f"""
            <div class="summary-table-container">
                <div class="summary-title">📊 Player Summary Profile: {player_name}</div>
                <table class="player-summary-table">
                    <thead><tr><th>Metric Category</th><th>Total Attempts</th><th>Visual Progress & Accuracy</th></tr></thead>
                    <tbody>
                        <tr><td><b>Total Passing</b></td><td>{stats['total_passes']}</td><td><div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {p_pct}%;"></div></div> <span class="stat-badge">{stats['success_passes']} ({p_pct:.1f}%)</span></td></tr>
                        <tr><td><b>Crosses</b></td><td>{stats['crosses']}</td><td><div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {c_pct}%;"></div></div> <span class="stat-badge">{stats['success_crosses']} ({c_pct:.1f}%)</span></td></tr>
                        <tr><td><b>Through Balls</b></td><td>{stats['through_balls']}</td><td><span class="stat-badge">{stats['through_balls']}</span></td></tr>
                        <tr><td><b>Defensive Tackles</b></td><td>{stats['tackles']}</td><td><span class="stat-badge">{stats['tackles']}</span></td></tr>
                        <tr><td><b>Clearances</b></td><td>{stats['clearances']}</td><td><span class="stat-badge">{stats['clearances']}</span></td></tr>
                        <tr><td><b>Ground Duels Won</b></td><td>-</td><td><span class="stat-badge">{stats['ground_duels_won']} Won</span></td></tr>
                        <tr><td><b>Aerial Duels Won</b></td><td>-</td><td><span class="stat-badge">{stats['aerial_duels_won']} Won</span></td></tr>
                        <tr><td style="color: gold; font-weight: bold;">⚽ Goals Scored</td><td>-</td><td><span class="stat-badge" style="background-color: #fef08a; color: #854d0e;">{stats['goals']} GOAL</span></td></tr>
                    </tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👤 Individual Player Lab", "👥 Team Strategy Lab"])

    with tab1:
        # تجهيز الأسماء مع لوجو النادي 🛡️ لتظهر بشكل عالمي في القائمة المنسدلة
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        player_options = {p: f"🛡️ {p}" for p in player_list}
        
        sel_player = st.selectbox("🎯 Focus Player:", options=player_list, format_func=lambda x: player_options[x])
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        p_stats = get_stats_only(p_df, all_selected_layers)
        render_player_summary_table(sel_player, p_stats)
        
        # تقسيم الشاشة لملعبين متوازيين (Side-by-Side) زي لاب سكاوت بالظبط
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3 style='text-align: center; color: #38bdf8;'>🔥 Tactical Heatmap</h3>", unsafe_allow_html=True)
            pitch_h = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_h, ax_h = pitch_h.draw(figsize=(8, 6))
            
            # الخريطة الحرارية لوحدها بألوان نارية فخمة (تدرج ناري مريح وعالي التباين)
            if len(p_df) > 1:
                sns.kdeplot(x=p_df['x_scaled'], y=p_df['y_scaled'], cmap='YlOrRd', fill=True, thresh=0.03, alpha=0.75, zorder=1, ax=ax_h)
            add_club_logo(ax_h)
            st.pyplot(fig_h)
            
        with col2:
            st.markdown("<h3 style='text-align: center; color: #a47e3c;'>🛡️ Defensive Actions Map</h3>", unsafe_allow_html=True)
            pitch_d = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_d, ax_d = pitch_d.draw(figsize=(8, 6))
            
            add_club_logo(ax_d)
            # رسم الأكشنز الدفاعية لوحدها تماماً فوق الملعب الأبيض النظيف
            draw_defensive_actions(p_df, ax_d, pitch_d, all_selected_layers)
            ax_d.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='x-small', framealpha=1, facecolor='#ffffff', edgecolor='#e2e8f0')
            st.pyplot(fig_d)

    with tab2:
        st.subheader(f"Tactical Distribution: {selected_team}")
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("<h4 style='text-align: center;'>Team Heatmap</h4>", unsafe_allow_html=True)
            pitch_th = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_th, ax_th = pitch_th.draw(figsize=(8, 6))
            if len(team_df) > 1:
                sns.kdeplot(x=team_df['x_scaled'], y=team_df['y_scaled'], cmap='Oranges', fill=True, thresh=0.05, alpha=0.6, zorder=1, ax=ax_th)
            add_club_logo(ax_th)
            st.pyplot(fig_th)
            
        with col_t2:
            st.markdown("<h4 style='text-align: center;'>Team Actions</h4>", unsafe_allow_html=True)
            pitch_td = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_td, ax_td = pitch_td.draw(figsize=(8, 6))
            add_club_logo(ax_td)
            draw_defensive_actions(team_df, ax_td, pitch_td, all_selected_layers)
            ax_td.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='x-small', framealpha=1, facecolor='#ffffff', edgecolor='#e2e8f0')
            st.pyplot(fig_td)
else:
    st.info("👋 Please upload a match CSV file on the left sidebar to generate the dynamic dashboard.")
