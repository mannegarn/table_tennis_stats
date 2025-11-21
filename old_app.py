
import streamlit as st
import pandas as pd
import os
import re
import glob
from PIL import Image, ImageOps
from streamlit_theme import st_theme




try:
    from utils.getLatestFiles import get_latest_master_players, get_latest_master_matches, get_latest_master_events
    from utils.glickoHelpers import calculate_glicko2_ratings, get_final_player_stats
    from utils.winrates import get_player_winrates
except ImportError:
    st.error("Could not import helper functions. Make sure 'utils/getLatestFiles.py' exists.")
    st.stop()

# page / title config ---
st.set_page_config(
    page_title="Table Tennis Stats Dashboard",
    page_icon="🏓",
    layout="wide"
)

theme_dict = st_theme() # Call the component ONCE
    
# Extract the base string ("light" or "dark")
if theme_dict and theme_dict.get("base"):
    theme = theme_dict.get("base")
else:
    theme= "light" # Default fallback

# load and cache data - 
@st.cache_data
def get_data():
    """
    Loads all master files, with individual try-except blocks
    for robustness.
    """
    master_players_df = pd.DataFrame()
    master_matches_df = pd.DataFrame()
    master_events_df = pd.DataFrame()

    try:
        master_players_df = get_latest_master_players()
    except Exception as e:
        st.error(f"Failed to load MASTER Players file: {e}", icon="🔥")

    try:
        master_matches_df = get_latest_master_matches()
    except Exception as e:
        st.error(f"Failed to load MASTER Matches file: {e}", icon="🔥")
    
    try:
        master_events_df = get_latest_master_events()
    except Exception as e:
        st.error(f"Failed to load MASTER Events file: {e}", icon="🔥")
        
    return master_players_df, master_matches_df, master_events_df

# --- 4. Main App ---
st.title("🏓 Table Tennis Stats Exploration 📈")
st.markdown("Author: **Marcus Annegarn** | Date: **2025/11/15**")

# --- 5. Introduction (Formatted Markdown) ---
with st.expander("Show Project Introduction & Methodology", expanded=True):
    st.markdown(
        """
        ### Description
        This dashboard is a landing page for a personal data project analyzing professional table tennis. 
        It primarily uses match and event data from the WTT (World Table Tennis) API.

        ### Data Sources
        * **WTT API (2021-Present):** Provides complete and accessible data for modern events.
        * https://worldtabletennis.com
        * **ITTF Website (Pre-2021):** Used for supplementary player data (like playing style), as this is unavailable in the WTT API. Older match data from this source may be added in the future.
        * https://results.ittf.link/index.php

        ### Analysis Scope
        * **Matches:** The analysis includes **~24,000 WTT singles matches** (as of November 2025), including matches from team events available in the WTT API.
        * **Exclusions:** Doubles matches, prize money, and world ranking data are not included in this analysis.

        ### Methodology & Data Quality
        * **Cleaning:** All data underwentcleaning, reconciliation, and feature engineering. Some clearly erroneous data has been amended manually.
        * **Quality:** Data for WTT mainline events appears to be high quality. Other regional events sometimes contain less complete or inaccurate data. Verifying every match is not feasible, so I simply have to trust the data available.

        ### Key Focus: Table Types
        A key focus of this project was to analyze player performance on different table types (e.g., "fast" vs. "grippy").
        * Table sponsors were identified from the API.
        * For other events, table manufacturers were manually identified by checking event footage - mostly on the WTT Youtube page which has generally very complete records.
        * https://www.youtube.com/@WTTGlobal
        """
    )

# --- 6. Load Data and Display KPIs ---
master_players_df, master_matches_df, master_events_df = get_data()

st.header("Overall Dataset Scope")

