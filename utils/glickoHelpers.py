import pandas as pd
import glicko2
from tqdm import tqdm
import numpy as np
import math # Needed for the Glicko/Elo formula

# --- CONFIGURATION ---
# IMPORTANT: Check that this is the correct column name in your DataFrame
# that holds the 'home', 'away', or 'tie' value.
WINNER_COLUMN_NAME = 'Winner' 

def calculate_glicko2_ratings(players_df, matches_df):
    
    """
    Calculates Glicko-2 ratings by iterating chronologically through all matches.
    Uses NumPy pre-allocation for significantly faster processing.
    
    Args:
        players_df (pd.DataFrame): DataFrame containing at least 'playerId'.
        matches_df (pd.DataFrame): DataFrame with 'matchDate', 'winnerId', 'loserId', 
                                         'documentCode', 'dnf', and the WINNER_COLUMN_NAME,
                                         'winnerName', 'loserName', 'winnerCountry', 'loserCountry',
                                         'EventName'.

    Returns:
        pd.DataFrame: A new DataFrame with match ratings (pre and post and delta) for every match, 
                      with final numeric output rounded to 2 decimal places.
    """

    print("--- 🟢 Commencing Glicko-2 Rating Calculation 🟢---")
    
    # 1. Initialize the player "cache"
    print("Initializing player rating cache...")
    player_cache = {
        int(row.playerId): {
            'glicko_obj': glicko2.Player(),
            'match_count': 0
        }
        for row in players_df.itertuples()
    }
    print(f"✅ Cache initialized for {len(player_cache)} players.")

    sorted_matches_df = matches_df.sort_values('matchDate')
    
    dnf_filter_bool = sorted_matches_df['dnf'] == False
    dnf_filter_str = sorted_matches_df['dnf'] == 'False'
    dnf_mask = dnf_filter_bool | dnf_filter_str
    
    matches_to_rate_df = sorted_matches_df[dnf_mask].copy() 
    
    matches_to_rate_df = matches_to_rate_df.dropna(subset=['winnerId', 'loserId'])

    num_matches_to_rate = len(matches_to_rate_df)
    num_original_matches = len(matches_df)

    print(f"🏓 {num_matches_to_rate} matches to rate out of {num_original_matches} total matches. 🏓")

    ratings_history = {
        # --- METADATA COLUMNS (NOW STANDALONE) ---
        'eventId': np.empty(num_matches_to_rate, dtype=int),
        'EventName': np.empty(num_matches_to_rate, dtype=object),
        'documentCode': np.empty(num_matches_to_rate, dtype=object),
        'matchDate': np.empty(num_matches_to_rate, dtype=object),
        'winnerId': np.empty(num_matches_to_rate, dtype=int),
        'winnerName': np.empty(num_matches_to_rate, dtype=object),
        'winnerCountry': np.empty(num_matches_to_rate, dtype=object),
        'loserId': np.empty(num_matches_to_rate, dtype=int),
        'loserName': np.empty(num_matches_to_rate, dtype=object),
        'loserCountry': np.empty(num_matches_to_rate, dtype=object),
        'Winner': np.empty(num_matches_to_rate, dtype=object), # <-- NEW COLUMN
        
        # --- PRE-MATCH RATINGS ---
        'winner_rating_pre': np.empty(num_matches_to_rate, dtype=float),
        'winner_rd_pre': np.empty(num_matches_to_rate, dtype=float),
        'winner_vol_pre': np.empty(num_matches_to_rate, dtype=float),
        'loser_rating_pre': np.empty(num_matches_to_rate, dtype=float),
        'loser_rd_pre': np.empty(num_matches_to_rate, dtype=float),
        'loser_vol_pre': np.empty(num_matches_to_rate, dtype=float),
        
        # --- POST-MATCH RATINGS ---
        'winner_rating_post': np.empty(num_matches_to_rate, dtype=float),
        'loser_rating_post': np.empty(num_matches_to_rate, dtype=float),
        'winner_rd_post': np.empty(num_matches_to_rate, dtype=float),
        'loser_rd_post': np.empty(num_matches_to_rate, dtype=float),
        
        # --- DELTA & ANALYSIS COLUMNS ---
        'winner_rating_delta': np.empty(num_matches_to_rate, dtype=float),
        'loser_rating_delta': np.empty(num_matches_to_rate, dtype=float),
        'rating_difference_pre': np.empty(num_matches_to_rate, dtype=float), # <-- RENAMED
        'expected_outcome': np.empty(num_matches_to_rate, dtype=float),
        
        # --- MATCH COUNT COLUMNS ---
        'winner_matches_played': np.empty(num_matches_to_rate, dtype=int),
        'loser_matches_played': np.empty(num_matches_to_rate, dtype=int),
    }

    for i, row in enumerate(tqdm(matches_to_rate_df.itertuples(index=False), total=num_matches_to_rate)):
        try:
            winner_id = int(row.winnerId)
            loser_id = int(row.loserId)

            winner_cache_entry = player_cache[winner_id]
            loser_cache_entry = player_cache[loser_id]
            
            winner_obj = winner_cache_entry['glicko_obj']
            loser_obj = loser_cache_entry['glicko_obj']

            winner_rating_pre = winner_obj.rating
            loser_rating_pre = loser_obj.rating
            
            rating_difference = loser_rating_pre - winner_rating_pre
            expected_win_chance = 1 / (1 + math.pow(10, rating_difference / 400))
            
            match_outcome = getattr(row, WINNER_COLUMN_NAME, None) # Get 'home', 'away', 'tie'

            # --- Store All Columns ---
            ratings_history['eventId'][i] = row.eventId
            ratings_history['EventName'][i] = row.EventName 
            ratings_history['documentCode'][i] = row.documentCode
            ratings_history['matchDate'][i] = row.matchDate
            ratings_history['winnerId'][i] = winner_id 
            ratings_history['winnerName'][i] = row.winnerName
            ratings_history['winnerCountry'][i] = row.winnerCountry
            ratings_history['loserId'][i] = loser_id 
            ratings_history['loserName'][i] = row.loserName
            ratings_history['loserCountry'][i] = row.loserCountry
            ratings_history['Winner'][i] = match_outcome # <-- STORE THE WINNER/TIE STATUS
            
            ratings_history['winner_rating_pre'][i] = winner_rating_pre
            ratings_history['winner_rd_pre'][i] = winner_obj.rd
            ratings_history['winner_vol_pre'][i] = winner_obj.vol
            ratings_history['loser_rating_pre'][i] = loser_rating_pre
            ratings_history['loser_rd_pre'][i] = loser_obj.rd
            ratings_history['loser_vol_pre'][i] = loser_obj.vol

            ratings_history['rating_difference_pre'][i] = winner_rating_pre - loser_rating_pre # <-- RENAMED
            ratings_history['expected_outcome'][i] = expected_win_chance

            if match_outcome == 'tie':
                winner_obj.update_player([loser_obj.rating], [loser_obj.rd], [0.5]) # 0.5 = Tie
                loser_obj.update_player([winner_obj.rating], [winner_obj.rd], [0.5]) # 0.5 = Tie
            else:
                winner_obj.update_player([loser_obj.rating], [loser_obj.rd], [1.0]) # 1.0 = Win
                loser_obj.update_player([winner_obj.rating], [winner_obj.rd], [0.0]) # 0.0 = Loss

            winner_cache_entry['match_count'] += 1
            loser_cache_entry['match_count'] += 1

            ratings_history['winner_rating_post'][i] = winner_obj.rating
            ratings_history['loser_rating_post'][i] = loser_obj.rating
            ratings_history['winner_rd_post'][i] = winner_obj.rd
            ratings_history['loser_rd_post'][i] = loser_obj.rd
            ratings_history['winner_matches_played'][i] = winner_cache_entry['match_count']
            ratings_history['loser_matches_played'][i] = loser_cache_entry['match_count']

            ratings_history['winner_rating_delta'][i] = winner_obj.rating - winner_rating_pre
            ratings_history['loser_rating_delta'][i] = loser_obj.rating - loser_rating_pre

        
        except KeyError as e:
            # print(f"Warning: Player ID {e} not in cache. Skipping match {row.documentCode}.")
            ratings_history['documentCode'][i] = row.documentCode
            ratings_history['winner_rating_pre'][i] = np.nan
        except Exception as e:
            # print(f"Error processing match {row.documentCode}: {e}")
            ratings_history['documentCode'][i] = row.documentCode
            ratings_history['winner_rating_pre'][i] = np.nan

    print(f"--- ✅ Glicko-2 Calculation Complete ---")
    
    results_df = pd.DataFrame(ratings_history)
    results_df = results_df.dropna(subset=['winner_rating_pre'])

    # Round all float columns at the end
    float_cols = [col for col in results_df.columns if results_df[col].dtype == np.float64]
    results_df[float_cols] = results_df[float_cols].round(2)
    
    # Convert ID and new count columns to integer
    id_cols = ['winnerId', 'loserId', 'winner_matches_played', 'loser_matches_played']
    results_df[id_cols] = results_df[id_cols].astype(int)

    return results_df