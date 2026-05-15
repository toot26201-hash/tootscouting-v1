import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="TootScouting Pro", layout="wide")

st.title("⚽ TootScouting | منصة التحليل الاحترافية")

uploaded_file = st.sidebar.file_uploader("ارفع ملف الـ Actions (CSV)", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # تنظيف المسميات (تحويلها لحروف صغيرة ومسح المسافات الزائدة)
    df.columns = df.columns.str.strip().str.lower()
    
    # فلتر اللاعبين
    if 'player' in df.columns:
        # حذف الصفوف اللي مفيهاش اسم لاعب
        df = df.dropna(subset=['player'])
        player_list = sorted(df['player'].unique().tolist())
        selected_player = st.sidebar.selectbox("اختر اللاعب للتحليل", player_list)
        player_df = df[df['player'] == selected_player].copy()
    else:
        st.sidebar.error("خطأ: عمود 'Player' غير موجود")
        player_df = df

    tab1, tab2, tab3 = st.tabs(["📊 البيانات", "🏹 Pass Map", "🔥 Heatmap"])

    with tab1:
        st.subheader(f"كل إجراءات اللاعب: {selected_player}")
        st.dataframe(player_df)

    # التحقق من وجود أعمدة الإحداثيات (بناءً على ملفك: x start, y start)
    if 'x start' in player_df.columns and 'y start' in player_df.columns:
        
        # تحويل الإحداثيات لمقياس الملعب (نضرب في 120 و 80)
        player_df['x_scaled'] = player_df['x start'] * 120
        player_df['y_scaled'] = player_df['y start'] * 80

        with tab2:
            st.subheader("خريطة التمريرات")
            # فلترة التمريرات فقط
            passes = player_df[player_df['action'].str.contains('pass', case=False, na=False)]
            
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
            fig, ax = pitch.draw(figsize=(10, 7))
            
            if not passes.empty:
                pitch.scatter(passes.x_scaled, passes.y_scaled, s=100, color='#1E3A8A', edgecolors='white', ax=ax)
                st.write(f"تم رصد {len(passes)} تمريرة")
            else:
                st.write("لا توجد تمريرات مسجلة لهذا اللاعب")
            st.pyplot(fig)

        with tab3:
            st.subheader("الخريطة الحرارية (مناطق التمركز)")
            pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#adadad')
            fig, ax = pitch.draw(figsize=(10, 7))
            
            if len(player_df) > 1:
                pitch.kdeplot(player_df.x_scaled, player_df.y_scaled, ax=ax, fill=True, levels=100, thresh=0, cmap='hot', alpha=0.5)
            else:
                st.write("بيانات غير كافية لرسم الخريطة الحرارية")
            st.pyplot(fig)
    else:
        st.error("⚠️ تنبيه: الملف لا يحتوي على أعمدة 'X start' و 'Y start' المطلوبة للرسم.")

else:
    st.info("👋 ارفع ملف الـ Actions (CSV) لتبدأ الفلترة والرسم التكتيكي.")
