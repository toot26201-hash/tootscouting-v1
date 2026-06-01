
# Map 1: Team Analysis
        pitch_all = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_all, ax_all = pitch_all.draw(figsize=(12, 9))
        fig_all.patch.set_facecolor('#ffffff')
        parse_action_metrics(team_df, ax_all, pitch_all, all_selected_layers, draw_mode=True, specific_type="all")
        
        ax_all.legend(
            handles=get_full_legend(), 
            loc='upper left', 
            bbox_to_anchor=(1.01, 1), 
            fontsize='small', 
            framealpha=1, 
            facecolor='white', 
            edgecolor='black', 
            labelcolor='black'
        )
        st.pyplot(fig_all)
        
        st.markdown("---")
        st.markdown(f"<h3 style='text-align: center; color: #a47e3c;'>🛡️ Map 2: Team Defensive & Combat Matrix</h3>", unsafe_allow_html=True)
        
        # Map 2: Team Defensive
        pitch_td = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_td, ax_td = pitch_td.draw(figsize=(12, 9))
        fig_td.patch.set_facecolor('#ffffff')
        parse_action_metrics(team_df, ax_td, pitch_td, all_selected_layers, draw_mode=True, specific_type="defensive")
        
        ax_td.legend(
            handles=get_full_legend(), 
            loc='upper left', 
            bbox_to_anchor=(1.01, 1), 
            fontsize='small', 
            framealpha=1, 
            facecolor='white', 
            edgecolor='black', 
            labelcolor='black'
        )
        st.pyplot(fig_td)# --- التعديل في خريطة الفريق (Map 1) ---
ax_all.legend(
    handles=get_full_legend(), 
    loc='upper left', 
    bbox_to_anchor=(1.01, 1), 
    fontsize='small', 
    framealpha=1,          # خلفية غير شفافة
    facecolor='white',     # خلفية بيضاء
    edgecolor='black',     # إطار أسود
    labelcolor='black'     # نص أسود
)

# --- التعديل في خريطة الدفاع (Map 2) ---
ax_td.legend(
    handles=get_full_legend(), 
    loc='upper left', 
    bbox_to_anchor=(1.01, 1), 
    fontsize='small', 
    framealpha=1,          # خلفية غير شفافة
    facecolor='white',     # خلفية بيضاء
    edgecolor='black',     # إطار أسود
    labelcolor='black'     # نص أسود
)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
from PIL import Image
import os
import matplotlib.colors as mcolors
import numpy as np
import base64

