import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
        # 3. محرك التصنيف التكتيكي المطور والموسع
        # -------------------------------------------------------------
        conditions = [
            # --- الهجوم الفارق ---
            valid_df['Action_raw'].str.contains('Goal|هدف', case=False) | valid_df['Tags'].str.contains('goal', case=False),
            valid_df['Action_raw'].str.contains('Shot|تسديد|شوط', case=False),
            valid_df['Action_raw'].str.contains('Corner|كورنر|ركنية', case=False) | valid_df['Tags'].str.contains('corner', case=False),
            valid_df['Action_raw'].str.contains('Cross|عرضية', case=False) | valid_df['Tags'].str.contains('cross', case=False),
            valid_df['Action_raw'].str.contains('Dribble|مرواغة|مراوغة|دريبليج', case=False) | valid_df['Tags'].str.contains('dribble', case=False),
            valid_df['Action_raw'].str.contains('Through|Key|ثرو', case=False) | valid_df['Tags'].str.contains('through|key|Behind', case=False),
            
            # --- الدفاع والتلاحم ---
            valid_df['Action_raw'].str.contains('Tackle|تدخل|افتكاك', case=False) | valid_df['Tags'].str.contains('tackle', case=False),
            valid_df['Action_raw'].str.contains('Clearance|تشتيت', case=False) | valid_df['Tags'].str.contains('clearance', case=False),
            valid_df['Action_raw'].str.contains('Air|هوائي|هواء', case=False) | valid_df['Tags'].str.contains('aerial|air', case=False),
            valid_df['Action_raw'].str.contains('Ground|أرضي|ارضي', case=False) | valid_df['Tags'].str.contains('ground', case=False),
            valid_df['Action_raw'].str.contains('Foul|فاول|خطأ|خطا', case=False) | valid_df['Tags'].str.contains('foul', case=False),
            valid_df['Action_raw'].str.contains('Counter|ضغط عكسي|عكسي', case=False) | valid_df['Tags'].str.contains('counterpress|press', case=False),
            
            # --- التمريرات العامة ---
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
        # 4. بناء القوائم المنفصلة (هجومية ودفاعية) في الـ Sidebar
        # -------------------------------------------------------------
        st.sidebar.markdown("---")
        players_list = ["كل اللاعبين"] + list(valid_df['Player'].dropna().unique())
        selected_player = st.sidebar.selectbox("👤 فلترة بحسب اللاعب:", players_list)
            
        temp_df = valid_df.copy()
        if selected_player != "كل اللاعبين":
            temp_df = temp_df[temp_df['Player'] == selected_player]

        # المجموعات التكتيكية المحددة من قبلك
        attack_categories = ["⚽ هدف (Goal)", "👟 تسديدة (Shot)", "🚩 كورنر (Corner)", "📐 عرضية (Cross)", "✨ مراوغة (Dribble)", "⚡ ثرو باص (Through Ball)", "🚀 تمريرة تقديمية (Progressive Pass)", "🔄 تمريرة عادية (Normal Pass)"]
        defense_categories = ["🛡️ تدخل (Tackle)", "💥 تشتيت (Clearance)", "🪂 صراع هوائي (Aerial Duel)", "🪵 صراع أرضي (Ground Duel)", "⚠️ فاول (Foul)", "⏱️ ضغط عكسي (Counterpress)"]

        # فرز الخيارات المتاحة فعلياً في الداتا لمنع ظهور خيارات فارغة
        available_attack = [act for act in attack_categories if act in temp_df['Clean_Action'].unique()]
        available_defense = [act for act in defense_categories if act in temp_df['Clean_Action'].unique()]

        st.sidebar.markdown("### 🏹 الفلاتر الهجومية")
        selected_attack = st.sidebar.multiselect("اختر الأكشنز الهجومية:", options=available_attack, default=available_attack)

        st.sidebar.markdown("### 🧱 الفلاتر الدفاعية")
        selected_defense = st.sidebar.multiselect("اختر الأكشنز الدفاعية:", options=available_defense, default=available_defense)

        # دمج الاختيارات من القائمتين لتطبيق الفلترة النهائية
        final_selected_actions = selected_attack + selected_defense

        # تطبيق الفلترة
        if final_selected_actions:
            filtered_df = temp_df[temp_df['Clean_Action'].isin(final_selected_actions)]
        else:
            filtered_df = pd.DataFrame(columns=temp_df.columns)

        # -------------------------------------------------------------
        # 5. إعادة رسم الملعب وإسقاط التكتيك
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        if not filtered_df.empty:
            # الأحداث التي ترسم كحركة (أسهم)
            movement_labels = ["🔄 تمريرة عادية (Normal Pass)", "🚀 تمريرة تقديمية (Progressive Pass)", "⚡ ثرو باص (Through Ball)", "📐 عرضية (Cross)", "🚩 كورنر (Corner)"]
            
            arrows_df = filtered_df[filtered_df['Clean_Action'].isin(movement_labels)]
            dots_df = filtered_df[~filtered_df['Clean_Action'].isin(movement_labels)]
            
            # رسم التحركات (الأسهم)
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
            
            # رسم الأحداث الثابتة والدفاعية برموز تكتيكية مخصصة
            if not dots_df.empty:
                for idx, row in dots_df.iterrows():
                    act_name = row['Clean_Action']
                    if "Goal" in act_name: m_color, m_style, m_size = '#00ff00', '*', 260         # نجمة خضراء للهدف
                    elif "Shot" in act_name: m_color, m_style, m_size = '#ff3366', 'o', 130         # نقطة حمراء للتسديدة
                    elif "Dribble" in act_name: m_color, m_style, m_size = '#ffff00', 'P', 120      # علامة + صفراء للمراوغة
                    elif "Tackle" in act_name: m_color, m_style, m_size = '#ff00ff', 'X', 130       # علامة X وردي للتدخل
                    elif "Clearance" in act_name: m_color, m_style, m_size = '#ffffff', 's', 110    # مربع أبيض للتشتيت
                    elif "Aerial" in act_name: m_color, m_style, m_size = '#3399ff', '^', 130       # مثلث أزرق للصراع الهوائي
                    elif "Ground" in act_name: m_color, m_style, m_size = '#brown', 'v', 120        # مثلث مقلوب للصراع الأرضي
                    elif "Foul" in act_name: m_color, m_style, m_size = '#ffcc00', 'd', 110         # معين برتقالي للفاول
                    else: m_color, m_style, m_size = '#00ffcc', 'h', 120                            # شكل سداسي فسفوري للضغط العكسي
                        
                    pitch.scatter(row['x_scaled'], row['y_scaled'], color=m_color, s=m_size, marker=m_style, edgecolors='#1a1a1a', zorder=4, ax=ax)
            
            # تحديث عرض الملعب بالداتا المطلوبة
            plot_placeholder.pyplot(fig)
            st.success(f"📋 تم تصفية وعرض {len(filtered_df)} حدث (هجومي/دفاعي) للاعب المحدد.")
        else:
            plot_placeholder.pyplot(fig)
            st.warning("الملعب معروض بالأعلى، لكن يرجى اختيار أكشن واحد على الأقل من القوائم الجانبية لتبدأ البيانات في الظهور.")
        plt.close(fig)
    else:
        st.error("عذراً، لم نتمكن من العثور على أعمدة الإحداثيات المطلوبة (X Start, Y Start).")
else:
    st.info("💡 الملعب جاهز؛ يرجى رفع ملف الإكسيل أو CSV من القائمة الجانبية لبدء الفلترة الهجومية والدفاعية المستقلة.")
