import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Tactical Analysis")

# تحميل البيانات
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80

    # تصنيف دقيق يشمل أنواع اللمسات داخل الصندوق
    def classify(row):
        val = str(row['Action']).lower()
        x, y = row['x_scaled'], row['y_scaled']
        in_box = (102 <= x <= 120) and (18 <= y <= 62)
        
        if in_box:
            if 'shot' in val or 'تسديد' in val: return "Shot (Box)"
            if 'pass' in val or 'تمرير' in val: return "Pass (Box)"
            if 'dribble' in val or 'مرواغة' in val: return "Dribble (Box)"
            return "Touch (Box)" # لمسة عادية
        
        if 'cross' in val: return "Cross"
        if 'corner' in val: return "Corner"
        if (80 <= x <= 100) and (30 <= y <= 50): return "Zone 14"
        return "Other"

    df['Type'] = df.apply(classify, axis=1)

    # اختيار الأكشنات
    selected_actions = st.sidebar.multiselect("Select Tactical Actions:", options=df['Type'].unique().tolist(), default=df['Type'].unique().tolist())
    filtered_df = df[df['Type'].isin(selected_actions)]

    # لوحة ألوان مميزة لكل نوع
    colors = {
        "Shot (Box)": "#FF0000",      # أحمر
        "Pass (Box)": "#00FF00",      # أخضر
        "Dribble (Box)": "#FF00FF",   # فوشيا
        "Touch (Box)": "#FFFFFF",     # أبيض
        "Cross": "#FF4500",           # برتقالي
        "Corner": "#00BFFF",          # أزرق سماوي
        "Zone 14": "#FFD700",         # ذهبي
        "Other": "#808080"            # رمادي
    }

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Detailed Actions Map")
        fig1, ax1 = plt.subplots(figsize=(10, 7))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax1)
        fig1.patch.set_facecolor('#1a1a1a')
        
        legend_elements = []
        for act in selected_actions:
            subset = filtered_df[filtered_df['Type'] == act]
            color = colors.get(act, "#FFFFFF")
            # رسم الدوائر مع التسمية
            pitch.scatter(subset['x_scaled'], subset['y_scaled'], color=color, s=150, ax=ax1, alpha=0.8)
            legend_elements.append(Line2D([0], [0], marker='o', color='none', markerfacecolor=color, markersize=12, label=act))
            
        # الدليل أسفل الملعب
        ax1.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, facecolor='#222222', labelcolor='white')
        st.pyplot(fig1)

    with col2:
        st.subheader("🔥 Zone Heatmap")
        fig2, ax2 = plt.subplots(figsize=(10, 7))
        pitch.draw(ax=ax2)
        fig2.patch.set_facecolor('#1a1a1a')
        if not filtered_df.empty:
            pitch.kdeplot(filtered_df['x_scaled'], filtered_df['y_scaled'], ax=ax2, fill=True, levels=100, cmap='inferno', alpha=0.6)
        st.pyplot(fig2)
