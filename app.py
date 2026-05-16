import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
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

    /* PREMIUM SCOUTLAB PLAYER CARD DESIGN */
    .premium-player-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid #a47e3c;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
    }
    .premium-card-left {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .premium-player-img-wrapper {
        position: relative;
        width: 110px;
        height: 110px;
        border-radius: 50%;
        border: 3px solid #a47e3c;
        background-color: #1e293b;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 15px rgba(164, 126, 60, 0.4);
    }
    .premium-player-avatar {
        font-size: 55px;
    }
    .premium-player-meta h2 {
        margin: 0;
        font-size: 2rem !important;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .premium-player-meta p {
        margin: 4px 0 0 0;
        font-size: 1rem;
        color: #94a3b8;
        font-weight: 500;
    }
    .premium-card-right {
        display: flex;
        gap: 15px;
    }
    .premium-stat-tile {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(164, 126, 60, 0.3);
        border-radius: 12px;
        padding: 15px;
        min-width: 100px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .premium-stat-tile-large {
        background: linear-gradient(135deg, #a47e3c 0%, #6d4c1b 100%);
        border: 1px solid #a47e3c;
    }
    .premium-tile-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }
    .premium-tile-lbl {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 6px;
        letter-spacing: 0.5px;
    }
    .premium-stat-tile-large .premium-tile-lbl {
        color: #f1f5f9;
    }

    /* Player Performance Summary Table Theme with Neon Progress Bars */
    .summary-table-container {
        background: #1e293b;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
        margin-bottom: 25px;
        border: 1px solid rgba(164, 126, 60, 0.3);
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
        selected_defense = st.multiselect("Actions:", ["Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Counterpress", "Goals"], default=["Tackles", "Ground Duels", "Clearances", "Aerial Duels", "Counterpress", "Fouls", "Goals"])

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
            mlines.Line2D([], [], color='red', marker='x', label='Foul (Red X)', linestyle='None', markersize=10, markeredgewidth=2),
            mlines.Line2D([], [], color='black', marker='o', label='Counterpress (#)', linestyle='None', markersize=8),
            mlines.Line2D([], [], color='gold', marker='*', label='Goal', linestyle='None', markersize=12)
        ]

    # محرك البحث ورصد الماتريكس التكتيكي بالكامل (تصفية شاملة للأهداف وكل الإجراءات لايف)
    def parse_action_metrics(dataframe, ax, pitch_obj, layers, draw_mode=True, specific_type=None):
        matrix = {
            "total_passes": 0, "success_passes": 0, "crosses": 0, "success_crosses": 0,
            "through_balls": 0, "tackles": 0, "clearances": 0, "ground_duels_won": 0,
            "aerial_duels_won": 0, "fouls": 0, "counterpress": 0, "goals": 0
        }
        
        for i, row in dataframe.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'ناجح' in tag or 'won' in tag or 'win' in tag
            action_captured = False
            
            # رصد الأهداف أولاً لضمان تفاعلية الكروت لايف بنسبة 100%
            if 'goal' in act or 'goal' in tag or 'هدف' in act or 'هدف' in tag:
                matrix["goals"] += 1
                if draw_mode and (specific_type is None or specific_type == "defense") and "Goals" in layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=650, color='gold', edgecolors='black', ax=ax, zorder=6)

            # فئة التمرير والبينيات التقديمية
            if 'pass' in act or 'تمرير' in act:
                if 'through' in tag and "Through Balls" in layers:
                    if draw_mode and (specific_type is None or specific_type == "passes"):
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax, zorder=4)
                    matrix["through_balls"] += 1
                    action_captured = True
                elif "Normal Passes" in layers and not any(k in tag for k in ['cross', 'through', 'corner', 'free kick']):
                    if draw_mode and (specific_type is None or specific_type == "passes"):
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.5, zorder=3)
                    action_captured = True
                
                # فرز الركنيات والفاولات كتمريرات مستقلة
                elif 'corner' in tag and "Corners" in layers:
                    if draw_mode and (specific_type is None or specific_type == "crosses"):
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange' if is_success else 'red', ax=ax, zorder=4)
                    action_captured = True
                elif 'cross' in tag and "Crosses" in layers:
                    if draw_mode and (specific_type is None or specific_type == "crosses"):
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax, zorder=4)
                    matrix["crosses"] += 1
                    if is_success: matrix["success_crosses"] += 1
                    action_captured = True
                
                if action_captured:
                    matrix["total_passes"] += 1
                    if is_success: matrix["success_passes"] += 1

            # الفئات الدفاعية البحتة
            elif any(w in act for w in ['tackle', 'inter', 'تدخل', 'قطع', 'تكل', 'تاكلز']) and "Tackles" in layers:
                if draw_mode and (specific_type is None or specific_type == "defense"):
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=240, color='blue', linewidth=3, ax=ax, zorder=5)
                matrix["tackles"] += 1

            elif any(w in act for w in ['clear', 'clearance', 'تشتيت', 'ابعاد']) and "Clearances" in layers:
                if draw_mode Image and (specific_type is None or specific_type == "defense"):
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='d', s=200, color='purple', ax=ax, zorder=5)
                matrix["clearances"] += 1

            elif any(w in act for w in ['aerial', 'هوائي', 'طير', 'رأس']) and "Aerial Duels" in layers:
                if draw_mode and (specific_type is None or specific_type == "defense"):
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='^', s=220, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax, zorder=5)
                if is_success: matrix["aerial_duels_won"] += 1

            elif any(w in act for w in ['duel', 'التحام', 'صراع', 'أرضي', 'ground']) and 'aerial' not in act and "Ground Duels" in layers:
                if draw_mode and (specific_type is None or specific_type == "defense"):
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color='#2ecc71' if is_success else 'red', ax=ax, zorder=5)
                if is_success: matrix["ground_duels_won"] += 1

            elif any(w in act or w in tag for w in ['foul', 'خطأ', 'committed', 'suffered']) and "Fouls" in layers:
                if draw_mode and (specific_type is None or specific_type == "defense"):
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=240, color='red', linewidth=3, ax=ax, zorder=5)
                matrix["fouls"] += 1

            elif any(w in act or w in tag for w in ['counterpress', 'press', 'recovery', 'ضغط']) and "Counterpress" in layers:
                if draw_mode and (specific_type is None or specific_type == "defense"):
                    ax.text(row.x_scaled, row.y_scaled, '#', color='black', fontsize=22, fontweight='bold', ha='center', va='center', zorder=5)
                matrix["counterpress"] += 1
                
        return matrix

    # دالة بناء كارت اللاعب البروفيشينال (ScoutLab Tactical Shield Card)
    def render_premium_player_card(player_name, selected_team, stats):
        p_pct = (stats['success_passes']/stats['total_passes'])*100 if stats['total_passes'] > 0 else 0
        total_def = stats['tackles'] + stats['clearances'] + stats['ground_duels_won'] + stats['aerial_duels_won']
        calculated_rating = int(60 + (p_pct * 0.25) + (total_def * 0.5))
        if calculated_rating > 99: calculated_rating = 99

        st.markdown(f"""
            <div class="premium-player-card">
                <div class="premium-card-left">
                    <div class="premium-player-img-wrapper"><span class="premium-player-avatar">🏃‍♂️</span></div>
                    <div class="premium-player-meta">
                        <h2>{player_name}</h2>
                        <p>Club: {selected_team} | Tactical Scouting Profile</p>
                    </div>
                </div>
                <div class="premium-card-right">
                    <div class="premium-stat-tile premium-stat-tile-large">
                        <div class="premium-tile-val">{calculated_rating}</div>
                        <div class="premium-tile-lbl">Rating</div>
                    </div>
                    <div class="premium-stat-tile">
                        <div class="premium-tile-val">{stats['total_passes']}</div>
                        <div class="premium-tile-lbl">Passes</div>
                    </div>
                    <div class="premium-stat-tile">
                        <div class="premium-tile-val">{p_pct:.0f}%</div>
                        <div class="premium-tile-lbl">Accuracy</div>
                    </div>
                    <div class="premium-stat-tile">
                        <div class="premium-tile-val">{total_def}</div>
                        <div class="premium-tile-lbl">Def. Stats</div>
                    </div>
                    <div class="premium-stat-tile">
                        <div class="premium-tile-val">{stats['goals']}</div>
                        <div class="premium-tile-lbl">Goals</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # لايف داشبورد بالكامل بارات نيون ملعلعة تفاعلية 100%
    def render_player_summary_table(player_name, stats, active_layers):
        p_pct = (stats['success_passes']/stats['total_passes'])*100 if stats['total_passes'] > 0 else 0
        c_pct = (stats['success_crosses']/stats['crosses'])*100 if stats['crosses'] > 0 else 0
        
        # ربط قيم البارات لايف بالفلاتر النشطة
        def get_live_bar_html(val, max_val=15):
            pct = (val / max_val) * 100 if val > 0 else 0
            if pct > 100: pct = 100
            return f'<div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {pct}%;"></div></div>'

        st.markdown(f"""
            <div class="summary-table-container">
                <div class="summary-title">📊 Live Interactive Summary Table (All-Bars Dashboard)</div>
                <table class="player-summary-table">
                    <thead><tr><th>Metric Category</th><th>Attempts Count</th><th>Visual Live Progress Bar</th></tr></thead>
                    <tbody>
                        <tr><td><b>Total Passing</b></td><td>{stats['total_passes'] if "Normal Passes" in active_layers else 0}</td><td>{get_live_bar_html(stats['total_passes'] if "Normal Passes" in active_layers else 0, 40)} <span class="stat-badge">{p_pct:.1f}% Acc</span></td></tr>
                        <tr><td><b>Crosses Matrix</b></td><td>{stats['crosses'] if "Crosses" in active_layers else 0}</td><td>{get_live_bar_html(stats['crosses'] if "Crosses" in active_layers else 0, 15)} <span class="stat-badge">{c_pct:.1f}% Acc</span></td></tr>
                        <tr><td><b>Through Balls</b></td><td>{stats['through_balls'] if "Through Balls" in active_layers else 0}</td><td>{get_live_bar_html(stats['through_balls'] if "Through Balls" in active_layers else 0)} <span class="stat-badge">Live</span></td></tr>
                        <tr><td><b>Defensive Tackles</b></td><td>{stats['tackles'] if "Tackles" in active_layers else 0}</td><td>{get_live_bar_html(stats['tackles'] if "Tackles" in active_layers else 0)} <span class="stat-badge">Live</span></td></tr>
                        <tr><td><b>Clearances (تشتيت)</b></td><td>{stats['clearances'] if "Clearances" in active_layers else 0}</td><td>{get_live_bar_html(stats['clearances'] if "Clearances" in active_layers else 0)} <span class="stat-badge">Live</span></td></tr>
                        <tr><td><b>Ground Duels Won</b></td><td>{stats['ground_duels_won'] if "Ground Duels" in active_layers else 0}</td><td>{get_live_bar_html(stats['ground_duels_won'] if "Ground Duels" in active_layers else 0)} <span class="stat-badge">Won</span></td></tr>
                        <tr><td><b>Aerial Duels Won</b></td><td>{stats['aerial_duels_won'] if "Aerial Duels" in active_layers else 0}</td><td>{get_live_bar_html(stats['aerial_duels_won'] if "Aerial Duels" in active_layers else 0)} <span class="stat-badge">Won</span></td></tr>
                        <tr><td><b>Fouls Operations</b></td><td>{stats['fouls'] if "Fouls" in active_layers else 0}</td><td>{get_live_bar_html(stats['fouls'] if "Fouls" in active_layers else 0)} <span class="stat-badge">Live</span></td></tr>
                        <tr><td><b>Counterpress (#)</b></td><td>{stats['counterpress'] if "Counterpress" in active_layers else 0}</td><td>{get_live_bar_html(stats['counterpress'] if "Counterpress" in active_layers else 0)} <span class="stat-badge">Live</span></td></tr>
                        <tr><td style="color: gold; font-weight: bold;">⚽ Goals Scored</td><td>{stats['goals'] if "Goals" in active_layers else 0}</td><td>{get_live_bar_html(stats['goals'] if "Goals" in active_layers else 0, 5)} <span class="stat-badge" style="background-color: #fef08a; color: #854d0e;">Live Target</span></td></tr>
                    </tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)

    # --- التبويبات الفنية الفخمة المنفصلة بالكامل ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Player Profile Summary", 
        "🔥 Player Tactical Heatmap", 
        "🏃‍♂️ Player Actions Map",
        "👥 Team Strategy Lab"
    ])

    player_list = sorted(team_df['Player'].dropna().unique().tolist())
    player_options = {p: f"🛡️ {p}" for p in player_list}

    # 1. التابة الأولى: الكارت الفخم وجدول البارات بالكامل تفاعلي لايف
    with tab1:
        sel_player_t1 = st.selectbox("🎯 Focus Player (Summary):", options=player_list, format_func=lambda x: player_options[x], key="sb_t1")
        p_df_t1 = team_df[team_df['Player'] == sel_player_t1].copy()
        p_stats_t1 = parse_action_metrics(p_df_t1, None, None, all_selected_layers, draw_mode=False)
        
        render_premium_player_card(sel_player_t1, selected_team, p_stats_t1)
        render_player_summary_table(sel_player_t1, p_stats_t1, all_selected_layers)

    # 2. التابة الثانية: خريطة حرارية لوحدها بكامل العرض وبألوان سكاوت لاب النارية
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

    # 3. التابة الثالثة: تفكيك الـ Player Actions Map لـ 3 خرائط منفصلة تماماً تحت بعض لسهولة السكرين شوتس
    with tab3:
        sel_player_t3 = st.selectbox("🎯 Focus Player (Actions Maps):", options=player_list, format_func=lambda x: player_options[x], key="sb_t3")
        p_df_t3 = team_df[team_df['Player'] == sel_player_t3].copy()
        
        # خريطة 1: التمريرات العادية والبينيات
        st.markdown("<h3 style='color: #2ecc71;'>📐 Map 1: Normal & Through Passes</h3>", unsafe_allow_html=True)
        pitch_m1 = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_m1, ax_m1 = pitch_m1.draw(figsize=(11, 7))
        add_club_logo(ax_m1)
        parse_action_metrics(p_df_t3, ax_m1, pitch_m1, all_selected_layers, draw_mode=True, specific_type="passes")
        st.pyplot(fig_m1)
        
        st.markdown("---")
        
        # خريطة 2: الكروسات والركنيات العرضية
        st.markdown("<h3 style='color: #38bdf8;'>🏹 Map 2: Crosses & Corners Matrix</h3>", unsafe_allow_html=True)
        pitch_m2 = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_m2, ax_m2 = pitch_m2.draw(figsize=(11, 7))
        add_club_logo(ax_m2)
        parse_action_metrics(p_df_t3, ax_m2, pitch_m2, all_selected_layers, draw_mode=True, specific_type="crosses")
        st.pyplot(fig_m2)
        
        st.markdown("---")
        
        # خريطة 3: مصفوفة الإجراءات الدفاعية والضغط والفاولات بالكامل
        st.markdown("<h3 style='color: #a47e3c;'>🛡️ Map 3: Complete Defensive & Combat Matrix</h3>", unsafe_allow_html=True)
        pitch_m3 = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_m3, ax_m3 = pitch_m3.draw(figsize=(11, 7))
        add_club_logo(ax_m3)
        parse_action_metrics(p_df_t3, ax_m3, pitch_m3, all_selected_layers, draw_mode=True, specific_type="defense")
        ax_m3.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#ffffff', edgecolor='#e2e8f0')
        st.pyplot(fig_m3)

    # 4. التابة الرابعة: تابة التحاليل الجماعية للفريق بالكامل
    with tab4:
        st.subheader(f"👥 Global Team Level Analysis: {selected_team}")
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("<h3 style='text-align: center; color: #38bdf8;'>🔥 Team Heatmap</h3>", unsafe_allow_html=True)
            pitch_th = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_th, ax_th = pitch_th.draw(figsize=(8, 6))
            
            scout_lab_colors = ["#3b82f6", "#10b981", "#facc15", "#f97316", "#7f1d1d"]
            scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab", scout_lab_colors, N=256)
            
            if len(team_df) > 1:
                sns.kdeplot(x=team_df['x_scaled'], y=team_df['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.01, alpha=0.82, bw_method=0.3, zorder=1, ax=ax_th)
            add_club_logo(ax_th)
            st.pyplot(fig_th)
            
        with col_t2:
            st.markdown("<h3 style='text-align: center; color: #a47e3c;'>🛡️ Team Actions Map</h3>", unsafe_allow_html=True)
            pitch_td = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#22312b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_td, ax_td = pitch_td.draw(figsize=(8, 6))
            
            add_club_logo(ax_td)
            parse_action_metrics(team_df, ax_td, pitch_td, all_selected_layers, draw_mode=True)
            ax_td.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='x-small', framealpha=1, facecolor='#ffffff', edgecolor='#e2e8f0')
            st.pyplot(fig_td)

else:
    st.info("👋 Please upload a match CSV file on the left sidebar to generate the dynamic dashboard.")
