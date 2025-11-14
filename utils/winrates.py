import pandas as pd


def get_player_winrates(players_df: pd.DataFrame, 
                          master_matches_df: pd.DataFrame, 
                          min_matches: int = 0,
                          info_string: str = '') -> pd.DataFrame:
    """
    Calculates the win rate for every player based on a provided list of matches.

    Args:
        players_df (pd.DataFrame): The master DataFrame of players, containing at least ['playerId', 'playerName'].
        master_matches_df (pd.DataFrame): A DataFrame of all matches to be considered,
                                         containing ['winnerId', 'loserId']. This DataFrame
                                         should be PRE-FILTERED by the user (e.g., by year or event type).
        min_matches (int, optional): The minimum number of total matches required to be included
                                     in the final DataFrame. Defaults to 0.

    Returns:
        pd.DataFrame: The players_df DataFrame, augmented with new columns for
                      TotalWins, TotalLosses, TotalMatches, and WinRate (as a percentage),
                      filtered by min_matches.
    """
    
    
    player_wins = master_matches_df['winnerId'].value_counts()
    
 
    player_losses = master_matches_df['loserId'].value_counts()
    
    win_loss_stats = pd.concat([
        player_wins.rename('TotalWins'), 
        player_losses.rename('TotalLosses')
    ], axis=1)

    # 4. Clean NaN values (for players with 0 wins or 0 losses) and convert to integer
    win_loss_stats['TotalWins'] = win_loss_stats['TotalWins'].fillna(0).astype(int)
    win_loss_stats['TotalLosses'] = win_loss_stats['TotalLosses'].fillna(0).astype(int)
    
    # 5. Calculate TotalMatches and WinRate
    win_loss_stats['TotalMatches'] = win_loss_stats['TotalWins'] + win_loss_stats['TotalLosses']
    
   
    # Calculate as percentage and round
    win_loss_stats['WinRate'] = (
        (win_loss_stats['TotalWins'] / win_loss_stats['TotalMatches']) * 100
    ).fillna(0).round(2)
    
   
    final_winrates_df = players_df.merge(
        win_loss_stats,
        left_on='playerId',
        right_index=True,  # Merge on players_df 'playerId' column and win_loss_stats index
        how='left'
    )   
    
    
    # Define columns that should be Integers
    int_cols = ['TotalWins', 'TotalLosses', 'TotalMatches']
    
    # Fill NaNs with 0 and convert to int for these columns
    final_winrates_df[int_cols] = final_winrates_df[int_cols].fillna(0).astype(int)
    
    # Handle 'WinRate' column separately (fill NaN with 0, and round)
    final_winrates_df['WinRate'] = final_winrates_df['WinRate'].fillna(0).round(2)   

    
    if min_matches > 0:
        final_winrates_df = final_winrates_df[
            final_winrates_df['TotalMatches'] >= min_matches]
 
    # Sort the final filtered data
    final_winrates_df = final_winrates_df.sort_values(by=['WinRate'], ascending=False)
    final_winrates_df = final_winrates_df[["playerId",
                                            "PlayerName",
                                            "CountryName", 
                                            "WinRate", 
                                            "TotalMatches", 
                                            "TotalWins", 
                                            "TotalLosses"]]

    if info_string != '':
        final_winrates_df = final_winrates_df.rename(columns={'WinRate': f"WinRate ({info_string})",
                                        "TotalMatches": f"TotalMatches ({info_string})",
                                        "TotalWins": f"TotalWins ({info_string})",
                                        "TotalLosses": f"TotalLosses ({info_string})"})
    
    return final_winrates_df.reset_index(drop=True)