# Function to read and encode the club logo to Base64
def get_base64_logo():
    current_dir = os.path.dirname(__file__)
    possible_paths = [
        os.path.join(current_dir, 'Espoon_Palloseura_logo.png'),
        os.path.join(current_dir, 'espoon_palloseura_logo.png'),
        'Espoon_Palloseura_logo.png',
        'espoon_palloseura_logo.png'
    ]
    logo_filename = None
    for path in possible_paths:
        if os.path.exists(path):
            logo_filename = path
            break
    if logo_filename and os.path.exists(logo_filename):
        with open(logo_filename, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# Page Config & Strict Dark Premium Theme (TootScouting Global Style)
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

st.markdown("""
    <style>
    /* Global Background and Text Color */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: #f8fafc !important;
    }
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- بقية الدوال الخاصة بك (تأكد من وجودها بنفس الترتيب في ملفك) ---
# ... get_full_legend(), parse_action_metrics() ...

# --- عند رسم الخرائط، استخدم هذا التنسيق المحدث للـ Legend ---

# خريطة 1:
ax_all.legend(
    handles=get_full_legend(), 
    loc='upper left', 
    bbox_to_anchor=(1.01, 1), 
    fontsize='small', 
    framealpha=1, 
    facecolor='#0f172a', 
    edgecolor='#334155',
    labelcolor='white'  # هنا التعديل ليصبح النص أبيض
)

# خريطة 2:
ax_td.legend(
    handles=get_full_legend(), 
    loc='upper left', 
    bbox_to_anchor=(1.01, 1), 
    fontsize='small', 
    framealpha=1, 
    facecolor='#0f172a', 
    edgecolor='#334155',
    labelcolor='white'  # هنا التعديل ليصبح النص أبيض
ax_all.legend(
            handles=get_full_legend(), 
            loc='upper left', 
            bbox_to_anchor=(1.01, 1), 
            fontsize='small', 
            framealpha=1, 
            facecolor='white', 
            edgecolor='black', 
            labelcolor='black'
        )
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
from PIL import Image
import os
import matplotlib.colors as mcolors
import numpy as np
import base64

# Function to read and encode the club logo to Base64
def get_base64_logo():
    current_dir = os.path.dirname(__file__)
    possible_paths = [
        os.path.join(current_dir, 'Espoon_Palloseura_logo.png'),
        os.path.join(current_dir, 'espoon_palloseura_logo.png'),
        'Espoon_Palloseura_logo.png',
        'espoon_palloseura_logo.png'
    ]
    logo_filename = None
    for path in possible_paths:
        if os.path.exists(path):
            logo_filename = path
            break
    if logo_filename and os.path.exists(logo_filename):
        with open(logo_filename, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# Page Config & Strict Dark Premium Theme (TootScouting Global Style)
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

st.markdown("""
    <style>
    /* Global Background and Text Color */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #334155;
    }
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #f8fafc !important;
    }
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

    /* CYBER GLOW GLOWING PLAYER CARD DESIGN */
    .premium-player-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%);
        border: 2px solid #38bdf8;
        border-radius: 20px;
        padding: 26px;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.7), inset 0 0 20px rgba(56, 189, 248, 0.2);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
        animation: cardGlowPulse 4s infinite alternate;
    }
    @keyframes cardGlowPulse {
        0% { box-shadow: 0 0 20px rgba(56, 189, 248, 0.5); }
        100% { box-shadow: 0 0 35px rgba(56, 189, 248, 0.9); }
    }
    .premium-card-left {
        display: flex;
        align-items: center;
        gap: 20px;
        z-index: 2;
    }
    .premium-player-img-wrapper {
        position: relative;
        width: 115px;
        height: 115px;
        border-radius: 50%;
        border: 3px solid #fbbf24;
        background-color: #ffffff !important; 
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.8);
        overflow: hidden;
    }
    .premium-player-logo-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 6px;
    }
    .premium-player-meta h2 {
        margin: 0;
        font-size: 2.2rem !important;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 0 0 10px rgba(255,255,255,0.4);
    }
    .premium-player-meta p {
        margin: 4px 0 0 0;
        font-size: 1rem;
        color: #38bdf8;
        font-weight: 600;
    }
    .premium-card-right {
        display: flex;
        gap: 15px;
        z-index: 2;
    }
    .premium-stat-tile {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 14px;
        padding: 16px;
        min-width: 105px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    }
    .premium-stat-tile-large {
        background: linear-gradient(135deg, #0284c7 0%, #1e3a8a 100%);
        border: 2px solid #38bdf8;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.8);
    }
    .premium-tile-val {
        font-size: 2rem;
        font-weight: 900;
        color: #ffffff;
        line-height: 1;
        text-shadow: 0 0 8px rgba(255,255,255,0.6);
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

    /* Progress Table Container */
    .summary-table-container {
        background: #1e293b;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
        margin-bottom: 25px;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .summary-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 16px;
        border-bottom: 2px solid #38bdf8;
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
       ax.legend(
            handles=...,  # اتركها كما هي في كودك
            loc='upper left', 
            bbox_to_anchor=(1.01, 1), 
            fontsize='small', 
            framealpha=1, 
            facecolor='white',    # تغيير الخلفية للأبيض
            edgecolor='black',    # إطار أسود
ax.legend(
            handles=...,  # اتركها كما هي في كودك
            loc='upper left', 
            bbox_to_anchor=(1.01, 1), 
            fontsize='small', 
            framealpha=1, 
            facecolor='white',    # تغيير الخلفية للأبيض
            edgecolor='black',    # إطار أسود
            labelcolor='black'    # نصوص سوداء
        )        )
    }
    .stat-badge {
        background-color: #0f172a;
ax.legend(
            handles=...,  # اتركها كما هي في كودك
            loc='upper left', 
            bbox_to_anchor=(1.01, 1), 
            fontsize='small', 
            framealpha=1, 
            facecolor='white',    # تغيير الخلفية للأبيض
            edgecolor='black',    # إطار أسود
            labelcolor='black'    # نصوص سوداء
        )        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }
    .progress-bar-bg {
        background-color: #0f172a;
        border-radius: 6px;
        width: 140px;
        height: 12px;
       ax.legend(
            handles=...,  # اتركها كما هي في كودك
            loc='upper left', 
            bbox_to_anchor=(1.01, 1), 
            fontsize='small', 
            framealpha=1, 
            facecolor='white',    # تغيير الخلفية للأبيض
            edgecolor='black',    # إطار أسود
ax.legend(
            handles=...,  # اتركها كما هي في كودك
            loc='upper left', 
            bbox_to_anchor=(1.01, 1), 
            fontsize='small', 
            framealpha=1, 
            facecolor='white',    # تغيير الخلفية للأبيض
            edgecolor='black',    # إطار أسود
            labelcolor='black'    # نصوص سوداء
        )        )
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

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- Sidebar Controls ---
st.sidebar.markdown("## 🛠️ Tactical Control Unit")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8-sig')
    except Exception as e:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='cp1252')

    # تنظيف وتوحيد أسماء الأعمدة لحالة الأحرف الصغيرة لمنع حساسيتها
    df.columns = df.columns.str.strip()
    
    # ميكانيكية Mapping مرنة وذكية للأعمدة الأساسية
    rename_dict = {}
    for col in df.columns:
        c_low = col.lower().replace('_', ' ').strip()
        if 'event type' in c_low or 'eventtype' in c_low or c_low == 'action' or c_low == 'event' or c_low == 'action type':
            rename_dict[col] = 'Action'
        elif 'players' in c_low or c_low == 'player' or c_low == 'player name':
            rename_dict[col] = 'Player'
        elif 'tag' in c_low or 'tags' in c_low:
            rename_dict[col] = 'Tags'
            
    if rename_dict:
        df = df.rename(columns=rename_dict)

    if 'Action' not in df.columns or 'Player' not in df.columns:
        st.sidebar.error("⚠️ لم نتمكن من تحديد أعمدة اللاعبين أو الأحداث تلقائياً. تأكد من وجود عمود باسم Player و Action.")
    
    df['Team'] = 'EPS'
    df = df.dropna(subset=['Action', 'Player'])
    df['Tags'] = df['Tags'].fillna('')
    df['Player'] = df['Player'].astype(str).str.strip()

    # نظام كشف ذكي وإصلاح إحداثيات الملعب (Flexible Coordinate Finder)
    col_map_lower = {c.lower().replace('_', ' ').strip(): c for c in df.columns}
    
    x_start_col = col_map_lower.get('x start') or col_map_lower.get('x') or col_map_lower.get('xstart')
    y_start_col = col_map_lower.get('y start') or col_map_lower.get('y') or col_map_lower.get('ystart')
    x_end_col = col_map_lower.get('x end') or col_map_lower.get('xend')
    y_end_col = col_map_lower.get('y end') or col_map_lower.get('yend')

    if x_start_col and y_start_col:
        df['x_scaled'] = df[x_start_col] if df[x_start_col].max() > 1 else df[x_start_col] * 120
        df['y_scaled'] = df[y_start_col] if df[y_start_col].max() > 1 else df[y_start_col] * 80
        
        if x_end_col and y_end_col:
            df['x_end_scaled'] = df[x_end_col] if df[x_end_col].max() > 1 else df[x_end_col] * 120
            df['y_end_scaled'] = df[y_end_col] if df[y_end_col].max() > 1 else df[y_end_col] * 80 
        else:
            df['x_end_scaled'] = df['x_scaled']
            df['y_end_scaled'] = df['y_scaled']
    else:
        st.sidebar.error("⚠️ لم نجد أعمدة الإحداثيات (X, Y) في الملف المرفوع!")

    team_list = ['EPS']
    selected_team = st.sidebar.selectbox("📋 Select Team", team_list)
    team_df = df.copy()

    with st.sidebar.expander("🎯 Passing & Attack Filters", expanded=True):
        selected_passes = st.multiselect("Pass & Attack Types:", ["Normal Passes", "Crosses", "Through Balls", "Key Passes", "Corners", "Shots", "Goals"], default=["Normal Passes", "Crosses", "Shots", "Goals"])
        
    with st.sidebar.expander("🛡️ Defensive Filters", expanded=True):
        selected_defense = st.multiselect("Actions:", ["Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Counterpress"], default=["Tackles", "Ground Duels", "Clearances", "Aerial Duels", "Counterpress"])

    all_selected_layers = selected_passes + selected_defense

    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', label='Pass Success', markersize=8),
            mlines.Line2D([], [], color='#e74c3c', marker='>', linestyle='-', label='Pass Failed', markersize=8),
            mlines.Line2D([], [], color='#38bdf8', marker='>', linestyle='-', label='Cross Success', markersize=8),
            mlines.Line2D([], [], color='#ef4444', marker='>', linestyle='--', label='Cross Failed', markersize=8),
            mlines.Line2D([], [], color='#FF69B4', marker='>', linestyle='-', label='Through Ball', markersize=8),
            mlines.Line2D([], [], color='#fbbf24', marker='>', linestyle='-', label='Key Pass 🔑', markersize=10, linewidth=3),
            mlines.Line2D([], [], color='#3b82f6', marker='*', label='Shot On-Target (Blue 🌟)', linestyle='None', markersize=12),
            mlines.Line2D([], [], color='#ef4444', marker='*', label='Shot Off-Target (Red 🌟)', linestyle='None', markersize=12),
            mlines.Line2D([], [], color='#60a5fa', marker='x', label='Tackle (Blue X)', linestyle='None', markersize=10, markeredgewidth=2),
            mlines.Line2D([], [], color='#c084fc', marker='d', label='Clearance', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#34d399', marker='s', label='Ground Duel Won', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#f87171', marker='s', label='Ground Duel Lost', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#34d399', marker='^', label='Aerial Won', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#f87171', marker='^', label='Aerial Lost', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#f87171', marker='x', label='Foul (Red X)', linestyle='None', markersize=10, markeredgewidth=2),
            mlines.Line2D([], [], color='#0f172a', marker='o', label='Counterpress (#)', linestyle='None', markersize=8),
            mlines.Line2D([], [], color='#fbbf24', marker='*', label='Goal Confirmed ⚽', linestyle='None', markersize=15)
        ]

    def parse_action_metrics(dataframe, ax, pitch_obj, layers, draw_mode=True, specific_type=None):
        matrix = {
            "total_passes": 0, "success_passes": 0, "crosses": 0, "success_crosses": 0,
            "through_balls": 0, "key_passes": 0, "tackles": 0, "clearances": 0, "ground_duels_won": 0,
            "aerial_duels_won": 0, "fouls": 0, "counterpress": 0, "goals": 0, "shots_on_target": 0, "shots_off_target": 0
        }
        for i, row in dataframe.iterrows():
            if 'x_scaled' not in dataframe.columns or 'y_scaled' not in dataframe.columns:
                continue
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'won' in tag or 'win' in tag or 'recovery' in tag or 'pass' in tag
            if 'failed' in tag or 'failure' in tag: is_success = False
            
            if 'goal' in act or 'goal' in tag:
                matrix["goals"] += 1
                if draw_mode and (specific_type is None or specific_type == "passes" or specific_type == "all") and "Goals" in layers:
                    pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=750, color='#fbbf24', edgecolors='black', ax=ax, zorder=6)

            if 'shot' in act or 'sh/a' in act:
                if is_success:
                    matrix["shots_on_target"] += 1
                    if draw_mode and (specific_type is None or specific_type == "passes" or specific_type == "all") and "Shots" in layers:
                        pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=450, color='#3b82f6', edgecolors='black', ax=ax, zorder=5)
                else:
                    matrix["shots_off_target"] += 1
                    if draw_mode and (specific_type is None or specific_type == "passes" or specific_type == "all") and "Shots" in layers:
                        pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=450, color='#ef4444', edgecolors='black', ax=ax, zorder=5)

            if 'pass' in act:
                action_captured = False
                if 'key' in tag or 'key pass' in tag:
                    matrix["key_passes"] += 1
                    if draw_mode and (specific_type is None or specific_type == "passes" or specific_type == "all") and "Key Passes" in layers:
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=3, color='#fbbf24', ax=ax, zorder=4)
                    action_captured = True
                elif 'through' in tag and "Through Balls" in layers:
                    if draw_mode and (specific_type is None or specific_type == "passes" or specific_type == "all"):
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax, zorder=4)
                    matrix["through_balls"] += 1
                    action_captured = True
                elif "Normal Passes" in layers and not any(k in tag for k in ['cross', 'through', 'corner']):
                    if draw_mode and (specific_type is None or specific_type == "passes" or specific_type == "all"):
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.6, zorder=3)
                    action_captured = True
                elif 'corner' in tag and "Corners" in layers:
                    if draw_mode and (specific_type is None or specific_type == "crosses" or specific_type == "all"):
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#fbbf24' if is_success else '#ef4444', ax=ax, zorder=4)
                    action_captured = True
                elif 'cross' in tag and "Crosses" in layers:
                    if draw_mode and (specific_type is None or specific_type == "crosses" or specific_type == "all"):
                        pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#38bdf8' if is_success else '#ef4444', linestyle='solid' if is_success else 'dashed', ax=ax, zorder=4)
                    matrix["crosses"] += 1
                    if is_success: matrix["success_crosses"] += 1
                    action_captured = True
                if action_captured:
                    matrix["total_passes"] += 1
                    if is_success: matrix["success_passes"] += 1

            elif 'extraction' in act or 'tackle' in act or 'clearance' in act:
                if 'clearance' in tag or 'clearance' in act:
                    if "Clearances" in layers:
                        if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "all"):
                            pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='d', s=200, color='#c084fc', ax=ax, zorder=5)
                    matrix["clearances"] += 1
                else:
                    if "Tackles" in layers:
                        if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "all"):
                            pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=240, color='#60a5fa', linewidth=3, ax=ax, zorder=5)
                    matrix["tackles"] += 1

            elif 'aerial' in act:
                if "Aerial Duels" in layers:
                    if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "all"):
                        pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='^', s=220, color='#34d399' if is_success else '#f87171', edgecolors='black', ax=ax, zorder=5)
                if is_success: matrix["aerial_duels_won"] += 1

            elif 'ground' in act or 'duel' in act:
                if "Ground Duels" in layers:
                    if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "all"):
                        pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='s', s=200, color='#34d399' if is_success else '#f87171', edgecolors='black', ax=ax, zorder=5)
                if is_success: matrix["ground_duels_won"] += 1

            elif 'foul' in act or 'fouls' in act:
                if "Fouls" in layers:
                    if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "all"):
                        pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=240, color='#ef4444', linewidth=3, ax=ax, zorder=5)
                matrix["fouls"] += 1

            elif 'press' in act or 'recovery' in tag or 'interception' in act:
                if "Counterpress" in layers:
                    if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "all"):
                        ax.text(row.x_scaled, row.y_scaled, '#', color='#0f172a', fontsize=22, fontweight='bold', ha='center', va='center', zorder=5)
                matrix["counterpress"] += 1
        return matrix

    def draw_premium_kde_heatmap(dataframe, ax):
        scout_lab_colors = ["#ffffff", "#e0f2fe", "#7dd3fc", "#0ea5e9", "#fbbf24", "#ef4444"]
        scout_cmap = mcolors.LinearSegmentedColormap.from_list("scout_lab_light", scout_lab_colors, N=256)
        sns.kdeplot(x=dataframe['x_scaled'], y=dataframe['y_scaled'], cmap=scout_cmap, fill=True, thresh=0.05, alpha=0.7, bw_method=0.28, zorder=1, ax=ax)

    def render_premium_player_card(player_name, selected_team, stats):
        p_pct = (stats['success_passes']/stats['total_passes'])*100 if stats['total_passes'] > 0 else 0
        total_def = stats['tackles'] + stats['clearances'] + stats['ground_duels_won'] + stats['aerial_duels_won']
        total_shots = stats['shots_on_target'] + stats['shots_off_target']
        calculated_rating = int(60 + (p_pct * 0.25) + (total_def * 0.5) + (stats['shots_on_target'] * 0.8) + (stats['key_passes'] * 1.2))
        if calculated_rating > 99: calculated_rating = 99
        logo_b64 = get_base64_logo()
        avatar_html = f'<img src="data:image/png;base64,{logo_b64}" class="premium-player-logo-img" />' if logo_b64 else '<span class="premium-player-avatar">🏃‍♂️</span>'
        st.markdown(f"""
            <div class="premium-player-card">
                <div class="premium-card-left">
                    <div class="premium-player-img-wrapper">{avatar_html}</div>
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
                        <div class="premium-tile-val">{stats['key_passes']}</div>
                        <div class="premium-tile-lbl">Key Passes 🔑</div>
                    </div>
                    <div class="premium-stat-tile">
                        <div class="premium-tile-val">{total_shots}</div>
                        <div class="premium-tile-lbl">Shots Total</div>
                    </div>
                    <div class="premium-stat-tile">
                        <div class="premium-tile-val">{stats['goals']}</div>
                        <div class="premium-tile-lbl">Goals</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    def render_player_summary_table(player_name, stats, active_layers):
        p_pct = (stats['success_passes']/stats['total_passes'])*100 if stats['total_passes'] > 0 else 0
        current_pct = (stats['success_crosses']/stats['crosses'])*100 if stats['crosses'] > 0 else 0
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
                        <tr><td><b>Crosses Matrix</b></td><td>{stats['crosses'] if "Crosses" in active_layers else 0}</td><td>{get_live_bar_html(stats['crosses'] if "Crosses" in active_layers else 0, 15)} <span class="stat-badge">{current_pct:.1f}% Acc</span></td></tr>
                        <tr><td><b>Through Balls</b></td><td>{stats['through_balls'] if "Through Balls" in active_layers else 0}</td><td>{get_live_bar_html(stats['through_balls'] if "Through Balls" in active_layers else 0)} <span class="stat-badge">Live</span></td></tr>
                        <tr><td><b style="color: #fbbf24;">🔑 Key Passes</b></td><td>{stats['key_passes'] if "Key Passes" in active_layers else 0}</td><td>{get_live_bar_html(stats['key_passes'] if "Key Passes" in active_layers else 0, 10)} <span class="stat-badge" style="background-color: #fef08a; color: #854d0e;">Chances</span></td></tr>
                        <tr><td><b style="color: #3b82f6;">🌟 Shots On-Target</b></td><td>{stats['shots_on_target'] if "Shots" in active_layers else 0}</td><td>{get_live_bar_html(stats['shots_on_target'] if "Shots" in active_layers else 0, 8)} <span class="stat-badge" style="background-color: #93c5fd; color: #1e3a8a;">🎯 On Goal</span></td></tr>
                        <tr><td><b style="color: #ef4444;">🌟 Shots Off-Target</b></td><td>{stats['shots_off_target'] if "Shots" in active_layers else 0}</td><td>{get_live_bar_html(stats['shots_off_target'] if "Shots" in active_layers else 0, 8)} <span class="stat-badge" style="background-color: #fca5a5; color: #7f1d1d;">Missed</span></td></tr>
                        <tr><td><b>Defensive Tackles</b></td><td>{stats['tackles'] if "Tackles" in active_layers else 0}</td><td>{get_live_bar_html(stats['tackles'] if "Tackles" in active_layers else 0)} <span class="stat-badge">Live</span></td></tr>
                        <tr><td><b>Clearances</b></td><td>{stats['clearances'] if "Clearances" in active_layers else 0}</td><td>{get_live_bar_html(stats['clearances'] if "Clearances" in active_layers else 0)} <span class="stat-badge">Live</span></td></tr>
                        <tr><td><b>Ground Duels Won</b></td><td>{stats['ground_duels_won'] if "Ground Duels" in active_layers else 0}</td><td>{get_live_bar_html(stats['ground_duels_won'] if "Ground Duels" in active_layers else 0)} <span class="stat-badge">Won</span></td></tr>
                        <tr><td><b>Aerial Duels Won</b></td><td>{stats['aerial_duels_won'] if "Aerial Duels" in active_layers else 0}</td><td>{get_live_bar_html(stats['aerial_duels_won'] if "Aerial Duels" in active_layers else 0)} <span class="stat-badge">Won</span></td></tr>
                        <tr><td><b>Fouls Operations</b></td><td>{stats['fouls'] if "Fouls" in active_layers else 0}</td><td>{get_live_bar_html(stats['fouls'] if "Fouls" in active_layers else 0)} <span class="stat-badge">Live</span></td></tr>
                        <tr><td><b>Counterpress Actions (#)</b></td><td>{stats['counterpress'] if "Counterpress" in active_layers else 0}</td><td>{get_live_bar_html(stats['counterpress'] if "Counterpress" in active_layers else 0)} <span class="stat-badge">Live</span></td></tr>
                        <tr><td style="color: gold; font-weight: bold;">Goals Scored</td><td>{stats['goals'] if "Goals" in active_layers else 0}</td><td>{get_live_bar_html(stats['goals'] if "Goals" in active_layers else 0, 5)} <span class="stat-badge" style="background-color: #fef08a; color: #854d0e;">Net Shaken</span></td></tr>
                    </tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔥 Player Tactical Heatmap", 
        "🏃‍♂️ Player Actions Map",
        "📊 Player Performance Stats",
        "👥 Team Tactical Heatmap",
        "🛡️ Team Actions Map"
    ])
    player_list = sorted([p for p in team_df['Player'].dropna().unique().tolist() if str(p).strip() != ''])

    if len(player_list) > 0:
        player_options = {p: f"🛡️ {p}" for p in player_list}
        with tab1:
            sel_player_t1 = st.selectbox("🎯 Focus Player (Heatmap):", options=player_list, format_func=lambda x: player_options[x], key="sb_t1")
            p_df_t1 = team_df[team_df['Player'] == sel_player_t1].copy()
            pitch_h = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_h, ax_h = pitch_h.draw(figsize=(12, 9))
            fig_h.patch.set_facecolor('#ffffff')
            if len(p_df_t1) > 0:
                draw_premium_kde_heatmap(p_df_t1, ax_h)
            ax_h.text(60, 40, str(sel_player_t1), fontsize=32, color='#0f172a', alpha=0.08, fontweight='bold', ha='center', va='center', zorder=2)
            st.pyplot(fig_h)

        with tab2:
            sel_player_t2 = st.selectbox("🎯 Focus Player (Actions Maps):", options=player_list, format_func=lambda x: player_options[x], key="sb_t2")
            p_df_t2 = team_df[team_df['Player'] == sel_player_t2].copy()
            
            st.markdown("<h3 style='color: #38bdf8; text-align: center;'>🌍 Map 1: Player Full Performance Map (Attack & Defense Summary)</h3>", unsafe_allow_html=True)
            pitch_ind_all = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_ind_all, ax_ind_all = pitch_ind_all.draw(figsize=(12, 9))
            fig_ind_all.patch.set_facecolor('#ffffff')
            parse_action_metrics(p_df_t2, ax_ind_all, pitch_ind_all, all_selected_layers, draw_mode=True, specific_type="all")
            ax_ind_all.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#0f172a', edgecolor='#334155')
            ax_ind_all.text(60, 40, str(sel_player_t2), fontsize=32, color='#0f172a', alpha=0.07, fontweight='bold', ha='center', va='center', zorder=2)
            st.pyplot(fig_ind_all)
            
            st.markdown("---")
            st.markdown("<h3 style='color: #2ecc71;'>📐 Map 2: Normal, Through, Key Passes & Shots Matrix</h3>", unsafe_allow_html=True)
            pitch_m1 = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_m1, ax_m1 = pitch_m1.draw(figsize=(11, 7))
            fig_m1.patch.set_facecolor('#ffffff')
            parse_action_metrics(p_df_t2, ax_m1, pitch_m1, all_selected_layers, draw_mode=True, specific_type="passes")
            ax_m1.legend(handles=[get_full_legend()[4], get_full_legend()[5], get_full_legend()[6], get_full_legend()[7]], loc='upper right', fontsize='small', facecolor='#0f172a', edgecolor='#334155')
            ax_m1.text(60, 40, str(sel_player_t2), fontsize=28, color='#0f172a', alpha=0.07, fontweight='bold', ha='center', va='center', zorder=2)
            st.pyplot(fig_m1)
            
            st.markdown("---")
            st.markdown("<h3 style='color: #38bdf8;'>🏹 Map 3: Crosses & Corners Matrix</h3>", unsafe_allow_html=True)
            pitch_m2 = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_m2, ax_m2 = pitch_m2.draw(figsize=(11, 7))
            fig_m2.patch.set_facecolor('#ffffff')
            parse_action_metrics(p_df_t2, ax_m2, pitch_m2, all_selected_layers, draw_mode=True, specific_type="crosses")
            ax_m2.text(60, 40, str(sel_player_t2), fontsize=28, color='#0f172a', alpha=0.07, fontweight='bold', ha='center', va='center', zorder=2)
            st.pyplot(fig_m2)
            
            st.markdown("---")
            st.markdown("<h3 style='color: #a47e3c;'>🛡️ Map 4: Complete Defensive & Combat Matrix</h3>", unsafe_allow_html=True)
            pitch_m3 = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
            fig_m3, ax_m3 = pitch_m3.draw(figsize=(11, 7))
            fig_m3.patch.set_facecolor('#ffffff')
            parse_action_metrics(p_df_t2, ax_m3, pitch_m3, all_selected_layers, draw_mode=True, specific_type="defense")
            ax_m3.legend(handles=get_full_legend()[8:], loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#0f172a', edgecolor='#334155')
            ax_m3.text(60, 40, str(sel_player_t2), fontsize=28, color='#0f172a', alpha=0.07, fontweight='bold', ha='center', va='center', zorder=2)
            st.pyplot(fig_m3)

        with tab3:
            sel_player_t3 = st.selectbox("🎯 Focus Player (Summary Stats):", options=player_list, format_func=lambda x: player_options[x], key="sb_t3")
            p_df_t3 = team_df[team_df['Player'] == sel_player_t3].copy()
            p_stats_t3 = parse_action_metrics(p_df_t3, None, None, all_selected_layers, draw_mode=False)
            render_premium_player_card(sel_player_t3, selected_team, p_stats_t3)
            render_player_summary_table(sel_player_t3, p_stats_t3, all_selected_layers)
    else:
        st.warning("⚠️ No players found in the uploaded file.")

    with tab4:
        st.markdown(f"<h3 style='text-align: center; color: #38bdf8;'>🔥 Team Global Heatmap: EPS</h3>", unsafe_allow_html=True)
        pitch_th = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_th, ax_th = pitch_th.draw(figsize=(12, 9))
        fig_th.patch.set_facecolor('#ffffff')
        if len(team_df) > 1:
            draw_premium_kde_heatmap(team_df, ax_th)
        st.pyplot(fig_th)

    with tab5:
        st.markdown(f"<h3 style='text-align: center; color: #38bdf8;'>🌍 Map 1: Team Full Tactical Performance Map (Attack & Defense)</h3>", unsafe_allow_html=True)
        pitch_all = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_all, ax_all = pitch_all.draw(figsize=(12, 9))
        fig_all.patch.set_facecolor('#ffffff')
        parse_action_metrics(team_df, ax_all, pitch_all, all_selected_layers, draw_mode=True, specific_type="all")
        ax_all.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#0f172a', edgecolor='#334155')
        st.pyplot(fig_all)
        
        st.markdown("---")
        st.markdown(f"<h3 style='text-align: center; color: #a47e3c;'>🛡️ Map 2: Team Defensive & Combat Matrix</h3>", unsafe_allow_html=True)
        pitch_td = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#475569', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_td, ax_td = pitch_td.draw(figsize=(12, 9))
        fig_td.patch.set_facecolor('#ffffff')
        parse_action_metrics(team_df, ax_td, pitch_td, all_selected_layers, draw_mode=True, specific_type="defense")
        ax_td.legend(handles=get_full_legend()[8:], loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#0f172a', edgecolor='#334155')
        st.pyplot(fig_td)
else:
    st.info("👋 Please upload a match CSV file on the left sidebar to generate the dynamic dashboard.")
