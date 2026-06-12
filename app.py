import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Crosses Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    
    # تحجيم البيانات
    df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80
    df['x2_scaled'], df['y2_scaled'] = df['x2'] * 120, df['y2'] * 80

    # تصنيف خاص للعرضيات
    def classify(row):
        val = str(row['Action']).lower()
        if 'cross' in val or 'عرضية' in val: return "Cross"
        return "Other"

    df['Type'] = df.apply(classify, axis=1)
    
    # فلترة للعرضيات فقط
    crosses_df = df[df['Type'] == "Cross"]

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Crosses Map")
        fig1, ax1 = plt.subplots(figsize=(10, 7))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax1)
        fig1.patch.set_facecolor('#1a1a1a')
        
        # رسم العرضيات باللون الذهبي
        if not crosses_df.empty:
            pitch.arrows(crosses_df['x_scaled'], crosses_df['y_scaled'], 
                         crosses_df['x2_scaled'], crosses_df['y2_scaled'], 
                         color='#FFD700', width=3, headwidth=6, headlength=6, ax=ax1)
            
            # الدليل
            legend_elements = [Line2D([0], [0], color='#FFD700', lw=3, label='Cross')]
            ax1.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), facecolor='#222222', labelcolor='white')
        
        st.pyplot(fig1)

    with col2:
        st.subheader("🔥 Heatmap of Crosses")
        fig2, ax2 = plt.subplots(figsize=(10, 7))
        pitch.draw(ax=ax2)
        fig2.patch.set_facecolor('#1a1a1a')
        if not crosses_df.empty:
            pitch.kdeplot(crosses_df['x_scaled'], crosses_df['y_scaled'], ax=ax2, fill=True, levels=50, cmap='YlOrBr', alpha=0.6)
        st.pyplot(fig2)
