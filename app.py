import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. رسم الملعب فوراً عند فتح التطبيق
st.subheader("🏟️ خريطة الفاعلية التكتيكية المتقدمة")

fig, ax = plt.subplots(figsize=(12, 8))
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
pitch.draw(ax=ax)
fig.patch.set_facecolor('#1a1a1a')

plot_placeholder = st.empty()
plot_placeholder.pyplot(fig)
plt.close(fig)

# 2. القائمة الجانبية لرفع الملف والفلاتر
st.sidebar.header("📁 تحميل البيانات والتحليل")
uploaded_file = st.sidebar.file_uploader("قم برفع ملف البيانات (Excel أو CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    st.sidebar.success("تم رفع الملف بنجاح!")
    
    # تنظيف أسماء الأعمدة
    df.columns = df.columns.str.strip()
    
    column_mapping = {
        'X Start': 'x1', 'Y Start': 'y1',
        'X End': 'x2', 'Y End': 'y2'
    }
    df = df.rename(columns=column_mapping)
    
    required_columns = ['x1', 'y1', 'x2', 'y2']
    if all(col in df.columns for col in required_columns):
        
        # العمليات الحسابية وتغيير الأبعاد (Scaling)
        df['x_scaled'] = df['x1'] * 120
        df['y_scaled'] = df['y1'] * 80
        df['x2_scaled'] = df['x2'] * 120
        df['y2_scaled'] = df['y2'] * 80
        
        valid_df = df[df['x_scaled'].notna() & df['y_scaled'].notna()].copy()
        valid_df['Action_raw'] = valid_df['Action'].astype(str).str.strip()
        valid_df['Tags'] = valid_df['Tags'].fillna('').astype(str)
        valid_df['Player'] = valid_df['Player'].astype(str).str.strip()
        
        valid_df['prog_distance'] = valid_df['x2_scaled'] - valid_df['x_scaled']

        # -------------------------------------------------------------
        # 3. محرك التصنيف التكتيكي
        # -------------------------------------------------------------
        conditions = [
            valid_df['Action_raw'].str.contains('Goal|هدف', case=False) | valid_df['Tags'].str.contains('goal', case=False),
            valid_df['Action_raw'].str.contains('Shot|تسديد|شوط', case=False),
            valid_df['Action_raw'].str.contains('Corner|كورنر|ركنية', case=False) | valid_df['Tags'].str.contains('corner', case=False),
            valid_df['Action_raw'].str.contains('Cross|عرضية', case=False) | valid_df['Tags'].str.contains('cross', case=False),
            valid_df['Action_raw'].str.contains('Dribble|مرواغة|مراوغة|دريبليج', case=False) | valid_df['Tags'].str.contains('dribble', case=False),
            valid_df['Action_raw'].str.contains('Through|Key|ثرو', case=False) | valid_df['Tags'].str.contains('through|key|Behind', case=False),
            
            valid_df['Action_raw'].str.contains('Tackle|تدخل|افتكاك', case=False) | valid_df['Tags'].str.contains('tackle', case=False),
            valid_df['Action_raw'].str.contains('Clearance|تشتيت', case=False) | valid_df['Tags'].str.contains('clearance', case=False),
            valid_df['Action_raw'].str.contains('Air|هوائي|هواء', case=False) | valid_df['Tags'].str.contains('aerial|air', case=False),
            valid_df['Action_raw'].str.contains('Ground|أرضي|ارضي', case=False) | valid_df['Tags'].str.contains('ground', case=False),
            valid_df['Action_raw'].str.contains('Foul|فاول|خطأ|خطا', case=False) | valid_df['Tags'].str.contains('foul', case=False),
            valid_df['Action_raw'].str.contains('Counter|ضغط عكسي|عكسي', case=False) | valid_df['Tags'].str.contains('counterpress|press', case=False),
            
            (valid_df['Action_raw'].str.contains('Pass|تمرير', case=False) | valid_df['Action_raw'].str.isnumeric()) & (valid_df['prog_distance'] >= 12),
            valid_df['Action_raw'].str.contains('Pass|تمرير', case=False) | valid_df['Action_raw'].str.isnumeric()
        ]
        
        choices = [
            "⚽ هدف (Goal)", "👟 تسديدة (Shot)", "🚩 كورنر (Corner)", "📐 عرضية (Cross)", 
            "✨ مراوغة (Dribble)", "⚡ ثرو باص (Through Ball)", "🛡️ تدخل (Tackle)", "💥 تشتيت (Clearance)", 
            "🪂 صراع هوائي (Aerial Duel)", "🪵 صراع أرضي (Ground Duel)", "⚠️ فاول (Foul)", "⏱️ ضغط عكسي (Counterpress)",
            "🚀 تمريرة تقديمية (Progressive Pass)", "🔄 تمريرة عادية (Normal Pass)"
        ]
        
        valid_df['Clean_Action'] = np.select(conditions, choices, default="📋 أحداث أخرى (Other)")

        # -------------------------------------------------------------
        # 4. بناء قوائم الفلترة في الـ Sidebar
        # -------------------------------------------------------------
        st.sidebar.markdown("---")
        players_list = ["كل اللاعبين"] + list(valid_df['Player'].dropna().unique())
        selected_player = st.sidebar.selectbox("👤 فلترة بحسب اللاعب:", players_list)
            
        temp_df = valid_df.copy()
        if selected_player != "كل اللاعبين":
            temp_df = temp_df[temp_df['Player'] == selected_player]

        attack_categories = ["⚽ هدف (Goal)", "👟 تسديدة (Shot)", "🚩 كورنر (Corner)", "📐 عرضية (Cross)", "✨ مراوغة (Dribble)", "⚡ ثرو باص (Through Ball)", "🚀 تمريرة تقديمية (Progressive Pass)", "🔄 تمريرة عادية (Normal Pass)"]
        defense_categories = ["🛡️ تدخل (Tackle)", "💥 تشتيت (Clearance)", "🪂 صراع هوائي (Aerial Duel)", "🪵 صراع أرضي (Ground Duel)", "⚠️ فاول (Foul)", "⏱️ ضغط عكسي (Counterpress)"]

        available_attack = [act for act in attack_categories if act in temp_df['Clean_Action'].unique()]
        available_defense = [act for act in defense_categories if act in temp_df['Clean_Action'].unique()]

        st.sidebar.markdown("### 🏹 الفلاتر الهجومية")
        selected_attack = st.sidebar.multiselect("اختر الأكشنز الهجومية:", options=available_attack, default=available_attack)

        st.sidebar.markdown("### 🧱 الفلاتر الدفاعية")
        selected_defense = st.sidebar.multiselect("اختر الأكشنز الدفاعية:", options=available_defense, default=available_defense)

        final_selected_actions = selected_attack + selected_defense

        if final_selected_actions:
            filtered
