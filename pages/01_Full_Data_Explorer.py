import select
import streamlit as st
from utils.getLatestFiles import get_latest_master_events, get_latest_master_matches, get_latest_master_players
import pandas as pd
import numpy as np

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



def filter_dataframes_by_text(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """
    Filters a DataFrame by checking if the search term is present in ANY string column.
    
    Args:
        df (pd.DataFrame): The DataFrame to search (e.g., events_df or players_df).
        search_term (str): The term to search for (case-insensitive).
        
    Returns:
        pd.DataFrame: The filtered DataFrame copy.
    """
    
    if not search_term or pd.isna(search_term) or not isinstance(search_term, str):
        return df # Return original DF if search term is empty or invalid
    
    search_term = search_term.strip()
    if not search_term:
        return df

    # 1. Identify all string (object) columns
    # We select columns that have 'object' (string) or 'string' dtype.
    string_cols = df.select_dtypes(include=['object', 'string']).columns

    # 2. Initialize the master search filter to all False
    # The filter must be the same length as the DataFrame
    master_filter = pd.Series(False, index=df.index)

    # 3. Build the filter dynamically
    # We iterate through each string column and use the OR operator (|)
    # to combine the results.
    for col in string_cols:
        # Check if the column is NOT entirely missing (for safety)
        if not df[col].empty:
            # .str.contains is vectorized. na=False is crucial here.
            column_filter = df[col].astype(str).str.contains(search_term, case=False, na=False)
            
            # Combine the current column filter with the master filter using OR
            master_filter = master_filter | column_filter
            
    # 4. Return the filtered DataFrame
    return df[master_filter].copy()


# --- 2. Build your Tabs and Tables (Same code as before) ---
tab1, tab2, tab3 = st.tabs(["📅 Events", "👤 Players", "🏓 Matches"])

with tab1:
 
    st.subheader("📅 Master Events Data")
    def render_events_table(events_df):

        """
        Renders an interactive table for the Events DataFrame with filters.
        """ 
    
        filtered_df = events_df.copy()
        

        search_term = st.text_input("🔍 Search Events", placeholder="search for text in any column e.g country / event type / sponsor brand")
        filtered_df = filter_dataframes_by_text(filtered_df, search_term)
     

        st.caption(f"Showing {len(filtered_df)} events")

        st.dataframe(
            filtered_df,
            width="stretch",
            hide_index=True,
            column_config={
                "eventId": st.column_config.NumberColumn("ID", format="%d"),
                "EventName": st.column_config.TextColumn("Event Name", width="medium"),
                "StartDate": st.column_config.DateColumn("Start Date", format="YYYY-MM-DD"),
                "EndDate": st.column_config.DateColumn("End Date", format="YYYY-MM-DD"),
                "TableBrand": st.column_config.TextColumn("Table Brand", help="Manufacturer of the table used"),
                "BallSponsor": st.column_config.TextColumn("Ball Sponsor"),
                "EventCountry": st.column_config.TextColumn("Country"),
                "EventType": st.column_config.TextColumn("Event Type"),
                "ContinentCode": st.column_config.TextColumn("Continent"),
                "Match Count": st.column_config.NumberColumn("Match Count", format="%d"),
                "EventStatus": st.column_config.TextColumn("Ongoing Status"),
            },
            height=500,          

        )
        
    render_events_table(events_df)

with tab2:


    st.subheader("👤 Master Players Data")
    def render_events_table(players_df):

        """
        Renders an interactive table for the Events DataFrame with filters.
        """ 

        gender_options = ["M", "F", "All"]
        selected_gender = st.selectbox("Select Gender", gender_options)
        if selected_gender != "All":
            players_df = players_df[players_df["Gender"] == selected_gender]

        filtered_df = players_df.copy()

        filtered_df = filtered_df[["PlayerName", "Gender",
                                   "Age", "DOB", "OrganizationName",
                                   "Hand","Grip", "Style"]]

        search_term = st.text_input("🔍 Search Players", placeholder="search for text in any column e.g country / name / hand / style ")
        filtered_df = filter_dataframes_by_text(filtered_df, search_term)
        

        st.caption(f"Showing {len(filtered_df)} players")

        st.dataframe(
            filtered_df,
            width="stretch",
            hide_index=True,
            column_config={
                "PlayerName": st.column_config.TextColumn("Name", width="medium"),
                "Gender": st.column_config.TextColumn("Gender", width="small"   ),
                "Age": st.column_config.NumberColumn("Age", format="%d"),
                "DOB": st.column_config.DateColumn("Date of Birth", format="YYYY-MM-DD"),
                "OrganizationName": st.column_config.TextColumn("Organization"),
                "Hand": st.column_config.TextColumn("Hand"),
                "Grip": st.column_config.TextColumn("Grip"),
                "Style": st.column_config.TextColumn("Style"),
                
            },
            height=500,
            

        )# 
        
    render_events_table(players_df=players_df)



with tab3:
    pass