from flag import info
import pandas as pd
import re 
from datetime import datetime
import os


import pandas as pd
from datetime import datetime
import os


def compute_match_winrates( master_matches_df: pd.DataFrame,info_string: str                       
                          ) -> pd.DataFrame:
    """
    Calculates the win rate for every player based on a provided list of matches.

    Args:
        master_matches_df (pd.DataFrame): A DataFrame of all matches to be considered,
                                         containing ['winnerId', 'loserId']. This DataFrame
                                         should be PRE-FILTERED by the user (e.g., by year or event type).
        min_matches (int, optional): The minimum number of total matches required to be included
                                     in the final DataFrame. Defaults to 0.

    Returns:
        pd.DataFrame with the following columns:
                        TotalWins, TotalLosses, TotalMatches, and WinRate (as a percentage),
                      filtered by min_matches.
    """

    
    if (info_string == "") or (not isinstance(info_string, str)) or (info_string.isspace()):
        print (f"❌ Please specify a valid info_string: {info_string} \n❌ File not saved")
        return None
    
    
    player_wins = master_matches_df['winnerId'].value_counts()  
 
    player_losses = master_matches_df['loserId'].value_counts()
    
    match_stats = pd.concat([       

        player_wins.rename('TotalWins'), 
        player_losses.rename('TotalLosses')
    ], axis=1)

    # cvonvert to NaN values (for players with 0 wins or 0 losses) and convert to integer
    match_stats['TotalWins'] = match_stats['TotalWins'].fillna(0).astype(int)
    match_stats['TotalLosses'] = match_stats['TotalLosses'].fillna(0).astype(int)
    
   # get total and percentages
    match_stats['TotalMatches'] = match_stats['TotalWins'] + match_stats['TotalLosses']
    match_stats['TotalMatches'] = match_stats['TotalMatches'].astype(int)
       
    match_stats['WinRate'] = (
        (match_stats['TotalWins'] / match_stats['TotalMatches']) * 100
    ).fillna(0).round(2)
  
       
    # Define columns that should be Integers
    int_cols = ['TotalWins', 'TotalLosses', 'TotalMatches']
    
    # Fill NaNs with 0 and convert to int for these columns
    match_stats[int_cols] = match_stats[int_cols].fillna(0).astype(int)
    
    # Handle 'WinRate' column separately (fill NaN with 0, and round)
    match_stats['WinRate'] = match_stats['WinRate'].fillna(0).round(2)   
    

 
    # Sort the final filtered data
    match_stats = match_stats.sort_values(by=['WinRate'], ascending=False)
    match_stats = match_stats.reset_index().rename(columns={'index': 'playerId'})
   
    # i am keeping this renaming structure for now - remnants of the old code
    # May be  needed later - check this!!! 
    match_stats = match_stats.rename(columns={'WinRate': f"MatchWinRate ({info_string})",
                                    "TotalMatches": f"TotalMatches ({info_string})",
                                    "TotalWins": f"TotalWins ({info_string})",
                                    "TotalLosses": f"TotalLosses ({info_string})"})
    
    return match_stats.reset_index(drop=True)



def compute_set_winrates(master_matches_df: pd.DataFrame, info_string: str) -> pd.DataFrame:
    """
    Calculates the set win rate for every player based on a provided list of matches.
    """
    
    if (info_string == "") or (not isinstance(info_string, str)) or (info_string.isspace()):
        print(f"❌ Please specify a valid info_string: {info_string}")
        return None

    # get sets won 
    # Sum 'winner_sets' grouped by 'winnerId' (Sets won when winning the match)
    sets_won_as_winner = master_matches_df.groupby('winnerId')['winnerSets'].sum()
    # Sum 'loser_sets' grouped by 'loserId' (Sets won when losing the match)
    sets_won_as_loser = master_matches_df.groupby('loserId')['loserSets'].sum()
    
    # Total Sets Won = Sets won in wins + Sets won in losses
    total_sets_won = sets_won_as_winner.add(sets_won_as_loser, fill_value=0)

    #--Calculate Sets Lost 
    # Sum 'loser_sets' grouped by 'winnerId' (Sets lost when winning the match)
    sets_lost_as_winner = master_matches_df.groupby('winnerId')['loserSets'].sum()
    # Sum 'winner_sets' grouped by 'loserId' (Sets lost when losing the match)
    sets_lost_as_loser = master_matches_df.groupby('loserId')['winnerSets'].sum()
    
    # Total Sets Lost = Sets lost in wins + Sets lost in losses
    total_sets_lost = sets_lost_as_winner.add(sets_lost_as_loser, fill_value=0)

   
    set_stats = pd.concat([
        total_sets_won.rename('TotalSetsWon'),
        total_sets_lost.rename('TotalSetsLost')
    ], axis=1).fillna(0).astype(int)

    set_stats['TotalSetsPlayed'] = set_stats['TotalSetsWon'] + set_stats['TotalSetsLost']
    
    set_stats['SetWinRate'] = (
        (set_stats['TotalSetsWon'] / set_stats['TotalSetsPlayed']) * 100
    ).fillna(0).round(2)

    #  Format and Rename ---
    set_stats = set_stats.reset_index().rename(columns={'index': 'playerId'})
    
    # Apply the info_string suffix to columns
    set_stats = set_stats.rename(columns={
        'SetWinRate': f"SetWinRate ({info_string})",
        'TotalSetsPlayed': f"TotalSetsPlayed ({info_string})",
        'TotalSetsWon': f"TotalSetsWon ({info_string})",
        'TotalSetsLost': f"TotalSetsLost ({info_string})"
    })

    return set_stats




