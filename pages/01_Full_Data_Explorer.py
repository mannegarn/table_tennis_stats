import re
import select
from matplotlib.style import available
import streamlit as st
import pandas as pd
import numpy as np
from utils.getLatestFiles import get_latest_master_events, get_latest_master_matches, get_latest_master_players
from utils.showFullData import filter_dataframes_by_text, render_events_table, render_players_table, render_matches_table

st.set_page_config(page_title="Data Explorer", page_icon="🔎", layout="wide")
st.title("🔎 Dataset Explorer")

events_df = get_latest_master_events()
matches_df, update_date = get_latest_master_matches()
players_df = get_latest_master_players()

match_counts = matches_df.groupby('eventId').size().reset_index(name='Match Count')
events_df = events_df.merge(
    match_counts,
    on='eventId',
    how='left'
)
events_df['Match Count'] = events_df['Match Count'].fillna(0).astype(int)
events_df.set_index('eventId', inplace=True)





# --- 2. Build your Tabs and Tables (Same code as before) ---
tab1, tab2, tab3 = st.tabs(["📅 Events", "👤 Players", "🏓 Matches"])

with tab1: 
    st.subheader("📅 Master Events Data")  
        
    render_events_table(events_df)

with tab2:
    st.subheader("👤 Master Players Data")
    
            
    render_players_table(players_df=players_df)

with tab3:
    st.subheader("🏓 Master Matches Data")   
        
    render_matches_table(matches_df)