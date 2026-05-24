import streamlit as st
import pandas as pd
import numpy as np
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import seaborn as sns
import io

# 1. إعدادات الصفحة العامة للتطبيق
st.set_page_config(
    page_title="TootScouting - Performance Analysis", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. تصميم الواجهة بهوية المنصة (CSS مخصص)
st.markdown("""
    <style>
    .main-title {
        font-size: 40px;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 20px;
    }
    .sidebar-title {
        font-size: 22px;
        font-weight: bold;
        color: #1F2937;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- تعريف الصفحات ---

# أ. صفحة خريطة التسديدات (Shot Map)
def show_shot_map_page():
    st.title("⚽ مركز تحليل التسديدات - Shot Map")
    st.markdown("تحليل جودة الكرات، زوايا التسديد، وقيم الأهداف المتوقعة (xG).")
    
    # ثيم الألوان لخرائط التسديدات
    BG_COLOR = '#111827'       # خلفية الملعب الداكنة
    LINE_COLOR = '#4B5563'     # لون خطوط الملعب
    GOAL_COLOR = '#10B981'     # أخضر للأهداف
    MISSED_COLOR = '#EF4444'   # أحمر للتسديدات الضائعة
    SAVED_COLOR = '#3B82F6'    # أزرق للتصديات

    # بيانات تجريبية (مبنية على نظام إحداثيات Opta/WhoScored من 0 لـ 100)
    mock_shots = {
        'player': ['Salah', 'Salah', 'Nunez', 'Diaz', 'Szoboszlai', 'Salah', 'Nunez'],
        'x': [88.5, 94.2, 78.0, 85.1, 72.5, 89.1, 91.0],  
        'y': [50.0, 48.5, 62.0, 35.0, 55.0, 41.2, 58.0],  
        'xG': [0.58, 0.76, 0.12, 0.25, 0.06, 0.32, 0.45],
        'outcome': ['Goal', 'Goal', 'Missed', 'Saved', 'Blocked', 'Saved', 'Missed']
    }
    df_shots = pd.DataFrame(mock_shots)

    # فلاتر التحكم الجانبية الخاصة بالصفحة
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 فلاتر خريطة التسديدات")
    selected_players = st.sidebar.multiselect(
        "اختر اللاعبين للتحليل:", 
        options=df_shots['player'].unique(), 
        default=df_shots['player'].unique()
    )
    
    filtered_df = df_shots[df_shots['player'].isin(selected_players)].copy()

    # تحديد الألوان بناءً على نتيجة التسديدة
    def assign_colors(outcome):
        if outcome == 'Goal': return GOAL_COLOR
        elif outcome == 'Saved': return SAVED_COLOR
        elif outcome == 'Missed': return MISSED_COLOR
        else: return '#9CA3AF' # رمادي للمحجوبة

    filtered_df['color'] = filtered_df['outcome'].apply(assign_colors)

    # رسم الملعب التكتيكي (نصف ملعب هجومي عمودي احترافي)
    pitch = Pitch(pitch_type='opta', pitch_color=BG_COLOR, line_color=LINE_COLOR, half=True, orientation='vertical')
    fig, ax = pitch.draw(figsize=(7, 9))
    fig.patch.set_facecolor(BG_COLOR)

    if not filtered_df.empty:
        # رسم نقاط التسديدات (حجم الدائرة يتأثر بالـ xG)
        pitch.scatter(
            filtered_df['x'], 
            filtered_df['y'],
            s=filtered_df['xG'] * 1000, 
            c=filtered_df['color'],
            alpha=0.85,
            edgecolors='#FFFFFF',
            linewidth=1.2,
            ax=ax
        )
        
        # إضافة الملصقات النصية الذكية فوق النقاط
        for idx, row in filtered_df.iterrows():
            pitch.annotate(
                f"{row['player']} ({row['xG']:.2f})", 
                xy=(row['x'], row['y']), 
                xytext=(0, 10), 
                textcoords='offset points',
                color='white', 
                fontsize=8, 
                va='center', 
                ha='center',
                ax=ax,
                bbox=dict(boxstyle='round,pad=0.2', fc=BG_COLOR, alpha=0.6, ec='none')
            )

    # عرض العناصر في الصفحة عبر أعمدة متناسقة
    col1, col2 = st.columns([5, 3])
    
    with col1:
        st.pyplot(fig, use_container_width=True)
        
        # زر تحميل الخريطة كصورة PNG للكشافين والمحللين
        fn = io.BytesIO()
        fig.savefig(fn, format="png", dpi=300, bbox_inches='tight')
        st.download_button(
            label="📥 تحميل خريطة التسديدات بجودة عالية", 
            data=fn, 
            file_name="tootscouting_shot_map.png", 
            mime="image/png"
        )
        
    with col2:
        st.subheader("💡 دليل قراءة الخريطة")
        st.markdown(f"""
        - **حجم الدائرة:** يعبر عن جودة الفرصة وقيم الأهداف المتوقعة (**xG**). كلما كبرت الدائرة، كلما كانت الهجمة أخطر وأقرب للمرمى.
        - **دلالات الألوان:**
            - <span style='color:{GOAL_COLOR}; font-weight:bold;'>■</span> هدف (Goal)
            - <span style='color:{SAVED_COLOR}; font-weight:bold;'>■</span> تصدي للحارس (Saved)
            - <span style='color:{MISSED_COLOR}; font-weight:bold;'>■</span> خارج المرمى (Missed)
            - <span style='color:#9CA3AF; font-weight:bold;'>■</span> تسديدة محجوبة (Blocked)
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("📋 جدول البيانات التحليلي")
        st.dataframe(filtered_df[['player', 'xG', 'outcome']], hide_index=True, use_container_width=True)


# ب. صفحة خريطة الحرارة (Heatmap)
def show_heatmap_page():
    st.title("🔥 مركز خرائط الحرارة - Heatmap")
    st.markdown("تتبع تحركات اللاعبين ومناطق نفوذهم داخل المستطيل الأخضر.")
    
    # بيانات وهمية لإحداثيات التحرك
    np.random.seed(42)
    mock_movements = {
        'x': np.random.uniform(50, 100, 100),
        'y': np.random.uniform(10, 90, 100)
    }
    df_heat = pd.DataFrame(mock_movements)
    
    pitch = Pitch(pitch_type='opta', pitch_color='#ffffff', line_color='#cccccc')
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # رسم خريطة الحرارة باستخدام Seaborn KDE
    sns.kdeplot(
        x=df_heat['x'], 
        y=df_heat['y'], 
        cmap='hot', 
        shade=True, 
        thresh=0.05, 
        n_levels=50, 
        ax=ax, 
        alpha=0.6
    )
    st.pyplot(fig)
    st.info("ملاحظة: يمكنك ربط هذه الخريطة بملفات تتبع اللاعبين (Tracking Data) الخاصة بـ TootScouting.")


# ج. صفحة الترحيب الرئيسية
def show_home_page():
    st.markdown('<div class="main-title">TootScouting Platform 📊</div>', unsafe_allow_html=True)
    st.markdown("""
    ### أهلاً بك في منصة التحليل الرياضي الخاصة بك!
    هذه المنصة مصممة خصيصاً لمساعدة محللي الأداء ومكتشفي المواهب على تحويل الأرقام الجافة إلى تقارير بصرية تكتيكية مبهرة.
    
    **من القائمة الجانبية يمكنك الانتقال بين:**
    * **خرائط الحرارة (Heatmaps):** لمعرفة مناطق انتشار اللاعبين.
    * **خرائط التسديدات (Shot Maps):** لتحليل الفعالية الهجومية والـ xG بنفس أسلوب المنصات العالمية مثل Insight90.
    """)


# 3. محرك التنقل الرئيسي (Sidebar Navigation)
st.sidebar.markdown('<div class="sidebar-title">TootScouting لوحة التحكم</div>', unsafe_allow_html=True)
menu_option = st.sidebar.radio(
    "اختر أداة التحليل:",
    ["🏠 الصفحة الرئيسية", "🔥 خريطة الحرارة (Heatmap)", "🎯 خريطة التسديدات (Shot Map)"]
)

# تشغيل الصفحة بناءً على اختيار المستخدم
if menu_option == "🏠 الصفحة الرئيسية":
    show_home_page()
elif menu_option == "🔥 خريطة الحرارة (Heatmap)":
    show_heatmap_page()
elif menu_option == "🎯 خريطة التسديدات (Shot Map)":
    show_shot_map_page()
