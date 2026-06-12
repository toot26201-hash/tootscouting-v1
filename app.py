import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Tactical Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    df['x_scaled'], df['y_scaled'] = df['x1'] * 120, df['y1'] * 80
    df['x2_scaled'], df['y2_scaled'] = df['x2'] * 120, df['y2'] * 80

    # تصنيف الأكشنات (تم إضافة العرضيات بوضوح)
    def classify(row):
        val = str(row['Action']).lower()
        if 'cross' in val or 'عرضية' in val: return "Cross"
        if 'shot' in val or 'تسديد' in val: return "Shot"
        if 'pass' in val or 'تمرير' in val: return "Pass"
        return "Other"

    df['Type'] = df.apply(classify, axis=1)
    
    selected_actions = st.sidebar.multiselect("Select Actions:", options=df['Type'].unique().tolist(), default=df['Type'].unique().tolist())
    filtered_df = df[df['Type'].isin(selected_actions)]

    # لوحة الألوان (العرضيات ذهبي)
    colors = {"Cross": "#FFD700", "Shot": "#FF0000", "Pass": "#00FF00", "Other": "#FFFFFF"}

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Actions Map")
        fig1, ax1 = plt.subplots(figsize=(10, 7))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax1)
        fig1.patch.set_facecolor('#1a1a1a')
        
        legend_elements = []
        for act in selected_actions:
            subset = filtered_df[filtered_df['Type'] == act]
            color = colors.get(act, "#FFFFFF")
            
            # رسم العرضيات كـ أسهم ذهبية
            pitch.arrows(subset['x_scaled'], subset['y_scaled'], subset['x2_scaled'], subset['y2_scaled'], 
                         color=color, width=3, headwidth=6, headlength=6, ax=ax1)
            
            legend_elements.append(Line2D([0], [0], color=color, lw=3, label=act))
            
        ax1.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, facecolor='#222222', labelcolor='white')
        st.pyplot(fig1)

    with col2:
        st.subheader("🔥 Heatmap")
        fig2, ax2 = plt.subplots(figsize=(10, 7))
        pitch.draw(ax=ax2)
        fig2.patch.set_facecolor('#1a1a1a')
        if not filtered_df.empty:
            pitch.kdeplot(filtered_df['x_scaled'], filtered_df['y_scaled'], ax=ax2, fill=True, levels=100, cmap='inferno', alpha=0.6)
        st.pyplot(fig2)
