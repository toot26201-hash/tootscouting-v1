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
        # 4. بناء القوائم الفلترة في الـ Sidebar
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
            filtered_df = temp_df[temp_df['Clean_Action'].isin(final_selected_actions)]
        else:
            filtered_df = pd.DataFrame(columns=temp_df.columns)

        # -------------------------------------------------------------
        # 5. إعادة رسم الملعب مع دليل الرموز واسم اللاعب الذهبي
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(12, 9))  # زيادة الطول قليلاً لاستيعاب الدليل بالأسفل
        pitch.draw(ax=ax)
        fig.patch.set_facecolor('#1a1a1a')
        
        # مصفوفة لتخزين عناصر الدليل (Legend Items) التي تم رسمها بالفعل
        legend_elements = []
        
        # كتابة اسم اللاعب باللون الذهبي الخفيف أعلى اليمين داخل الملعب
        player_display_name = selected_player if selected_player != "كل اللاعبين" else "جميع اللاعبين"
        ax.text(115, 5, player_display_name, color='#D4AF37', fontsize=18, 
                fontweight='bold', ha='right', va='top', alpha=0.75,
                bbox=dict(facecolor='#1a1a1a', alpha=0.4, edgecolor='none', pad=4))

        if not filtered_df.empty:
            movement_labels = ["🔄 تمريرة عادية (Normal Pass)", "🚀 تمريرة تقديمية (Progressive Pass)", "⚡ ثرو باص (Through Ball)", "📐 عرضية (Cross)", "🚩 كورنر (Corner)"]
            
            arrows_df = filtered_df[filtered_df['Clean_Action'].isin(movement_labels)]
            dots_df = filtered_df[~filtered_df['Clean_Action'].isin(movement_labels)]
            
            # رسم التحركات (الأسهم)
            if not arrows_df.empty:
                for act in arrows_df['Clean_Action'].unique():
                    sub_arrow = arrows_df[arrows_df['Clean_Action'] == act]
                    if "Normal" in act: color, name = '#00ffcc', "تمريرة عادية"
                    elif "Progressive" in act: color, name = '#ff9900', "تمريرة تقديمية"
                    elif "Through" in act: color, name = '#cc00ff', "ثرو باص"
                    elif "Cross" in act: color, name = '#ffff00', "عرضية"
                    else: color, name = '#00f0ff', "ركلة ركنية"
                    
                    has_end = sub_arrow['x2_scaled'].notna() & (sub_arrow['x2_scaled'] != 0) & (sub_arrow['x2_scaled'] != sub_arrow['x_scaled'])
                    arrow_plots = sub_arrow[has_end]
                    dot_plots = sub_arrow[~has_end]
                    
                    if not arrow_plots.empty:
                        pitch.arrows(arrow_plots['x_scaled'], arrow_plots['y_scaled'], arrow_plots['x2_scaled'], arrow_plots['y2_scaled'], width=2, headwidth=3, headlength=3, color=color, alpha=0.8, ax=ax)
                        pitch.scatter(arrow_plots['x_scaled'], arrow_plots['y_scaled'], color=color, s=40, edgecolors='#ffffff', zorder=3, ax=ax)
                    if not dot_plots.empty:
                        pitch.scatter(dot_plots['x_scaled'], dot_plots['y_scaled'], color=color, s=60, edgecolors='#ffffff', zorder=3, ax=ax)
                        
                    # إضافة السهم للدليل التكتيكي
                    if name not Bristol:
                        legend_elements.append(Line2D([0], [0], color=color, lw=2, solid_capstyle='round', label=name))

            # رسم الأحداث الثابتة والدفاعية
            if not dots_df.empty:
                drawn_dots_actions = set()
                for idx, row in dots_df.iterrows():
                    act_name = row['Clean_Action']
                    if "Goal" in act_name: m_color, m_style, m_size, label_text = '#00ff00', '*', 260, "هدف"
                    elif "Shot" in act_name: m_color, m_style, m_size, label_text = '#ff3366', 'o', 130, "تسديدة"
                    elif "Dribble" in act_name: m_color, m_style, m_size, label_text = '#ffff00', 'P', 120, "مراوغة"
                    elif "Tackle" in act_name: m_color, m_style, m_size, label_text = '#ff00ff', 'X', 130, "تدخل / افتكاك"
                    elif "Clearance" in act_name: m_color, m_style, m_size, label_text = '#ffffff', 's', 110, "تشتيت"
                    elif "Aerial" in act_name: m_color, m_style, m_size, label_text = '#3399ff', '^', 130, "صراع هوائي"
                    elif "Ground" in act_name: m_color, m_style, m_size, label_text = '#8B4513', 'v', 120, "صراع أرضي"
                    elif "Foul" in act_name: m_color, m_style, m_size, label_text = '#ffcc00', 'd', 110, "فاول مكتسب/مرتكب"
                    else: m_color, m_style, m_size, label_text = '#00ffcc', 'h', 120, "ضغط عكسي"
                        
                    pitch.scatter(row['x_scaled'], row['y_scaled'], color=m_color, s=m_size, marker=m_style, edgecolors='#1a1a1a', zorder=4, ax=ax)
                    
                    # إضافة الرمز للدليل التكتيكي بدون تكرار
                    if label_text not in drawn_dots_actions:
                        legend_elements.append(Line2D([0], [0], marker=m_style, color='none', markerfacecolor=m_color, markeredgecolor='#1a1a1a', markersize=10, label=label_text))
                        drawn_dots_actions.add(label_text)

            # وضع دليل الرموز في الأسفل بشكل شيك جداً ومنظم هوريزونتال
            if legend_elements:
                ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.02),
                          ncol=4, fancybox=True, shadow=True, facecolor='#222222', edgecolor='#7c7c7c', 
                          labelcolor='#ffffff', fontsize=11)
            
            # تحديث الملعب
            plot_placeholder.pyplot(fig)
            st.success(f"📋 تم تحليل خريطة الفاعلية لـ ({player_display_name}) وعرض {len(filtered_df)} حدث بنجاح.")
        else:
            # في حالة عدم اختيار أكشنز يظهر الملعب واسم اللاعب فقط
            plot_placeholder.pyplot(fig)
            st.warning("الملعب فارغ، يرجى تفعيل أكشن واحد على الأقل من القائمة الجانبية.")
        plt.close(fig)
    else:
        st.error("عذراً، لم نتمكن من العثور على أعمدة الإحداثيات المطلوبة (X Start, Y Start).")
else:
    st.info("💡 الملعب جاهز؛ يرجى رفع ملف الإكسيل أو CSV من القائمة الجانبية لبدء التحليل التكتيكي المتقدم.")
