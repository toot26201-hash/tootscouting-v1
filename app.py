import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch

st.set_page_config(layout="wide")
st.title("TootScouting - Advanced Match Analysis")

# 1. Sidebar
st.sidebar.header("📁 DATA LOAD & ANALYSIS")
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # محاولة اكتشاف عمود اللاعبين (لو اسمه Player أو Name)
    player_col = next((col for col in df.columns if col.lower() in ['player', 'name', 'لاعب']), None)
    
    if player_col:
        df = df.rename(columns={player_col: 'Player'})
        df['Player'] = df['Player'].fillna('Unknown').astype(str)
        
        # فلتر اللاعبين
        players_list = ["All Players"] + sorted(df['Player'].unique().tolist())
        selected_player = st.sidebar.selectbox("👤 FILTER BY PLAYER:", players_list)
        
        st.success(f"تم اكتشاف عمود اللاعبين باسم: {player_col}")
    else:
        st.sidebar.error("لم يتم العثور على عمود اللاعبين! تأكد أن الملف يحتوي على عمود اسمه 'Player' أو 'Name'.")
        selected_player = "All Players"

    # باقي الكود...
    df = df.rename(columns={'X Start': 'x1', 'Y Start': 'y1', 'X End': 'x2', 'Y End': 'y2'})
    # ... (بقية منطق الرسم والتصنيف زي ما عملنا في الخطوات اللي فاتت)
