# التعديل المطلوب ليكون لون النص أبيض (labelcolor='#f8fafc')
ax_all.legend(
    handles=get_full_legend(), 
    loc='upper left', 
    bbox_to_anchor=(1.01, 1), 
    fontsize='small', 
    framealpha=1, 
    facecolor='#0f172a',    # الخلفية الداكنة الأصلية لمنظومتك
    edgecolor='#334155',    # الحدود
    labelcolor='#f8fafc'    # <--- هذا هو التعديل الذي يجعل النص أبيض
)