if not master_matches_df.empty and not master_players_df.empty and not master_events_df.empty:
    
    # Create 4 columns for the high-level stats
    col1, col2, col3, col4 = st.columns(4)

    total_match_count = len(master_matches_df)
    col1.metric("Total Matches Analyzed", f"{total_match_count:,}")

    # Calculate unique players from the *match file* for an accurate count
    total_player_count = len(master_players_df)
    col2.metric("Unique Players in Matches", f"{total_player_count:,}")

    total_event_count = len(master_events_df)
    col3.metric("Total Events Covered", f"{total_event_count:,}")

        
    st.divider()

    first_event = master_events_df.iloc[0]
    first_event_name = first_event["EventName"]
    first_event_date = first_event["StartDate"]

    last_event = master_events_df.iloc[-1]
    last_event_name = last_event["EventName"]
    last_event_date = last_event["StartDate"]

    st.header("Events Covered ")
    col4, col5 = st.columns(2)

    col4.metric(f"First Event - **{first_event_date}**", first_event_name)
    
    col5.metric(f"Latest Event - **{last_event_date}**", last_event_name)
        

    st.divider()

   
    st.header("🏆 Player Leaderboards (Top 5)")

    # --- Helper Function to prepare all data (cached for performance) ---
    def get_leaderboard_data(players_df, matches_df):
        """
        Runs all Glicko and WinRate calculations for Men and Women
        and merges final player metadata for display.
        """
        # 1. Get player ID sets for filtering
        men_player_ids = set(players_df[players_df['Gender'] == 'M']['playerId'])
        women_player_ids = set(players_df[players_df['Gender'] == 'F']['playerId'])
        
        # 2. Filter matches
        men_matches_filter = matches_df['winnerId'].isin(men_player_ids) & \
                             matches_df['loserId'].isin(men_player_ids)
        men_matches = matches_df[men_matches_filter]
        
        women_matches_filter = matches_df['winnerId'].isin(women_player_ids) & \
                               matches_df['loserId'].isin(women_player_ids)
        women_matches = matches_df[women_matches_filter]

        # 3. Filter players
        men_players = players_df[players_df['Gender'] == 'M']
        women_players = players_df[players_df['Gender'] == 'F']

        # 4. Run your Glicko and WinRate functions
        men_ratings_hist_df = calculate_glicko2_ratings(men_players, men_matches)
        women_ratings_hist_df = calculate_glicko2_ratings(women_players, women_matches)

        men_winrates_df = get_player_winrates(men_players, men_matches, min_matches=10)
        women_winrates_df = get_player_winrates(women_players, women_matches, min_matches=10)

        men_final_stats_df = get_final_player_stats(men_ratings_hist_df)
        women_final_stats_df = get_final_player_stats(women_ratings_hist_df)
        
        # 5. Merge WinRate stats
        men_stats = men_final_stats_df.merge(
            men_winrates_df[['playerId', 'WinRate']], on='playerId', how='left'
        )
        women_stats = women_final_stats_df.merge(
            women_winrates_df[['playerId', 'WinRate']], on='playerId', how='left'
        )
        
        # --- 6. *** NEW FIX: Merge Player Metadata *** ---
        # ADD 'Gender' to this list
        metadata_cols = ['playerId', 'HeadShot', 'flagUrl', 'Gender'] 
        
        men_stats = men_stats.merge(
            players_df[metadata_cols], # Pass 'Gender' from the main players_df
            on='playerId',
            how='left'
        )
        women_stats = women_stats.merge(
            players_df[metadata_cols], # Pass 'Gender' from the main players_df
            on='playerId',
            how='left'
        )
        # --- End of Fix ---
        
        return men_stats, women_stats

    # --- Run the data preparation ---
    # (This will be skipped if the cache is hot)
    try:
        men_stats_df, women_stats_df = get_leaderboard_data(master_players_df, master_matches_df)
    except Exception as e:
        st.error(f"Error generating leaderboard data: {e}")
        st.stop()


    # --- 8. Display Leaderboards in 3 Columns ---
    col1, col2, col3 = st.columns(3)

    # ----------------- COLUMN 1: MOST MATCHES -----------------
    with col1:
        st.subheader("Most Matches Played")
        
        # --- MEN ---
        top_men_matches = men_stats_df.sort_values(by='totalMatches', ascending=False).head(5)
        st.markdown("##### Men")
        st.dataframe(
            top_men_matches[['playerName', 'totalMatches']], 
            hide_index=True, width="stretch"
        )
        
        # --- WOMEN ---
        top_women_matches = women_stats_df.sort_values(by='totalMatches', ascending=False).head(5)
        st.markdown("##### Women")
        st.dataframe(
            top_women_matches[['playerName', 'totalMatches']], 
            hide_index=True, width="stretch"
        )

    # ----------------- COLUMN 2: BEST WIN RATE -----------------
    with col2:
        st.subheader("Best Win Rate (%)")
        
        # --- MEN ---
        top_men_winrate = men_stats_df.sort_values(by='WinRate', ascending=False).head(5)
        st.markdown("##### Men")
        st.dataframe(
            top_men_winrate[['playerName', 'WinRate']],
            column_config={"WinRate": st.column_config.ProgressColumn(
                "Win Rate", format="%.1f%%", min_value=0, max_value=100
            )},
            hide_index=True, width="stretch"
        )
        
        # --- WOMEN ---
        top_women_winrate = women_stats_df.sort_values(by='WinRate', ascending=False).head(5)
        st.markdown("##### Women")
        st.dataframe(
            top_women_winrate[['playerName', 'WinRate']],
            column_config={"WinRate": st.column_config.ProgressColumn(
                "Win Rate", format="%.1f%%", min_value=0, max_value=100
            )},
            hide_index=True, width="stretch"
        )

    # ----------------- COLUMN 3: HIGHEST RATING -----------------
    with col3:
        st.subheader("Highest Glicko-2 Rating")
        
        # --- MEN ---
        top_men_rating = men_stats_df.sort_values(by='ratingFinal', ascending=False).head(5)
        st.markdown("##### Men")
        st.dataframe(
            top_men_rating[['playerName', 'ratingFinal']], 
            hide_index=True, width="stretch"
        )
        
        # --- WOMEN ---
        top_women_rating = women_stats_df.sort_values(by='ratingFinal', ascending=False).head(5)
        st.markdown("##### Women")
        st.dataframe(
            top_women_rating[['playerName', 'ratingFinal']], 
            hide_index=True, width="stretch"
            
            )
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # --- 2. Correct the DEFAULT_HEADSHOTS dictionary ---
    # Join the BASE_DIR with the relative path to create the absolute file path
    DEFAULT_HEADSHOTS={
    "light":{
        "M": os.path.join(BASE_DIR, "imgs", "men_light.png"),
        "F": os.path.join(BASE_DIR, "imgs", "women_light.png")},
    "dark": {
        "M": os.path.join(BASE_DIR, "imgs", "men_dark.png"),
        "F": os.path.join(BASE_DIR, "imgs", "women_dark.png")}
    }
   

    def display_final_leaderboard(df: pd.DataFrame, metric_col: str, metric_label: str, image_width: int = 80) -> None:
        """
        Renders a top-N leaderboard using custom columns and st.image for full size control.
        """
        
        # --- 1. THE FIX: Get the theme ONCE at the start of the function ---
        # Call the st_theme() function
        
        
        # Create the column headers first
        st.markdown(f"**#** | **PLAYER** | **{metric_label.upper()}**", unsafe_allow_html=True)
        st.markdown("---")

        # Loop through the rows to display
        for i, row in enumerate(df.itertuples()):
            rank = i + 1
            
            col_rank, col_img, col_name, col_metric = st.columns([1, 2, 5, 3])

            # Column 1: Rank
            with col_rank:
                st.markdown(f"### {rank}")

            # Column 2: Image
            with col_img:
              
            
                if pd.notna(row.HeadShot):
                    # Remote URL (works fine)
                    st.image(row.HeadShot, width=image_width) 
                else:
                    
                    try:
                        # --- 3. THE FIX: Use the 'current_theme' variable ---
                        default_headshot_path = DEFAULT_HEADSHOTS[theme][row.Gender]
                        st.image(default_headshot_path, width=image_width)
                    except KeyError:
                        st.warning("Default key error.")
                    except Exception as e:
                        st.error("Image load error.")
                
            # Column 3: Name and Flag
            with col_name:
                flag_col, name_col = st.columns([1, 6])
                
                if pd.notna(row.flagUrl):
                    flag_col.image(row.flagUrl, width=30)
                
                name_col.markdown(f"**{row.playerName}**")

            # Column 4: Metric
            with col_metric:
                if metric_col == "WinRate":
                    st.metric(metric_label, f"{row.WinRate:.1f}%")
                else:
                    metric_val = getattr(row, metric_col)
                    st.metric(metric_label, f"{metric_val:,.0f}")
                    
    st.markdown("---")


    # --- 2. REPLACE your "Display Leaderboards" section with this ---
    # (This code calls the new function)

    col1, col2, col3 = st.columns(3)

    # ----------------- COLUMN 1: MOST MATCHES -----------------
    with col1:
        st.subheader("Most Matches Played")
        
        # --- MEN ---
        top_men_matches = men_stats_df.sort_values(by='totalMatches', ascending=False).head(5)
        st.markdown("##### Men")
        display_final_leaderboard(top_men_matches, "totalMatches", "Total Matches")
        
        # --- WOMEN ---
        top_women_matches = women_stats_df.sort_values(by='totalMatches', ascending=False).head(5)
        st.markdown("##### Women")
        display_final_leaderboard(top_women_matches, "totalMatches", "Total Matches")

    # ----------------- COLUMN 2: BEST WIN RATE -----------------
    with col2:
        st.subheader("Best Win Rate (%)")
        
        # --- MEN ---
        top_men_winrate = men_stats_df.sort_values(by='WinRate', ascending=False).head(5)
        st.markdown("##### Men")
        display_final_leaderboard(top_men_winrate, "WinRate", "Win Rate")
        
        # --- WOMEN ---
        top_women_winrate = women_stats_df.sort_values(by='WinRate', ascending=False).head(5)
        st.markdown("##### Women")
        display_final_leaderboard(top_women_winrate, "WinRate", "Win Rate")

    # ----------------- COLUMN 3: HIGHEST RATING -----------------
    with col3:
        st.subheader("Highest Glicko-2 Rating")
        
        # --- MEN ---
        top_men_rating = men_stats_df.sort_values(by='ratingFinal', ascending=False).head(5)
        st.markdown("##### Men")
        display_final_leaderboard(top_men_rating, "ratingFinal", "Glicko-2 Rating")
        
        # --- WOMEN ---
        top_women_rating = women_stats_df.sort_values(by='ratingFinal', ascending=False).head(5)
        st.markdown("##### Women")
        display_final_leaderboard(top_women_rating, "ratingFinal", "Glicko-2 Rating")