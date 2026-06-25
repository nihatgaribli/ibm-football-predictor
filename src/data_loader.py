"""
Data Loader Module

This module contains functions for loading and caching soccer match data
from StatsBomb API.
"""

import streamlit as st
import pandas as pd
from typing import Dict
from .soccer_tracking_data import get_soccer_tracking_data, get_world_cup_matches


@st.cache_data
def load_world_cup_matches() -> Dict:
    """
    Load and cache World Cup 2022 matches.
    
    Returns
    -------
    Dict
        Dictionary containing World Cup 2022 match information
    """
    return get_world_cup_matches()


@st.cache_data
def load_tracking_data(match_id: int) -> pd.DataFrame:
    """
    Load and cache tracking data from StatsBomb.
    
    Parameters
    ----------
    match_id : int
        The match ID to load tracking data for
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing tracking data for the specified match
    """
    try:
        with st.spinner('Loading tracking data from StatsBomb...'):
            df = get_soccer_tracking_data(match_id=match_id)
        return df
    except Exception as e:
        st.error(f"Error loading tracking data: {e}")
        return pd.DataFrame()

# Made with Bob
