# --- استبدل الجزء الخاص بالرسم الجماعي في Tab 2 بهذا الكود ---

    with tab2:
        st.subheader(f"Team Performance Profile: {selected_team}")
        
        # حساب إحصائيات الفريق
        col1, col2, col3, col4 = st.columns(4)
        
        # التأكد من وجود البيانات وتجنب الأخطاء
        shots = team_df[team_df['Action'].str.contains('shot|sh/a', case=False, na=False)]
        goals = team_df[team_df['Tags'].str.contains('goal', case=False, na=False)]
        
        # Area 14 & Box Entries logic
        area14 = team_df[(team_df['x_end_scaled'] >= 80) & (team_df['x_end_scaled'] <= 102) & 
                         (team_df['y_end_scaled'] >= 18) & (team_df['y_end_scaled'] <= 62)]
        
        box_entries = team_df[(team_df['x_end_scaled'] > 102) & 
                              (team_df['y_end_scaled'] >= 18) & (team_df['y_end_scaled'] <= 62)]

        col1.metric("Total Shots", len(shots))
        col2.metric("Goals", len(goals))
        col3.metric("Area 14 Entries", len(area14))
        col4.metric("Box Entries", len(box_entries))

        st.subheader("Team Offensive Zones & Heatmap")
        pitch_team = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#22312b')
        fig_t, ax_t = pitch_team.draw(figsize=(12, 8))
        
        # --- حل مشكلة الخطأ: رسم Area 14 باستخدام matplotlib مباشرة ---
        import matplotlib.patches as patches
        # Area 14 coordinates: x(80 to 102), y(18 to 62)
        rect = patches.Rectangle((80, 18), 22, 44, linewidth=2, edgecolor='blue', facecolor='blue', alpha=0.1)
        ax_t.add_patch(rect)
        ax_t.text(91, 40, "Area 14", color='blue', ha='center', va='center', fontsize=12, fontweight='bold', alpha=0.6)

        # رسم الـ Heatmap للفريق
        if len(team_df) > 1:
            pitch_team.kdeplot(team_df.x_scaled, team_df.y_scaled, ax=ax_t, fill=True, cmap='Reds', alpha=0.5, zorder=1)
        
        # رسم الأهداف كعلامات ذهبية
        if not goals.empty:
            pitch_team.scatter(goals.x_scaled, goals.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax_t, zorder=5, label='Goals')

        st.pyplot(fig_t)
