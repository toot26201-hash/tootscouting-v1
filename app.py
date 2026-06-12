import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Tactical Passing Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    df['x_scaled'], df['y_scaled'] = df['x1'] * 1.2, df['y1'] * 0.8
    df['x2_scaled'], df['y2_scaled'] = df['x2'] * 1.2, df['y2'] * 0.8

    # تصنيف التمريرات بناءً على المنطقة
    def classify_pass(row):
        val = str(row['Action']).lower()
        if 'pass' not in val: return "Other"
        
        x, y = row['x_scaled'], row['y_scaled']
        
        # Zone 14: الوسط (X 80-100, Y 30-50)
        if 80 <= x <= 100 and 30 <= y <= 50: return "Pass in Zone 14"
        
        # Half-Spaces: اليمين (Y 10-30) واليسار (Y 50-70) في الثلث الأخير (X > 80)
        if x >= 80 and (10 <= y <= 30 or 50 <= y <= 70): return "Pass in Half-Space"
        
        return "Other Pass"

    df['Type'] = df.apply(classify_pass, axis=1)
    
    # فلترة التمريرات فقط
    filtered_df = df[df['Type'] != "Other"]

    # لوحة ألوان التمريرات
    pass_colors = {
        "Pass in Zone 14": "#FFD700",    # ذهبي
        "Pass in Half-Space": "#00FF00", # أخضر
        "Other Pass": "#FFFFFF"          # أبيض
    }

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Pass Map (Zone 14 & Half-Spaces)")
        fig1, ax1 = plt.subplots(figsize=(10, 7))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax1)
        fig1.patch.set_facecolor('#1a1a1a')
        
        legend_elements = []
        for p_type in ["Pass in Zone 14", "Pass in Half-Space"]:
            subset = filtered_df[filtered_df['Type'] == p_type]
            color = pass_colors.get(p_type)
            
            # رسم التمريرات كأسهم
            pitch.arrows(subset['x_scaled'], subset['y_scaled'], subset['x2_scaled'], subset['y2_scaled'], 
                         color=color, width=2, headwidth=4, headlength=4, ax=ax1)
            
            legend_elements.append(Line2D([0], [0], color=color, lw=2, label=p_type))
            
        ax1.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, facecolor='#222222', labelcolor='white')
        st.pyplot(fig1)

    with col2:
        st.subheader("🔥 Pass Heatmap")
        fig2, ax2 = plt.subplots(figsize=(10, 7))
        pitch.draw(ax=ax2)
        fig2.patch.set_facecolor('#1a1a1a')
        if not filtered_df.empty:
            pitch.kdeplot(filtered_df['x_scaled'], filtered_df['y_scaled'], ax=ax2, fill=True, levels=100, cmap='inferno', alpha=0.6)
        st.pyplot(fig2)
