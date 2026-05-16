import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
from PIL import Image

# 1. Page Config & Strict Dark Premium Theme (Matching the Tactical Card)
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

    /* Player Performance Summary Table Theme */
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
    </style>
""", unsafe_allow_html=True)

def add_logo(ax):
    try:
        img = Image.open('image_deac96.png')
        ax.imshow(img, extent=[48, 72, 28, 52], alpha=0.12, zorder=0)
    except:
        pass

st.title("🔬 TootScouting | Tactical Analysis Pro Lab")

# --- Sidebar Controls ---
st.sidebar.markdown("## 🛠️ Tactical Control Unit")
uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # Scale Coordinates to StatsBomb Dimensions (120x80)
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    df = df.dropna(subset=['Action', 'Team'])
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("📋 Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    # Dropdown Filter Configuration Units
    with st.sidebar.expander("🎯 Passing Filters", expanded=True):
        selected_passes = st.multiselect("Pass Types:", ["Normal Passes", "Crosses", "Through Balls", "Corners", "Free Kicks"], default=["Normal Passes", "Crosses"])
        
    with st.sidebar.expander("🛡️ Defensive & Attack Filters", expanded=True):
        selected_defense = st.multiselect("Actions:", ["Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Counterpress", "Goals"], default=["Tackles", "Ground Duels", "Goals"])

    all_selected_layers = selected_passes + selected_defense

    # --- Static Visual Map Legend ---
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

    # --- Pitch Graphics Drawing Engine ---
    def process_and_draw_tactics(dataframe, ax, pitch_obj, layers, draw=True):
        counts = {
            "total_passes": 0, "success_passes": 0,
            "crosses": 0, "success_crosses": 0,
            "through_balls": 0, "tackles": 0,
            "clearances": 0, "ground_duels_won": 0,
            "aerial_duels_won": 0, "goals": 0
        }
        
        for i, row in dataframe.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'ناجح' in tag
            drawn_action = False
            
            # Passing Matrix Processing
            if 'pass' in act or 'تمرير' in act:
                if 'cross' in tag and "Crosses" in layers:
                    if draw: pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                    counts["crosses"] += 1
                    if is_success: counts["success_crosses"] += 1
                    drawn_action = True
                elif 'through' in tag and "Through Balls" in layers:
                    if draw: pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax)
                    counts["through_balls"] += 1
                    drawn_action = True
                elif 'corner' in tag and "Corners" in layers:
                    if draw: pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange' if is_success else 'red', ax=ax)
                    drawn_action = True
                elif "Normal Passes" in layers and not any(k in tag for k in ['cross', 'through', 'corner', 'free kick']):
                    if draw: pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.5)
                    drawn_action = True
                
                if drawn_action:
                    counts["total_passes"] += 1
                    if is_success: counts["success_passes"] += 1

            # Defensive Matrix Processing
            elif any(word in act for word in ['tackle', 'inter', 'تدخل', 'قطع', 'clear', 'تشتيت', 'duel', 'التحام']):
                if any(w in act for w in ['tackle', 'inter', 'تدخل', 'قطع']) and "Tackles" in layers:
                    if draw: pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=220, color='blue', linewidth=2.5, ax=ax)
                    counts["tackles"] += 1
                elif 'clear' in act and "Clearances" in layers:
                    if draw: pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='d', s=180, color='purple', ax=ax)
                    counts["clearances"] += 1
                elif 'aerial' in act and "Aerial Duels" in layers:
                    if draw: pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='^', s=200, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax)
                    if is_success: counts["aerial_duels_won"] += 1
                elif 'duel' in act and 'aerial' not in act and "Ground Duels" in layers:
                    if draw: pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='s', s=180, color='#2ecc71' if is_success else 'red', ax=ax)
                    if is_success: counts["ground_duels_won"] += 1
            
            # Goal Operations
            if ('goal' in tag or 'هدف' in tag) and "Goals" in layers:
                if draw: pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax, zorder=5)
                counts["goals"] += 1
                
        return counts

    # --- Player Performance Summary Component ---
    def render_player_summary_table(player_name, stats):
        pass_acc = f"{(stats['success_passes']/stats['total_passes'])*100:.1f}%" if stats['total_passes'] > 0 else "0%"
        cross_acc = f"{(stats['success_crosses']/stats['crosses'])*100:.1f}%" if stats['crosses'] > 0 else "0%"
        
        st.markdown(f"""
            <div class="summary-table-container">
                <div class="summary-title">📊 Player Summary Profile: {player_name}</div>
                <table class="player-summary-table">
                    <thead>
                        <tr>
                            <th>Metric Category</th>
                            <th>Total Attempts</th>
                            <th>Successful / Accuracy</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><b>Total Passing</b></td>
                            <td>{stats['total_passes']}</td>
                            <td><span class="stat-badge">{stats['success_passes']} ({pass_acc})</span></td>
                        </tr>
                        <tr>
                            <td><b>Crosses</b></td>
                            <td>{stats['crosses']}</td>
                            <td><span class="stat-badge">{stats['success_crosses']} ({cross_acc})</span></td>
                        </tr>
                        <tr>
                            <td><b>Through Balls</b></td>
                            <td>{stats['through_balls']}</td>
                            <td><span class="stat-badge">{stats['through_balls']}</span></td>
                        </tr>
                        <tr>
                            <td><b>Defensive Tackles</b></td>
                            <td>{stats['tackles']}</td>
                            <td><span class="stat-badge">{stats['tackles']}</span></td>
                        </tr>
                        <tr>
                            <td><b>Clearances</b></td>
                            <td>{stats['clearances']}</td>
                            <td><span class="stat-badge">{stats['clearances']}</span></td>
                        </tr>
                        <tr>
                            <td><b>Ground Duels Won</b></td>
                            <td>-</td>
                            <td><span class="stat-badge">{stats['ground_duels_won']} Won</span></td>
                        </tr>
                        <tr>
                            <td><b>Aerial Duels Won</b></td>
                            <td>-</td>
                            <td><span class="stat-badge">{stats['aerial_duels_won']} Won</span></td>
                        </tr>
                        <tr>
                            <td style="color: #gold; font-weight: bold;">⚽ Goals Scored</td>
                            <td>-</td>
                            <td><span class="stat-badge" style="background-color: #fef08a; color: #854d0e;">{stats['goals']} GOAL</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)

    # --- System Application Tabs ---
    tab1, tab2 = st.tabs(["👤 Individual Player Lab", "👥 Team Strategy Lab"])

    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("🎯 Focus Player:", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        # Calculate calculations for dynamic framework feed
        p_stats = process_and_draw_tactics(p_df, None, None, all_selected_layers, draw=False)
        render_player_summary_table(sel_player, p_stats)
        
        # Base pitch drawing configuration
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#1e293b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig, ax = pitch.draw(figsize=(12, 8.5))
        add_logo(ax)
        
        process_and_draw_tactics(p_df, ax, pitch, all_selected_layers, draw=True)
        ax.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#ffffff')
        st.pyplot(fig)

    with tab2:
        st.subheader(f"Tactical Distribution: {selected_team}")
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#1e293b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_t, ax_t = pitch_t.draw(figsize=(12.5, 9))
        add_logo(ax_t)
        
        process_and_draw_tactics(team_df, ax_t, pitch_t, all_selected_layers, draw=True)
        ax_t.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#ffffff')
        st.pyplot(fig_t)

else:
    st.info("👋 Please upload a match CSV file on the left sidebar to generate the dynamic dashboard.")
