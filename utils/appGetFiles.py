import os
import streamlit as st

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Goes up from /utils to /table_tennis_stats

from utils.getLatestFiles import get_latest_master_players, get_latest_master_matches, get_latest_master_events

@st.cache_data
def get_app_data():
    
 
    master_players_df = get_latest_master_players()
    master_events_df = get_latest_master_events()
    master_matches_df = get_latest_master_matches()

    return master_events_df, master_matches_df, master_players_df
