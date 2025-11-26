from asyncio import events
import streamlit as st
import pandas as pd
from components.intro import render_intro
import time
from utils.getLatestFiles import get_latest_master_events, get_latest_master_matches, get_latest_master_players
# Import the functions from your utility and component folders


with st.spinner('Loading Data...'):    
    events_df = get_latest_master_events()
    matches_df, update_date = get_latest_master_matches()
    players_df = get_latest_master_players()

st.set_page_config(
    page_title="Table Tennis Stats Dashboard",
    page_icon="🏓",
    layout="wide"
)


st.title("🏓 Table Tennis Stats Exploration📈 ")

st.markdown("Author: **Marcus Annegarn**")

now_date = time.strftime("%Y-%m-%d")
update_date = update_date.strftime("%Y-%m-%d")
if update_date == now_date:
    update_date = "Today"
    st.markdown(f"Today's Date: {now_date} | Data Updated: {update_date} ✔️")
    pass
else:
    st.button("Refresh Data", type = "primary")
    st.markdown(f"Today's Date: {now_date} | Data Updated: {update_date} 🟠 ")








theme = render_intro(events_df, matches_df, players_df)
# Page config and Title (These must be in app.py)






# Load all data (This calls your cached function)
# master_players_df, master_matches_df, master_events_df = get_data()

# Render the Introduction Component
# (Pass the necessary data into the component for display)


