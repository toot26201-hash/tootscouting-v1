import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# ... [نفس كود الإعدادات وتحميل البيانات السابق] ...

    with tab2:
        pitch, fig2, ax2 = draw_toot_pitch(sel_player)
        selected_actions = att_choices + def_choices
        
        # إنشاء قائمة بالرموز للدليل (Legend)
        legend_elements = []
        
        for act in selected_actions:
            subset = p_df[p_df['Action'].str.contains(act, case=False, na=False) | p_df['Tags'].str.contains(act, case=False, na=False)]
            for _, row in subset.iterrows():
                tag = str(row['Tags']).lower()
                
                # [نفس منطق الرسم السابق مع إضافة label لكل عنصر]
                if act == 'Corner':
                    pitch.arrows(row['x_scaled'], row['y_scaled'], row['x2_scaled'], row['y2_scaled'], ax=ax2, color='blue', width=2, headwidth=5, zorder=3)
                elif act == 'Cross':
                    pitch.arrows(row['x_scaled'], row['y_scaled'], row['x2_scaled'], row['y2_scaled'], ax=ax2, color='orange', width=2, headwidth=5, zorder=3)
                elif act in ["Pass", "Progressive Pass"]:
                    color = '#2ecc71' if 'success' in tag else '#e74c3c'
                    pitch.arrows(row['x_scaled'], row['y_scaled'], row['x2_scaled'], row['y2_scaled'], ax=ax2, color=color, width=2, headwidth=5, zorder=3)
                elif act == 'Shot':
                    color = '#2563eb' if 'on target' in tag else '#dc2626'
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='*', s=200, zorder=3)
                elif act == 'Goal':
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color='gold', marker='*', s=300, zorder=3)
                elif act == 'Foul':
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color='red', marker='x', s=150, zorder=3)
                elif act == 'pressing':
                    ax2.text(row['x_scaled'], row['y_scaled'], '#', color='#2ecc71', fontsize=20, fontweight='bold', ha='center', va='center', zorder=3)
                elif act == 'Aerial Duel':
                    color = '#2ecc71' if 'won' in tag else '#e74c3c'
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='^', s=150, zorder=3)
                elif act == 'Ground Duel':
                    color = '#2ecc71' if 'won' in tag else '#e74c3c'
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color=color, marker='s', s=150, zorder=3)
                elif act in ['Tackle', 'extraction']:
                    pitch.scatter(row['x_scaled'], row['y_scaled'], ax=ax2, color='purple', marker='d', s=150, zorder=3)

        # إضافة الدليل (Legend) يدوياً
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label='Corner'),
            Line2D([0], [0], color='orange', lw=2, label='Cross'),
            Line2D([0], [0], color='#2ecc71', marker='>', linestyle='None', label='Pass Success'),
            Line2D([0], [0], color='#e74c3c', marker='>', linestyle='None', label='Pass Failed'),
            Line2D([0], [0], color='gold', marker='*', linestyle='None', label='Goal'),
            Line2D([0], [0], color='red', marker='x', linestyle='None', label='Foul'),
            Line2D([0], [0], color='#2ecc71', marker='#', linestyle='None', label='Pressing'),
            Line2D([0], [0], color='purple', marker='d', linestyle='None', label='Tackle/Extraction')
        ]
        ax2.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
        
        st.pyplot(fig2)
