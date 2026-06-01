import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter

def draw_professional_heatmap(p_df, player_name):
    # 1. إعداد الملعب
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#c7d5cc', 
                  linewidth=1, line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 7))

    # 2. إنشاء شبكة (Binning) لتوزيع البيانات
    # استخدام 50x50 يعطي دقة عالية وانسيابية
    bins = (50, 50)
    bin_statistic = pitch.bin_statistic(p_df.x_scaled, p_df.y_scaled, statistic='count', bins=bins)
    
    # 3. تطبيق التصفية الغاوسية (Gaussian Filter) للحصول على الشكل الانسيابي
    # sigma هو المسؤول عن "نعومة" الألوان، 1.5 هو رقم مثالي للنمط الاحترافي
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], sigma=1.5)

    # 4. تعريف الألوان (Custom Colormap)
    # من الأزرق الداكن (الخلفية) إلى الأصفر الفاقع (المنطقة الأكثر كثافة)
    colors = ['#1d2d44', '#1f5f8b', '#3a9ad9', '#8ccb7e', '#fbd400']
    cmap = LinearSegmentedColormap.from_list('toot_cmap', colors, N=100)

    # 5. رسم الهيت ماب
    # vmin=0 يضمن أن المناطق الخالية تظل شفافة أو بلون الخلفية
    heatmap = pitch.heatmap(bin_statistic, ax=ax, cmap=cmap, zorder=1, vmin=0, vmax=bin_statistic['statistic'].max() * 0.8)

    # 6. إضافة اسم اللاعب كعلامة مائية
    ax.text(60, 40, player_name, fontsize=30, color='#1e293b', 
            alpha=0.2, fontweight='bold', ha='center', va='center', zorder=2)

    return fig, ax

# للاستخدام داخل الكود الخاص بك في التبويب الأول (tab1):
# with tab1:
#     fig, ax = draw_professional_heatmap(p_df, sel_player)
#     st.pyplot(fig)
