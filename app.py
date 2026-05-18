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

# دالة ذكية ومضمونة لقراءة مسار اللوجو وتحويله لـ Base64 للكارت فقط
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
        background-color: #ffffff !important; 
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 15px rgba(164, 126, 60, 0.4);
        overflow: hidden;
    }
    .premium-player-logo-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 6px;
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

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- Sidebar Controls ---
st.sidebar.markdown("## 🛠️ Tactical Control Unit")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8-sig')
    except Exception as e:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='cp1252')

    df.columns = df.columns.str.strip()
    
    # 🎯 ميكانيزم المابينج الدقيق والذكي (Precise Selective Mapping) لمنع تكرار وتداخل الأعمدة تماماً
    rename_dict = {}
    
    # 1. تحديد عمود الإجراء الأساسي Action
    for col in df.columns:
        c_low = col.lower().strip()
        if 'action' in c_low or 'event type' in c_low or 'event_type' in c_low or c_low == 'event' or c_low == 'إجراء' or c_low == 'حدث':
            rename_dict[col] = 'Action'
            break

    # 2. تحديد عمود الفريق الكلي Team
    for col in df.columns:
        c_low = col.lower().strip()
        if 'team' in c_low or 'teams' in c_low or c_low == 'side' or c_low == 'squad' or c_low == 'club' or c_low == 'فريق':
            rename_dict[col] = 'Team'
            break

    # 3. تحديد عمود اللاعبين الفردي Player من غير تداخل مع عمود Name
    for col in df.columns:
        c_low = col.lower().strip()
        if 'player' in c_low or 'players' in c_low or c_low == 'لاعب':
            rename_dict[col] = 'Player'
            break
    if 'Player' not in rename_dict.values():
        for col in df.columns:
            c_low = col.lower().strip()
            if 'name' in c_low and col not in rename_dict:
                rename_dict[col] = 'Player'
                break

    # 4. تحديد عمود الـ Tags المساعد
    for col in df.columns:
        c_low = col.lower().strip()
        if 'tag' in c_low or 'tags' in c_low or 'وصف' in c_low:
            rename_dict[col] = 'Tags'
            break
            
    if rename_dict:
        df = df.rename(columns=rename_dict)

    required_cols = ['Action', 'Team']
    missing_cols = [c for c in required_cols if c not in df.columns]
    
    if missing_cols:
        st.error(f"⚠️ الملف المرفوع لا يحتوي على الأعمدة الأساسية المطلوبة: {missing_cols}")
        st.markdown("### 🔍 الأعمدة المتوفرة حالياً داخل ملفك هي:")
        st.write(list(df.columns))
    else:
        df['Team'] = df['Team'].fillna('Unknown Team')
        df = df.dropna(subset=['Action'])
        
        if 'Tags' not in df.columns:
            df['Tags'] = ''
        else:
            df['Tags'] = df['Tags'].fillna('')
            
        if 'Player' in df.columns:
            df['Player'] = df['Player'].fillna('Unknown Player').astype(str).str.strip()

        # معالجة الإحداثيات والضرب التلقائي في أبعاد الملعب المعتمدة دولياً (120x80)
        col_map_lower = {c.lower().strip(): c for c in df.columns}
        
        x_start_col = col_map_lower.get('x start') or col_map_lower.get('x')
        y_start_col = col_map_lower.get('y start') or col_map_lower.get('y')
        x_end_col = col_map_lower.get('x end')
        y_end_col = col_map_lower.get('y end')

        if x_start_col and y_start_col:
            df['x_scaled'] = df[x_start_col] if df[x_start_col].max() > 1 else df[x_start_col] * 120
            df['y_scaled'] = df[y_start_col] if df[y_start_col].max() > 1 else df[y_start_col] * 80
            
            if x_end_col and y_end_col:
                df['x_end_scaled'] = df[x_end_col] if df[x_end_col].max() > 1 else df[x_end_col] * 120
                df['y_end_scaled'] = df[y_end_col] if df[y_end_col].max() > 1 else df[y_end_col] * 80 
            else:
                df['x_end_scaled'] = df['x_scaled']
                df['y_end_scaled'] = df['y_scaled']

        team_list = sorted([t for t in df['Team'].unique().tolist() if pd.notna(t) and str(t).strip() != ''])
        if not team_list:
            team_list = ['Default Team']
            df['Team'] = 'Default Team'
            
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

        def parse_action_metrics(dataframe, ax, pitch_obj, layers, draw_mode=True, specific_type=None):
            matrix = {
                "total_passes": 0, "success_passes": 0, "crosses": 0, "success_crosses": 0,
                "through_balls": 0, "tackles": 0, "clearances": 0, "ground_duels_won": 0,
                "aerial_duels_won": 0, "fouls": 0, "counterpress": 0, "goals": 0
            }
            
            for i, row in dataframe.iterrows():
                if 'x_scaled' not in dataframe.columns or 'y_scaled' not in dataframe.columns:
                    continue
                act = str(row['Action']).lower()
                tag = str(row['Tags']).lower()
                
                is_success = 'success' in tag or 'ناجح' in tag or 'won' in tag or 'win' in tag or 'pass' in tag or 'outcome: pass' in tag
                if 'failed' in tag or 'failure' in tag: is_success = False
                action_captured = False
                
                if 'goal' in act or 'goal' in tag or 'هدف' in act or 'هدف' in tag:
                    matrix["goals"] += 1
                    if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "all") and "Goals" in layers:
                        pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=650, color='gold', edgecolors='black', ax=ax, zorder=6)

                if 'pass' in act or 'تمرير' in act:
                    if 'through' in tag and "Through Balls" in layers:
                        if draw_mode and (specific_type is None or specific_type == "passes" or specific_type == "all"):
                            pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax, zorder=4)
                        matrix["through_balls"] += 1
                        action_captured = True
                    elif "Normal Passes" in layers and not any(k in tag for k in ['cross', 'through', 'corner', 'free kick']):
                        if draw_mode and (specific_type is None or specific_type == "passes" or specific_type == "all"):
                            pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.5, zorder=3)
                        action_captured = True
                    elif 'corner' in tag and "Corners" in layers:
                        if draw_mode and (specific_type is None or specific_type == "crosses" or specific_type == "all"):
                            pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange' if is_success else 'red', ax=ax, zorder=4)
                        action_captured = True
                    elif 'cross' in tag and "Crosses" in layers:
                        if draw_mode and (specific_type is None or specific_type == "crosses" or specific_type == "all"):
                            pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else '#e74c3c', linestyle='solid' if is_success else 'dashed', ax=ax, zorder=4)
                        matrix["crosses"] += 1
                        if is_success: matrix["success_crosses"] += 1
                        action_captured = True
                    
                    if action_captured:
                        matrix["total_passes"] += 1
                        if is_success: matrix["success_passes"] += 1

                elif any(w in act for w in ['tackle', 'inter', 'تدخل', 'قطع', 'تكل', 'تاكلز']):
                    if "Tackles" in layers:
                        if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "all"):
                            pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=240, color='blue', linewidth=3, ax=ax, zorder=5)
                    matrix["tackles"] += 1

                elif any(w in act for w in ['clear', 'clearance', 'تشتيت', 'ابعاد']):
                    if "Clearances" in layers:
                        if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "all"):
                            pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='d', s=200, color='purple', ax=ax, zorder=5)
                    matrix["clearances"] += 1

                elif any(w in act for w in ['aerial', 'هوائي', 'طير', 'رأس']):
                    if "Aerial Duels" in layers:
                        if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "all"):
                            pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='^', s=220, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax, zorder=5)
                    if is_success: matrix["aerial_duels_won"] += 1

                elif any(w in act for w in ['duel', 'التحام', 'صراع', 'أرضي', 'ground']) and 'aerial' not in act:
                    if "Ground Duels" in layers:
                        if draw_mode and (specific_type is None or specific_type == "defense" or specific_type == "
