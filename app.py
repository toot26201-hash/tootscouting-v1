import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

# ... (باقي الكود كما هو)

    # 4. الرسم
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')
    pitch.draw(ax=ax)
    fig.patch.set_facecolor('#1a1a1a')
    
    # إضافة اسم اللاعب في المنتصف (التعديل الجديد)
    ax.text(60, 40, selected_player, color='#D4AF37', fontsize=60, fontweight='bold', 
            ha='center', va='center', alpha=0.15, zorder=1)

    # إعدادات الألوان والرموز (configs)
    # ... (باقي كود الرسم والـ Legend كما هو)

    st.pyplot(fig)
