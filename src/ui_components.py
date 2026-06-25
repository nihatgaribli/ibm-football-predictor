"""
UI Components Module

This module contains all UI-related functions including theme CSS,
insight cards, gauges, and other visual components.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any, Tuple


def get_theme_css(theme: str = 'dark') -> str:
    """
    Get the CSS styling for the application based on the selected theme.
    
    Parameters
    ----------
    theme : str
        Theme mode - either 'light' or 'dark'
        
    Returns
    -------
    str
        CSS styling as a string
    """
    if theme == 'light':
        return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Poppins', sans-serif; }

    /* Light mode - Clean white background with subtle gradients */
    .stApp {
        background:
            radial-gradient(1200px 620px at 12% -8%, rgba(16, 185, 129, 0.08), transparent 60%),
            radial-gradient(1100px 560px at 100% 0%, rgba(59, 130, 246, 0.08), transparent 55%),
            radial-gradient(1000px 760px at 50% 120%, rgba(139, 92, 246, 0.06), transparent 60%),
            linear-gradient(160deg, #ffffff 0%, #f8fafc 48%, #f1f5f9 100%);
        background-attachment: fixed;
    }

    /* Main hero header with animated gradient */
    .main-header {
        font-size: 3.6rem;
        font-weight: 800;
        background: linear-gradient(110deg, #059669 0%, #0284c7 35%, #6366f1 70%, #059669 100%);
        background-size: 250% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.4rem;
        letter-spacing: 1.5px;
        animation: shine 6s linear infinite, float 4s ease-in-out infinite;
        filter: drop-shadow(0 4px 16px rgba(14, 165, 233, 0.25));
    }

    @keyframes shine { to { background-position: 250% center; } }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }

    .sub-header {
        font-size: 1.15rem;
        color: rgba(51, 65, 85, 0.85);
        text-align: center;
        margin-bottom: 1.6rem;
        font-weight: 400;
        letter-spacing: 0.5px;
    }

    /* Pill badges under header */
    .badge-row { text-align: center; margin-bottom: 1.8rem; }
    .badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        margin: 0 0.3rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #334155;
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    /* Glass cards — more visible in light mode */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1.5px solid rgba(14, 165, 233, 0.25) !important;
        border-radius: 18px !important;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.08), 0 1px 4px rgba(0, 0, 0, 0.06);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-4px);
        border-color: rgba(14, 165, 233, 0.45) !important;
        box-shadow: 0 12px 32px rgba(14, 165, 233, 0.18), 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.15);
        border-radius: 14px;
        padding: 0.8rem 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    [data-testid="stMetricLabel"] p {
        color: rgba(51, 65, 85, 0.8) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.72rem !important;
    }
    [data-testid="stMetric"],
    [data-testid="stMetric"] * {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        white-space: normal !important;
        overflow: visible !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        text-overflow: unset !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
        font-weight: 800;
        line-height: 1.25;
        background: linear-gradient(135deg, #059669 0%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* AI explanation box */
    .explanation-box {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.08) 0%, rgba(139, 92, 246, 0.06) 100%);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-left: 4px solid #0284c7;
        border-radius: 14px;
        padding: 1.3rem 1.4rem;
        margin-top: 0.6rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        color: #1e293b;
        line-height: 1.65;
        font-size: 0.97rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(185deg, rgba(248, 250, 252, 0.98) 0%, rgba(241, 245, 249, 0.98) 100%);
        border-right: 1px solid rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(12px);
    }
    [data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #334155 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
        color: #fff;
        border: none;
        border-radius: 999px;
        padding: 0.6rem 1.6rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }

    /* Inputs */
    .stSelectbox div[data-baseweb="select"] > div,
    .stRadio > div {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    /* Dropdown menus (popovers) and tooltips */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    div[data-baseweb="tooltip"],
    ul[role="listbox"],
    li[role="option"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #f1f5f9 !important;
    }
    
    /* Input fields (like text input if any) */
    input {
        color: #1e293b !important;
        background-color: transparent !important;
    }

    /* Section headers and all text elements */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px;
        margin-top: 0.6rem !important;
    }
    
    p, span, div, label {
        color: #334155 !important;
    }
    
    /* Ensure all Streamlit text is dark */
    .stMarkdown, .stText {
        color: #1e293b !important;
    }

    /* Alerts */
    .stAlert {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }

    /* Expander */
    .streamlit-expanderHeader, details summary {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.1);
        color: #334155 !important;
        font-weight: 600;
    }

    /* Plotly chart container — visible border in light mode */
    .js-plotly-plot {
        border-radius: 20px;
        overflow: hidden;
    }

    /* Wrapper around each Plotly chart */
    [data-testid="stPlotlyChart"] {
        border: 1.5px solid rgba(14, 165, 233, 0.3) !important;
        border-radius: 20px !important;
        box-shadow: 0 6px 24px rgba(14, 165, 233, 0.1), 0 2px 8px rgba(0, 0, 0, 0.06) !important;
        overflow: hidden;
        background: #ffffff;
    }
    
    /* Plotly Legend */
    .js-plotly-plot .legend {
        background: rgba(255, 255, 255, 0.95) !important;
    }
    
    .js-plotly-plot .legend .bg {
        fill: rgba(255, 255, 255, 0.95) !important;
    }

    /* Force all Plotly SVG text to be dark in light mode */
    .js-plotly-plot .gtitle text,
    .js-plotly-plot text.gtitle,
    .js-plotly-plot .xtitle,
    .js-plotly-plot .ytitle,
    .js-plotly-plot .ztitle,
    .js-plotly-plot .g-xtitle text,
    .js-plotly-plot .g-ytitle text,
    .js-plotly-plot .g-ztitle text {
        fill: #1e293b !important;
    }
    .js-plotly-plot .xtick text,
    .js-plotly-plot .ytick text,
    .js-plotly-plot .ztick text {
        fill: #334155 !important;
    }
    /* Override only non-pitch charts: transparent paper_bgcolor = timeline/others */
    /* Pitch charts have dark plot_bgcolor so we don't touch their text */
    
    /* We intentionally do not override .hoverlayer text so Plotly tooltips stay legible 
       on their dark backgrounds. */

    /* Legend card */
    .legend-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        padding: 1rem 1.3rem;
        border-radius: 14px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        color: #334155;
        font-size: 0.92rem;
        line-height: 1.9;
        margin-top: 0.8rem;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: rgba(51, 65, 85, 0.8);
        font-size: 0.92rem;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 18px;
        border: 1px solid rgba(0, 0, 0, 0.06);
        margin-top: 2rem;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #0ea5e9, #6366f1);
        border-radius: 999px;
    }

    /* Spinner */
    .stSpinner > div { border-top-color: #0284c7 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255, 255, 255, 0.7);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 10px;
        color: rgba(51, 65, 85, 0.7) !important;
        font-weight: 600;
        background: transparent;
        padding: 0 18px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%) !important;
        color: #fff !important;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
    }

    /* AI insight cards */
    .insight-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        height: 100%;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .insight-card:hover { transform: translateY(-5px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
    .insight-card .ic-top { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .insight-card .ic-icon { font-size: 1.35rem; }
    .insight-card .ic-title {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.6px;
        text-transform: uppercase; color: rgba(51, 65, 85, 0.7);
    }
    .insight-card .ic-value { font-size: 1.45rem; font-weight: 800; line-height: 1.15; color: #1e293b; }
    .insight-card .ic-sub { font-size: 0.82rem; color: rgba(51, 65, 85, 0.65); margin-top: 0.25rem; }
    .insight-card .ic-bar { position: absolute; left: 0; top: 0; bottom: 0; width: 5px; }

    /* Section sub-title */
    .section-label {
        font-size: 0.78rem; font-weight: 700; letter-spacing: 1.5px;
        text-transform: uppercase; color: rgba(71, 85, 105, 0.9);
        margin: 0.4rem 0 0.2rem 0;
    }

    /* Responsive Adjustments for Mobile */
    @media (max-width: 768px) {
        .main-header { font-size: 2.2rem; background-size: 300% auto; margin-top: 1rem; }
        .sub-header { font-size: 0.95rem; margin-bottom: 1rem; padding: 0 10px; }
        .badge { padding: 0.25rem 0.6rem; font-size: 0.7rem; margin: 0.2rem; }
        .badge-row { margin-bottom: 1rem; }
        [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
        .explanation-box { padding: 1rem; font-size: 0.85rem; margin-top: 0.4rem; }
        .legend-card { padding: 0.8rem 1rem; font-size: 0.8rem; line-height: 1.6; }
        .footer-text { padding: 1rem; font-size: 0.8rem; }
        .insight-card { padding: 0.8rem 1rem; }
        .insight-card .ic-value { font-size: 1.2rem; }
        .insight-card .ic-icon { font-size: 1.1rem; }
        .insight-card .ic-title { font-size: 0.65rem; }
    }
</style>
"""
    else:  # dark theme
        return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Poppins', sans-serif; }

    /* Deep stadium-night background with soft colored light pools */
    .stApp {
        background:
            radial-gradient(1200px 620px at 12% -8%, rgba(16, 185, 129, 0.18), transparent 60%),
            radial-gradient(1100px 560px at 100% 0%, rgba(59, 130, 246, 0.18), transparent 55%),
            radial-gradient(1000px 760px at 50% 120%, rgba(139, 92, 246, 0.16), transparent 60%),
            linear-gradient(160deg, #070b16 0%, #0b1322 48%, #080d18 100%);
        background-attachment: fixed;
    }

    /* Main hero header with animated gradient + float */
    .main-header {
        font-size: 3.6rem;
        font-weight: 800;
        background: linear-gradient(110deg, #34d399 0%, #38bdf8 35%, #818cf8 70%, #34d399 100%);
        background-size: 250% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.4rem;
        letter-spacing: 1.5px;
        animation: shine 6s linear infinite, float 4s ease-in-out infinite;
        filter: drop-shadow(0 6px 24px rgba(56, 189, 248, 0.35));
    }

    @keyframes shine { to { background-position: 250% center; } }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }

    .sub-header {
        font-size: 1.15rem;
        color: rgba(226, 232, 240, 0.82);
        text-align: center;
        margin-bottom: 1.6rem;
        font-weight: 400;
        letter-spacing: 0.5px;
    }

    /* Pill badges under header */
    .badge-row { text-align: center; margin-bottom: 1.8rem; }
    .badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        margin: 0 0.3rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #e2e8f0;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(8px);
    }

    /* Glass cards (st.container(border=True)) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 18px !important;
        box-shadow: 0 10px 34px rgba(0, 0, 0, 0.38);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 46px rgba(56, 189, 248, 0.18);
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 0.8rem 1rem;
    }
    [data-testid="stMetricLabel"] p {
        color: rgba(226, 232, 240, 0.75) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.72rem !important;
    }
    [data-testid="stMetric"],
    [data-testid="stMetric"] * {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        white-space: normal !important;
        overflow: visible !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        text-overflow: unset !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
        font-weight: 800;
        line-height: 1.25;
        background: linear-gradient(135deg, #34d399 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* AI explanation box with depth */
    .explanation-box {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(139, 92, 246, 0.10) 100%);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-left: 4px solid #38bdf8;
        border-radius: 14px;
        padding: 1.3rem 1.4rem;
        margin-top: 0.6rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
        color: #e8eefb;
        line-height: 1.65;
        font-size: 0.97rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(185deg, rgba(13, 20, 38, 0.96) 0%, rgba(10, 15, 30, 0.96) 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(12px);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        background: linear-gradient(135deg, #34d399 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
        color: #fff;
        border: none;
        border-radius: 999px;
        padding: 0.6rem 1.6rem;
        font-weight: 600;
        box-shadow: 0 6px 18px rgba(14, 165, 233, 0.4);
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 26px rgba(99, 102, 241, 0.55);
    }

    /* Inputs (selectbox / radio) */
    .stSelectbox div[data-baseweb="select"] > div,
    .stRadio > div {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }

    /* Section headers */
    h3 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px;
        margin-top: 0.6rem !important;
    }

    /* Alerts / info boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }

    /* Expander */
    .streamlit-expanderHeader, details summary {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #e2e8f0 !important;
        font-weight: 600;
    }

    /* Plotly chart container glow */
    .js-plotly-plot {
        border-radius: 20px;
        box-shadow: 0 14px 44px rgba(0, 0, 0, 0.45);
        overflow: hidden;
    }

    /* Legend list */
    .legend-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        padding: 1rem 1.3rem;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.10);
        color: #e2e8f0;
        font-size: 0.92rem;
        line-height: 1.9;
        margin-top: 0.8rem;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: rgba(226, 232, 240, 0.78);
        font-size: 0.92rem;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 2rem;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #0ea5e9, #6366f1);
        border-radius: 999px;
    }

    /* Spinner */
    .stSpinner > div { border-top-color: #38bdf8 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255, 255, 255, 0.03);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 10px;
        color: rgba(226, 232, 240, 0.7) !important;
        font-weight: 600;
        background: transparent;
        padding: 0 18px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%) !important;
        color: #fff !important;
        box-shadow: 0 6px 18px rgba(14, 165, 233, 0.4);
    }

    /* AI insight cards */
    .insight-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        height: 100%;
        box-shadow: 0 8px 26px rgba(0, 0, 0, 0.32);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .insight-card:hover { transform: translateY(-5px); box-shadow: 0 14px 38px rgba(0,0,0,0.45); }
    .insight-card .ic-top { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .insight-card .ic-icon { font-size: 1.35rem; }
    .insight-card .ic-title {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.6px;
        text-transform: uppercase; color: rgba(226, 232, 240, 0.7);
    }
    .insight-card .ic-value { font-size: 1.45rem; font-weight: 800; line-height: 1.15; color: #f1f5f9; }
    .insight-card .ic-sub { font-size: 0.82rem; color: rgba(226, 232, 240, 0.65); margin-top: 0.25rem; }
    .insight-card .ic-bar { position: absolute; left: 0; top: 0; bottom: 0; width: 5px; }

    /* Section sub-title */
    .section-label {
        font-size: 0.78rem; font-weight: 700; letter-spacing: 1.5px;
        text-transform: uppercase; color: rgba(148, 163, 184, 0.9);
        margin: 0.4rem 0 0.2rem 0;
    }

    /* Responsive Adjustments for Mobile */
    @media (max-width: 768px) {
        .main-header { font-size: 2.2rem; background-size: 300% auto; margin-top: 1rem; }
        .sub-header { font-size: 0.95rem; margin-bottom: 1rem; padding: 0 10px; }
        .badge { padding: 0.25rem 0.6rem; font-size: 0.7rem; margin: 0.2rem; }
        .badge-row { margin-bottom: 1rem; }
        [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
        .explanation-box { padding: 1rem; font-size: 0.85rem; margin-top: 0.4rem; }
        .legend-card { padding: 0.8rem 1rem; font-size: 0.8rem; line-height: 1.6; }
        .footer-text { padding: 1rem; font-size: 0.8rem; }
        .insight-card { padding: 0.8rem 1rem; }
        .insight-card .ic-value { font-size: 1.2rem; }
        .insight-card .ic-icon { font-size: 1.1rem; }
        .insight-card .ic-title { font-size: 0.65rem; }
    }
</style>
"""


def insight_card_html(icon: str, title: str, value: str, sub: str, accent: str) -> str:
    """
    Generate HTML for a single glassmorphism insight card.
    
    Parameters
    ----------
    icon : str
        Emoji or icon to display
    title : str
        Card title
    value : str
        Main value to display
    sub : str
        Subtitle or description
    accent : str
        Accent color for the left bar
        
    Returns
    -------
    str
        HTML string for the insight card
    """
    return (
        f'<div class="insight-card"><div class="ic-bar" style="background:{accent};"></div>'
        f'<div class="ic-top"><span class="ic-icon">{icon}</span>'
        f'<span class="ic-title">{title}</span></div>'
        f'<div class="ic-value">{value}</div><div class="ic-sub">{sub}</div></div>'
    )


def make_dominance_gauge(att_pct: float, att_label: str) -> go.Figure:
    """
    Build a dark-themed gauge showing the attacking team's control share.
    
    Parameters
    ----------
    att_pct : float
        Attacking team control percentage (0-100)
    att_label : str
        Label for the attacking team
        
    Returns
    -------
    go.Figure
        Plotly gauge figure
    """
    is_light = st.session_state.get('theme_mode', 'dark') == 'light'

    num_color  = '#0f172a' if is_light else '#f1f5f9'
    tick_color = 'rgba(0,0,0,0.25)' if is_light else 'rgba(255,255,255,0.3)'
    tick_font  = 'rgba(0,0,0,0.55)' if is_light else 'rgba(255,255,255,0.55)'
    title_color = 'rgba(15,23,42,0.85)' if is_light else 'rgba(226,232,240,0.8)'
    threshold_color = '#0f172a' if is_light else 'white'
    font_color  = '#1e293b' if is_light else 'white'

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=att_pct,
        number=dict(suffix="%", font=dict(size=32, color=num_color)),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickcolor=tick_color,
                tickfont=dict(color=tick_font, size=10)
            ),
            bar=dict(color="#38bdf8", thickness=0.28),
            bgcolor="rgba(255,255,255,0.04)" if not is_light else "rgba(0,0,0,0.03)",
            borderwidth=0,
            steps=[
                dict(range=[0, 50], color="rgba(255,77,94,0.25)"),
                dict(range=[50, 100], color="rgba(46,155,255,0.25)")
            ],
            threshold=dict(
                line=dict(color=threshold_color, width=3),
                thickness=0.85,
                value=50
            ),
        ),
        title=dict(
            text=f"{att_label} · attacking-third control",
            font=dict(size=13, color=title_color)
        ),
    ))
    
    fig.update_layout(
        height=230,
        margin=dict(l=24, r=24, t=54, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Poppins", color=font_color)
    )
    
    return fig


def extract_ai_insights(analysis_result: Dict[str, Any]) -> Tuple[Tuple, Tuple, Dict]:
    """
    Extract key talking points from a shot's spatial analysis.
    
    Parameters
    ----------
    analysis_result : dict
        Analysis result dictionary containing player areas and team dominance
        
    Returns
    -------
    tuple
        (most_space, most_tight, dominance) where:
        - most_space: (player_name, area) tuple for player with most space
        - most_tight: (player_name, area) tuple for player with least space
        - dominance: dict of team dominance percentages
    """
    areas = analysis_result.get('player_areas', {})
    nz = {k: v for k, v in areas.items() if v and v > 0}
    most_space = max(nz.items(), key=lambda x: x[1]) if nz else (None, 0.0)
    most_tight = min(nz.items(), key=lambda x: x[1]) if nz else (None, 0.0)
    dom = analysis_result.get('team_dominance', {})
    return most_space, most_tight, dom

# Made with Bob
