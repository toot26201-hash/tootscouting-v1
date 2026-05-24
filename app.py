import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
import seaborn as sns
from PIL import Image
import os
import matplotlib.colors as mcolors
import numpy as np
import base64

# Function to read and encode the club logo to Base64
def get_base64_logo():
    current_dir = os.path.dirname(__file__)
    possible_paths = [
        os.path.join(current_dir, 'Espoon_Palloseura_logo.png'),
        os.path.join(current_dir, 'espoon_palloseura_logo.png'),
        'Espoon_Palloseura_logo.png',
        'espoon_palloseura_logo.png'
    ]
    logo_filename = None
    for path in possible_paths:
        if os.path.exists(path):
            logo_filename = path
            break
    if logo_filename and os.path.exists(logo_filename):
        with open(logo_filename, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# Page Config & Strict Dark Premium Theme (TootScouting Global Style)
st.set_page_config(page_title="TootScouting Tactical Master Pro", layout="wide")

st.markdown("""
    <style>
    /* Global Background and Text Color */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #334155;
    }
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #f8fafc !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #0f172a;
        padding: 8px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        color: #94a3b8 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #a47e3c !important; 
        color: #ffffff !important;
        border-color: #a47e3c !important;
    }

    /* CYBER GLOW GLOWING PLAYER CARD DESIGN */
    .premium-player-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%);
        border: 2px solid #38bdf8;
        border-radius: 20px;
        padding: 26px;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.7), inset 0 0 20px rgba(56, 189, 248, 0.2);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
        animation: cardGlowPulse 4s infinite alternate;
    }
    @keyframes cardGlowPulse {
        0% { box-shadow: 0 0 20px rgba(56, 189, 248, 0.5); }
        100% { box-shadow: 0 0 35px rgba(56, 189, 248, 0.9); }
    }
    .premium-card-left {
        display: flex;
        align-items: center;
        gap: 20px;
        z-index: 2;
    }
    .premium-player-img-wrapper {
        position: relative;
        width: 115px;
        height: 115px;
        border-radius: 50%;
        border: 3px solid #fbbf24;
        background-color: #ffffff !important; 
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.8);
        overflow: hidden;
    }
    .premium-player-logo-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 6px;
    }
    .premium-player-meta h2 {
        margin: 0;
        font-size: 2.2rem !important;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 0 0 10px rgba(255,255,255,0.4);
    }
    .premium-player-meta p {
        margin: 4px 0 0 0;
        font-size: 1rem;
        color: #38bdf8;
        font-weight: 600;
    }
    .premium-card-right {
        display: flex;
        gap: 15px;
        z-index: 2;
    }
    .premium-stat-tile {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 14px;
        padding: 16px;
        min-width: 105px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    }
    .premium-stat-tile-large {
        background: linear-gradient(135deg, #0284c7 0%, #1e3a8a 100%);
        border: 2px solid #38bdf8;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.8);
    }
    .premium-tile-val {
        font-size: 2rem;
        font-weight: 900;
        color: #ffffff;
        line-height: 1;
        text-shadow: 0 0 8px rgba(255,255,255,0.6);
    }
    .premium-tile-lbl {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 6px;
        letter-spacing: 0.5px;
    }
    .premium-stat-tile-large .premium-tile-lbl {
        color: #f1f5f9;