def compute_point_winrates(master_matches_df: pd.DataFrame, info_string: str) -> pd.DataFrame:
    """
    Calculates the point win rate for every player based on a provided list of matches.
    """
    
    if (info_string == "") or (not isinstance(info_string, str)) or (info_string.isspace()):
        print(f"❌ Please specify a valid info_string: {info_string}")
        return None

    # --- 1. Calculate Points Won ---
    # Points won when winning the match
    points_won_as_winner = master_matches_df.groupby('winnerId')['winnerTotalPoints'].sum()
    # Points won when losing the match (loser_total_points)
    points_won_as_loser = master_matches_df.groupby('loserId')['loserTotalPoints'].sum()
    
    total_points_won = points_won_as_winner.add(points_won_as_loser, fill_value=0)

    # --- 2. Calculate Points Lost ---
    # Points lost when winning the match (which is the loser's total points)
    points_lost_as_winner = master_matches_df.groupby('winnerId')['loserTotalPoints'].sum()
    # Points lost when losing the match (which is the winner's total points)
    points_lost_as_loser = master_matches_df.groupby('loserId')['winnerTotalPoints'].sum()
    
    total_points_lost = points_lost_as_winner.add(points_lost_as_loser, fill_value=0)

    # --- 3. Combine and Calculate Stats ---
    point_stats = pd.concat([
        total_points_won.rename('TotalPointsWon'),
        total_points_lost.rename('TotalPointsLost')
    ], axis=1).fillna(0).astype(int)

    point_stats['TotalPointsPlayed'] = point_stats['TotalPointsWon'] + point_stats['TotalPointsLost']
    
    point_stats['PointWinRate'] = (
        (point_stats['TotalPointsWon'] / point_stats['TotalPointsPlayed']) * 100
    ).fillna(0).round(2)

    # --- 4. Format and Rename ---
    point_stats = point_stats.reset_index().rename(columns={'index': 'playerId'})
    
    # Apply the info_string suffix
    point_stats = point_stats.rename(columns={
        'PointWinRate': f"PointWinRate ({info_string})",
        'TotalPointsPlayed': f"TotalPointsPlayed ({info_string})",
        'TotalPointsWon': f"TotalPointsWon ({info_string})",
        'TotalPointsLost': f"TotalPointsLost ({info_string})"
    })

    return point_stats    

def save_winrates(df, info_string, winrates_dir ="../Data/Master/Winrates/" ):

    if (info_string == "") or (not isinstance(info_string, str)) or (info_string.isspace()):
        print (f"❌ Please specify a valid info_string: {info_string} \n❌ File not saved")
        return None 


    info_string = info_string.upper()

    os.makedirs(winrates_dir, exist_ok=True)
    safe_label =info_string.replace(" ", "_")
    date_string = datetime.now().strftime("%Y%m%d")
    winrates_filename = f"{date_string}_winrates_{safe_label}.csv"
    winrates_filepath = os.path.join(winrates_dir, winrates_filename)
    df.to_csv(winrates_filepath, index=False)
    print(f"✅✅Saved master player winrates to {winrates_filepath}")
   

    

def save_winrates(df, info_string, winrates_dir ="../Data/Master/Winrates/" ):

    if (info_string == "") or (not isinstance(info_string, str)) or (info_string.isspace()):
        print (f"❌ Please specify a valid info_string: {info_string} \n❌ File not saved")
        return None 


    info_string = info_string.upper()

    os.makedirs(winrates_dir, exist_ok=True)
    safe_label =info_string.replace(" ", "_")
    date_string = datetime.now().strftime("%Y%m%d")
    winrates_filename = f"{date_string}_winrates_{safe_label}.csv"
    winrates_filepath = os.path.join(winrates_dir, winrates_filename)
    df.to_csv(winrates_filepath, index=False)
    print(f"✅✅Saved master player winrates to {winrates_filepath}")
   