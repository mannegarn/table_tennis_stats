
from calendar import c
import streamlit as st
import pandas as pd
from streamlit_theme import st_theme


def render_intro(master_events_df,  master_matches_df, master_players_df):

    theme_dict = st_theme() # Call the component ONCE
        
    # Extract the base string ("light" or "dark")
    if theme_dict and theme_dict.get("base"):
        theme = theme_dict.get("base")
    else:
        theme= "light" # Default fallback

    # load and cache data - 
  
    # --- 4. Main App ---
   
  

    # --- 5. Introduction (Formatted Markdown) ---
    with st.expander("Show Project Introduction & Methodology", expanded=True):
        st.markdown(
            """
            ### Description
            This dashboard is a landing page for a personal data project analyzing professional table tennis. 
            It primarily uses match and event data from the WTT (World Table Tennis) API.

            ### Code 
            The code for this project can be found [here](https://github.com/mannegarn/table_tennis_stats).

            ### Data Sources
            * **WTT API (2021-Present):** Provides complete and accessible data for modern events.
            * https://worldtabletennis.com
            * **ITTF Website (Pre-2021):** Used for supplementary player data (like playing style), as this is unavailable in the WTT API. Older match data from this source may be added in the future.
            * https://results.ittf.link/index.php

            ### Analysis Scope
            * **Matches:** The analysis includes **~24,000 WTT singles matches** (as of November 2025), including matches from team events available in the WTT API.
            * **Exclusions:** Doubles matches, prize money, and world ranking data are not included in this analysis.

            ### Methodology & Data Quality
            * **Cleaning:** All data underwent cleaning, reconciliation, and feature engineering. Some clearly erroneous data has been amended manually.
            * **Quality:** Data for WTT mainline events appears to be high quality. Other regional events sometimes contain less complete or inaccurate data. Verifying every match is not feasible, so I simply have to trust the data available.

            ### Key Focus: Table Types
            A key focus of this project was to analyze player performance on different table types (e.g., "fast" vs. "grippy").
            * Table sponsors were identified from the API.
            * For other events, table manufacturers were manually identified by checking event footage - mostly on the WTT Youtube page which has generally very complete records.
            * https://www.youtube.com/@WTTGlobal
            """
        )


    

    if not master_matches_df.empty and not master_players_df.empty and not master_events_df.empty:
        with st.expander("Dataset Scope", expanded=True):        
        # Create 4 columns for the high-level stats
            col1, col2, col3= st.columns(3)

          
            col3.metric("Total Matches", f"{len(master_matches_df):,}")
            col3.metric("Total Players", f"{len(master_players_df):,}")


            total_womens_count = len(master_matches_df[master_matches_df["subEventName"].str.contains("women", case=False)])
            female_count = len(master_players_df[master_players_df["Gender"] == "F"])
            male_count = len(master_players_df[master_players_df["Gender"] == "M"])

            col1.metric("Women's Matches", f"{total_womens_count:,}   ")
            col2.metric("Men's Matches", f"{len(master_matches_df) - total_womens_count:,}  ")

            
            col1.metric("Women's Players", f"{female_count:,}")
            col2.metric("Men's Players", f"{male_count:,}")

                        

            st.divider()

        with st.expander("Events Covered", expanded=True):        
        # Create 4 columns for the high-level stats
            col1, col2 = st.columns(2)
              #########################
            total_event_count = len(master_events_df)
            col2.metric("Total Events", f"{total_event_count:,}")

            first_event = master_events_df.iloc[0]
            first_event_name = first_event["EventName"]
            first_event_date = first_event["StartDate"]
            
            last_event = master_events_df.iloc[-1]
            last_event_name = last_event["EventName"]
            last_event_date = last_event["StartDate"]                
         
            col1.metric(f"Earliest Event - **{first_event_date}**", f"{first_event_name}")
            col1.metric(f"Latest Event - **{last_event_date}**", f"{last_event_name}")
           

    
        st.header("🏆 Player Leaderboards (Top 5)")
        return theme