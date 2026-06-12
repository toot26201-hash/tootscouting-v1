import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

# ... (نفس كود تحميل البيانات والتصنيف السابق) ...

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
            
            # التأكد من وجود بيانات
            if not subset.empty:
                # نستخدم width أكبر و headwidth لضمان ظهور السهم
                pitch.arrows(subset['x_scaled'], subset['y_scaled'], 
                             subset['x2_scaled'], subset['y2_scaled'], 
                             color=color, width=3, headwidth=6, headlength=6, ax=ax1)
            
            legend_elements.append(Line2D([0], [0], color=color, lw=3, label=p_type))
            
        ax1.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, facecolor='#222222', labelcolor='white')
        st.pyplot(fig1)
