import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Debugging Arrows")

uploaded_file = st.sidebar.file_uploader("Upload Data", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تحويل الأعمدة لـ numeric للتأكد من عدم وجود نصوص
    for col in ['X Start', 'Y Start', 'X End', 'Y End']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # تحديث الإحداثيات
    df['x1'] = df['X Start'] * 120
    df['y1'] = df['Y Start'] * 80
    df['x2'] = df['X End'] * 120
    df['y2'] = df['Y End'] * 80

    # فلترة العرضيات فقط
    df['is_cross'] = df['Action'].astype(str).str.contains('cross', case=False) | df['Action'].astype(str).str.contains('عرضية', case=False)
    crosses = df[df['is_cross'] == True]

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Crosses Found: {len(crosses)}")
        fig, ax = plt.subplots(figsize=(10, 7))
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
        pitch.draw(ax=ax)
        
        if not crosses.empty:
            # رسم نقاط البداية (للتأكد أن البيانات موجودة)
            ax.scatter(crosses['x1'], crosses['y1'], color='red', s=50, zorder=3, label='Start Point')
            
            # رسم الأسهم
            pitch.arrows(crosses['x1'], crosses['y1'], crosses['x2'], crosses['y2'], 
                         color='#FFD700', width=3, headwidth=6, headlength=6, ax=ax)
            
        st.pyplot(fig)
        
        # عرض البيانات للتأكد من القيم
        st.write(crosses[['X Start', 'Y Start', 'X End', 'Y End']])
