import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. رسم الملعب فوراً (خارج أي شرط لضمان ظهوره بمجرد فتح التطبيق)
st.subheader("🏟️ خريطة الفاعلية الشاملة")

fig, ax = plt.subplots(figsize=(12, 8))
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
pitch.draw(ax=ax)
fig.patch.set_facecolor('#1a1a1a')

# إنشاء مساحة عرض ثابتة للملعب في Streamlit
plot_placeholder = st.empty()
plot_placeholder.pyplot(fig)
plt.close(fig)

# 2. رفع ملف البيانات (CSV أو Excel)
st.sidebar.header("📁 تحميل البيانات")
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

        # محرك التصنيف التكتيكي
        conditions = [
            valid_df['Action_raw'].str.contains('Goal|هدف', case=False) | valid_df['Tags'].str.contains('goal', case=False),
            valid_df['Action_raw'].str.contains('Shot|تسديد|شوط', case=False),
            valid_df['Action_raw'].str.contains('Corner|كورنر|ركنية', case=False) | valid_df['Tags'].str.contains('corner', case=False),
            valid_df['Action_raw'].str.contains('Cross|عرضية', case=False) | valid_df['Tags'].str.contains('cross', case=False),
            valid_df['Action_raw'].str.contains('Through|Key|ثرو', case=False) | valid_df['Tags'].str.contains('through|key|Behind', case=False),
            valid_df['Action_raw'].str.contains('Tackle|افتكاك|تاكل', case=False) | valid_df['Tags'].str.contains('tackle', case=False),
            valid_df['Action_raw'].str.contains('Intercept|قطع|اعتراض', case=False) | valid_df['Tags'].str.contains('intercept', case=False),
            valid_df['Action_raw'].str.contains('Clearance|تشتيت', case=False) | valid_df['Tags'].str.contains('clearance', case=False),
            valid_df['Action_raw'].str.contains('Duel|صراع|التحام', case=False) | valid_df['Tags'].str.contains('duel', case=False),
            (valid_df['Action_raw'].str.contains('Pass|تمرير', case=False) | valid_df['Action_raw'].str.isnumeric()) & (valid_df['prog_distance'] >= 12),
            valid_df['Action_raw'].str.contains('Pass|تمرير', case=False) | valid_df['Action_raw'].str.isnumeric()
        ]
        
        choices = [
            "🎯 هدف (Goal)", "👟 تسديدة (Shot)", "🚩 كورنر (Corner)", "📐 عرضية (Cross)", 
            "⚡ ثرو باص (Through Ball)", "🛡️ افتكاك كرة (Tackle)", "🛑 قطع كرة (Interception)", 
            "💥 تشتيت (Clearance)", "⚔️ الالتحامات (Duels)", "🚀 تمريرة تقديمية (Progressive Pass)", 
            "🔄 تمريرة عادية (Normal Pass)"
        ]
        
        valid_df['Clean_Action'] = np.select(conditions, choices, default="📋 أحداث أخرى (Other)")

        # الفلاتر (Multiselect)
        st.subheader("🎯 لوحة الفلاتر التكتيكية (هجوم ودفاع)")
        col1, col2 = st.columns(2)
        
        with col2:
            players_list = ["كل اللاعبين"] + list(valid_df['Player'].dropna().unique())
            selected_player = st.selectbox("فلترة بحسب اللاعب:", players_list)
            
        temp_df = valid_df.copy()
        if selected_player != "كل اللاعبين":
            temp_df = temp_df[temp_df['Player'] == selected_player]
            
        with col1:
            display_actions = list(temp_df['Clean_Action'].unique())
            display_actions.sort()
            selected_actions = st.multiselect("اختر الأكشنز المطلوبة:", options=display_actions, default=display_actions)

        # تطبيق الفلترة
        if selected_actions:
            filtered_df = temp_df[temp_df['Clean_Action'].isin(selected_actions)]
        else:
            filtered_df = pd.DataFrame(columns=temp_df.columns)

        # إعادة رسم الملعب وعمود البيانات فوقه وتحديث الـ Placeholder
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        if not filtered_df.empty:
            movement_labels = ["🔄 تمريرة عادية (Normal Pass)", "🚀 تمريرة تقديمية (Progressive Pass)", "⚡ ثرو باص (Through Ball)", "📐 عرضية (Cross)", "🚩 كورنر (Corner)"]
            arrows_df = filtered_df[filtered_df['Clean_Action'].isin(movement_labels)]
            dots_df = filtered_df[~filtered_df['Clean_Action'].isin(movement_labels)]
            
            # رسم الأسهم
            if not arrows_df.empty:
                for act in arrows_df['Clean_Action'].unique():
                    sub_arrow = arrows_df[arrows_df['Clean_Action'] == act]
                    if "Normal" in act: color = '#00ffcc'
                    elif "Progressive" in act: color = '#ff9900'
                    elif "Through" in act: color = '#cc00ff'
                    elif "Cross" in act: color = '#ffff00'
                    else: color = '#00f0ff'
                    
                    has_end = sub_arrow['x2_scaled'].notna() & (sub_arrow['x2_scaled'] != 0) & (sub_arrow['x2_scaled'] != sub_arrow['x_scaled'])
                    arrow_plots = sub_arrow[has_end]
                    dot_plots = sub_arrow[~has_end]
                    
                    if not arrow_plots.empty:
                        pitch.arrows(arrow_plots['x_scaled'], arrow_plots['y_scaled'], arrow_plots['x2_scaled'], arrow_plots['y2_scaled'], width=2, headwidth=3, headlength=3, color=color, alpha=0.8, ax=ax)
                        pitch.scatter(arrow_plots['x_scaled'], arrow_plots['y_scaled'], color=color, s=40, edgecolors='#ffffff', zorder=3, ax=ax)
                    if not dot_plots.empty:
                        pitch.scatter(dot_plots['x_scaled'], dot_plots['y_scaled'], color=color, s=60, edgecolors='#ffffff', zorder=3, ax=ax)
            
            # رسم النقاط والدفاع
            if not dots_df.empty:
                for idx, row in dots_df.iterrows():
                    act_name = row['Clean_Action']
                    if "Goal" in act_name: m_color, m_style, m_size = '#00ff00', '*', 250
                    elif "Shot" in act_name: m_color, m_style, m_size = '#ff3366', 'o', 120
                    elif "Tackle" in act_name: m_color, m_style, m_size = '#ff00ff', 'X', 130
                    elif "Interception" in act_name: m_color, m_style, m_size = '#3399ff', 'D', 110
                    elif "Clearance" in act_name: m_color, m_style, m_size = '#ffffff', 's', 100
                    else: m_color, m_style, m_size = '#ffff00', '^', 110
                        
                    pitch.scatter(row['x_scaled'], row['y_scaled'], color=m_color, s=m_size, marker=m_style, edgecolors='#1a1a1a', zorder=4, ax=ax)
            
            # تحديث الملعب بالداتا الجديدة
            plot_placeholder.pyplot(fig)
            st.success(f"تم عرض {len(filtered_df)} حدث تكتيكي بنجاح.")
        else:
            st.warning("تم تصفية البيانات ولم يتبقَ أحداث لعرضها بناءً على خياراتك الحالي.")
        plt.close(fig)
    else:
        st.error("عذراً، لم نتمكن من العثور على أعمدة الإحداثيات المطلوبة (X Start, Y Start). يرجى التأكد من أسماء الأعمدة بالملف.")
else:
    st.info("يرجى رفع ملف البيانات من القائمة الجانبية لبدء إسقاط الأحداث الهجومية والدفاعية.")
