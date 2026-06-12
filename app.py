import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Tactical Passing Analysis")

# تحميل البيانات
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    # تأكد أن أسماء الأعمدة في ملفك هي "X Start", "Y Start", "X End", "Y End"
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    # تحجيم الإحداثيات (ضرب في 120 و 80 لتناسب ملعب StatsBomb)
    df['x_scaled'] = df['x1'] * 120
    df['y_scaled'] = df['y1'] * 80
    df['x2_scaled'] = df['x2'] * 120
    df['y2_scaled'] = df['y2'] * 80

    # تصنيف التمريرات
    def classify_pass(row):
        val = str(row['Action']).lower()
        if 'pass' not in val: return "Other"
        x, y = row['x_scaled'], row['y_scaled']
        if 80 <= x <= 100 and 30 <= y <= 50: return "Pass in Zone 14"
        if x >= 80 and (10 <= y <= 30 or 50 <= y <= 70): return "Pass in Half-Space"
        return "Other Pass"

    df['Type'] = df.apply(classify_pass, axis=1)
    filtered_df = df[df['Type'] != "Other"]

    pass_colors = {"Pass in Zone 14": "#FFD700", "Pass in Half-Space": "#00FF00"}

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Pass Map")
        fig1, ax1 = plt.subplots(figsize=(10, 7))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax1)
        fig1.patch.set_facecolor('#1a1a1a')
        
        legend_elements = []
        for p_type in ["Pass in Zone 14", "Pass in Half-Space"]:
            subset = filtered_df[filtered_df['Type'] == p_type]
            if not subset.empty:
                color = pass_colors.get(p_type)
                pitch.arrows(subset['x_scaled'], subset['y_scaled'], 
                             subset['x2_scaled'], subset['y2_scaled'], 
                             color=color, width=3, headwidth=6, headlength=6, ax=ax1)
                legend_elements.append(Line2D([0], [0], color=color, lw=3, label=p_type))
        
        if legend_elements:
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
