import pandas as pd
from datetime import datetime, timezone, timedelta
import numpy as np
import streamlit as st
import os
#### Path Definitions (needed for now maybe to do with using notebooks - check this!!!)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Goes up one level from /utils
DEFAULT_EVENTS_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Events')


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
            
    # 4. Return the filtered DataFr
    # ame
    return df[master_filter].copy()
def render_events_table(events_df):

    """
    Renders an interactive table for the Events DataFrame with filters.
    """

    show_raw_data = st.checkbox("Show raw data")
    search_term = st.text_input(
    "🔍 Search Events", 
    placeholder="Search text in any column (e.g., country, type, sponsor)"
    )               

    filtered_df = filter_dataframes_by_text(events_df, search_term)


    st.caption(f"Showing {len(filtered_df)} events")


    if show_raw_data:

        st.dataframe(
            filtered_df, 
            use_container_width=True, 
            height=500
    )
    else:

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "eventId": st.column_config.NumberColumn("ID", format="%d"),
                "EventName": st.column_config.TextColumn("Event Name", width="medium"),
                "StartDate": st.column_config.DateColumn("Start Date", format="YYYY-MM-DD"),
                "EndDate": st.column_config.DateColumn("End Date", format="YYYY-MM-DD"),
                "TableSponsor": st.column_config.TextColumn("Table"),
                "BallSponsor": st.column_config.TextColumn("Ball"),
                "EventCountry": st.column_config.TextColumn("Country"),
                "EventType": st.column_config.TextColumn("Event Type"),
                "ContinentCode": st.column_config.TextColumn("Continent"),
                "Match Count": st.column_config.NumberColumn("Matches"),
                "EventStatus": st.column_config.TextColumn("Status"),
            },
            height=500
        )

def render_players_table(players_df):
        """
        Renders an interactive table for the Players DataFrame with filters.
        Structure: Inputs -> Filter Logic -> Display Logic (Raw vs. Polished).
        """
        
        show_raw_data = st.checkbox("Show raw data ")
        gender_options = ["All", "F", "M"]
        selected_gender = st.selectbox("Select Gender", gender_options)
        search_term = st.text_input(
            "🔍 Search Players", 
            placeholder="Search text in any column (e.g., name, country, style)"
        )

       
        
        filtered_df = players_df.copy()

        
        if selected_gender != "All":
            filtered_df = filtered_df[filtered_df["Gender"] == selected_gender]

        filtered_df = filter_dataframes_by_text(filtered_df, search_term)

    
        st.caption(f"Showing {len(filtered_df)} players")
    
        if show_raw_data:
        
            st.dataframe(
                filtered_df, 
                use_container_width=True, 
                height=500
            )
        else:
            
            display_cols = [
                "PlayerName", "Gender", "Age", "DOB", 
                "OrganizationName", "Hand", "Grip", "Style"
            ]
            
        
            available_cols = [c for c in display_cols if c in filtered_df.columns]
            polished_df = filtered_df[available_cols]

            st.dataframe(
                polished_df,
                width="stretch",
                hide_index=True,
                column_config={
                    "PlayerName": st.column_config.TextColumn("Name", width="medium"),
                    "Gender": st.column_config.TextColumn("Gender", width="small"),
                    "Age": st.column_config.NumberColumn("Age", format="%d"),
                    "DOB": st.column_config.DateColumn("Date of Birth", format="YYYY-MM-DD"),
                    "OrganizationName": st.column_config.TextColumn("Organization"),
                    "Hand": st.column_config.TextColumn("Hand"),
                    "Grip": st.column_config.TextColumn("Grip"),
                    "Style": st.column_config.TextColumn("Style"),
                },
                height=500
            )

def render_matches_table(matches_df):

        """
        Renders an interactive table for the Matches DataFrame with filters.
        """ 
        
        show_raw_data = st.checkbox("Show raw data  ")
        gender_options = ["All", "F", "M"]
        selected_gender = st.selectbox("Select Gender ", gender_options)
        search_term = st.text_input(
            "🔍 Search Matches", 
            placeholder="Search text in any column (e.g. name, event, location)"
        )


        filtered_df = matches_df.copy()
        mens_filter = filtered_df["subEventName"].str.contains("Men", regex=True)
        womens_filter = filtered_df["subEventName"].str.contains("Women", regex=True)
        filtered_df.loc[mens_filter, "subEventName"] = "M"
        filtered_df.loc[womens_filter, "subEventName"] = "F"

    
      
        if selected_gender != "All":
            filtered_df = filtered_df[filtered_df["subEventName"].str.contains(selected_gender)]    


            filtered_df = filter_dataframes_by_text(filtered_df, search_term)

        st.caption(f"Showing {len(filtered_df)} matches ")

        
        if show_raw_data:
            st.dataframe(
                filtered_df, 
                use_container_width=True, 
                height=500
            )
        else:
       
            display_cols = [
                "subEventName", "EventName","Round", "matchDate", "winnerName",
                "winnerCountry", "loserName","loserCountry", "overallScore",
                "gameScore", "duration (unreliable)", "bestOf"
            ]
            available_cols = [c for c in display_cols if c in filtered_df.columns]
            polished_df = filtered_df[available_cols]
                 
            st.dataframe(
                polished_df,
                width="stretch",
                hide_index=True,
                column_config={
                    "subEventName": st.column_config.TextColumn("Gender"),
                    "EventName": st.column_config.TextColumn("Event Name"),
                    "Round": st.column_config.TextColumn("Round", width="small"),
                    "matchDate": st.column_config.DateColumn("Match Date", format="YYYY-MM-DD"),
                    "winnerName": st.column_config.TextColumn("Winner Name", width="medium"),
                    "winnerCountry": st.column_config.TextColumn("Winner Country", width="small"),
                    "loserName": st.column_config.TextColumn("Loser Name", width="medium"),
                    "loserCountry": st.column_config.TextColumn("Loser Country", width="small"),
                    "overallScore": st.column_config.TextColumn("Overall Score", width="small"),
                    "gameScore": st.column_config.TextColumn("Game Score", width="small"),
                    "duration (unreliable)": st.column_config.TextColumn("Duration(unreliable)", width="small"),
                    "bestOf": st.column_config.TextColumn("Best of", width="small")              
                    },
            height=500          

        )# 

