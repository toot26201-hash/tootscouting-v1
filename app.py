import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines  # تم إصلاح السطر هنا يا بطل
import seaborn as sns
from PIL import Image
import os
import matplotlib.colors as mcolors

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

    /* Player Performance Summary Table Theme with Neon Progress Bars */
    .summary-table-container {
        background: #1e293b;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
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
        background-color: #0f172a;
        color: #38bdf8;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.4);
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
    }
    
    /* Progress Bar Neon Design */
    .progress-bar-bg {
        background-color: #0f172a;
        border-radius: 6px;
        width: 140px;
        height: 12px;
        display: inline-block;
        margin-right: 12px;
        vertical-align: middle;
        overflow: hidden;
        border: 1px solid #334155;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #a47e3c 0%, #38bdf8 100%);
        height: 100%;
        border-radius: 6px;
        box-shadow: 0 0 8px #38bdf8;
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
        
    with st.sidebar.expander("🛡️ Defensive & Attack Filters", expanded=True):
        selected_defense = st.multiselect("Actions:", ["Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Counterpress", "Goals"], default=["Tackles", "Ground Duels", "Clearances", "Aerial Duels"])

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

    # محرك البحث ورسم الماتريكس التكتيكي بالكامل
    def parse_action_metrics(dataframe, ax, pitch_obj, layers, draw_mode=True):
        matrix = {
            "total_passes": 0, "success_passes": 0, "crosses": 0, "success_crosses": 0,
            "through_balls": 0, "tackles": 0, "clearances": 0, "ground_duels_won": 0,
            "aerial_duels_won": 0, "goals": 0
        }
        
        for i, row in dataframe.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'ناجح' in tag or 'won' in tag or 'win' in tag
            action_captured = False
            
            if 'pass' in act or 'تمرير' in act:
                if 'cross' in tag and "Crosses" in layers:
                    if draw_mode: pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax, zorder=4)
                    matrix["crosses"] += 1
                    if is_success: matrix["success_crosses"] += 1
                    action_captured = True
                elif 'through' in tag and "Through Balls" in layers:
                    if draw_mode: pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax, zorder=4)
                    matrix["through_balls"] += 1
                    action_captured = True
                elif 'corner' in tag and "Corners" in layers:
                    if draw_mode: pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange' if is_success else 'red', ax=ax, zorder=4)
                    action_captured = True
                elif "Normal Passes" in layers and not any(k in tag for k in ['cross', 'through', 'corner', 'free kick']):
                    if draw_mode: pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.5, zorder=3)
                    action_captured = True
                
                if action_captured:
                    matrix["total_passes"] += 1
                    if is_success: matrix["success_passes"] += 1

            elif any(w in act for w in ['tackle', 'inter', 'تدخل', 'قطع', 'تكل', 'تاكلز']) and "Tackles" in layers:
                if draw_mode: pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=240, color='blue', linewidth=3, ax=ax, zorder=5)
                matrix["tackles"] += 1

            elif any(w in act for w in ['clear', 'clearance', 'تشتيت', 'ابعاد']) and "Clearances" in layers:
                if draw_mode: pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='d', s=200, color='purple', ax=ax, zorder=5)
                matrix["clearances"] += 1

            elif any(w in act for w in ['aerial', 'هوائي', 'طير', 'رأس']) and "Aerial Duels" in layers:
                if draw_mode: pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='^', s=220, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax, zorder=5)
                if is_success: matrix["aerial_duels_won"] += 1

            elif any(w in act for w in ['duel', 'التحام', 'صراع', 'أرضي', 'ground']) and 'aerial' not in act and "Ground Duels" in layers:
                if draw_mode: pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color='#2ecc71' if is_success else 'red', ax=ax, zorder=5)
                if is_success: matrix["ground_duels_won"] += 1
            
            if ('goal' in tag or 'هدف' in tag) and "Goals" in layers:
                if draw_mode: pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=650, color='gold', edgecolors='black', ax=ax, zorder=6)
                matrix["goals"] += 1
                
        return matrix

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
                        <tr><td><b>Defensive Tackles (Tackles)</b></td><td>{stats['tackles']}</td><td><span class="stat-badge">{stats['tackles']}</span></td></tr>
                        <tr><td><b>Clearances</b></td><td>{stats['clearances']}</td><td><span class="stat-badge">{stats['clearances']}</span></td></tr>
                        <tr><td><b>Ground Duels Won</b></td><td>-</td><td><span class="stat-badge">{stats['ground_duels_won']} Won</span></td></tr>
                        <tr><td><b>Aerial Duels Won</b></td><td>-</td><td><span class="stat-badge">{stats['aerial_duels_won']} Won</span></td></tr>
                        <tr><td style="color: gold; font-weight: bold;">⚽ Goals Scored</td><td>-</td><td><span class="stat-badge" style="background-color: #fef08a; color: #854d0e;">{stats['goals']} GOAL</span></td></tr>
                    </tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)

    # --- التبويبات الفنية الثلاثية المنفصلة (The Master Setup) ---
    tab1, tab2, tab3 = st.tabs(["📊 Player Profile Summary", "🔥 Tactical Heatmap", "🏃‍♂️ Player Actions Map"])

    # تجهيز قوايم اللعيبة مدمج فيها لوجو EPS الإحترافي 🛡️
    player_list = sorted(team_df['Player'].dropna().unique().tolist())
    player_options = {p: f"🛡️ {p}" for p in player_list}

    # 1. التابة الأولى: جدول الأداء والملخص الإحصائي
    with tab1:
        sel_player_t1 = st.selectbox("🎯 Focus Player (Summary):", options=player_list, format_func=lambda x: player_options[x], key="sb_t1")
        p_df_t1 = team_df[team_df['Player'] == sel_player_t1].copy()
        p_stats_t1 = parse_action_metrics(p_df_t1, None, None, all_selected_layers, draw_mode=False)
        render_player_summary_table(sel_player_t1, p_stats_t1)

    # 2. التابة الثانية: خريطة حرارية لوحدها بكامل عرض الشاشة وبألوان سكاوت لاب
    with tab2:
        sel_player_t2 = st.selectbox("🎯 Focus Player (Heatmap):", options=player_list, format_func=lambda x: player_options[x], key="sb_t2")
        p_df_t2 = team_df[team_df['Player'] == sel_player_t2].copy()
        
        pitch_h = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_h, ax_h = pitch_h.draw(figsize=(12, 9))
        
        scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
        
        if len(p_df_t2) > 1:
            sns.kdeplot(x=p_df_t2['x_scaled'], y=p_df_t2['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.01, alpha=0.85, bw_method=0.3, zorder=1, ax=ax_h)
        add_club_logo(ax_h)
        st.pyplot(fig_h)

    # 3. التابة الثالثة المستقلة: ملعب الأكشنز والتمريرات والإجراءات الدفاعية بالكامل
    with tab3:
        sel_player_t3 = st.selectbox("🎯 Focus Player (Actions):", options=player_list, format_func=lambda x: player_options[x], key="sb_t3")
        p_df_t3 = team_df[team_df['Player'] == sel_player_t3].copy()
        
        pitch_d = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_d, ax_d = pitch_d.draw(figsize=(12, 9))
        
        add_club_logo(ax_d)
        parse_action_metrics(p_df_t3, ax_d, pitch_d, all_selected_layers, draw_mode=True)
        ax_d.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#ffffff', edgecolor='#e2e8f0')
        st.pyplot(fig_d)

else:
    st.info("👋 Please upload a match CSV file on the left sidebar to generate the dynamic dashboard.")
