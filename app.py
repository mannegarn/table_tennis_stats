import streamlit as st
import pandas as pd
from components.intro import render_intro
from utils.appGetFiles import get_app_data
# Import the functions from your utility and component folders

# import components.intro

# Page config and Title (These must be in app.py)
st.set_page_config(
    page_title="Table Tennis Stats Dashboard",
    page_icon="🏓",
    layout="wide"
)

st.title("🏓 Table Tennis Stats Exploration📈 ")

master_events_df, master_matches_df, master_players_df = get_app_data()

theme = render_intro(master_events_df, master_matches_df, master_players_df)


# Load all data (This calls your cached function)
# master_players_df, master_matches_df, master_events_df = get_data()

# Render the Introduction Component
# (Pass the necessary data into the component for display)


