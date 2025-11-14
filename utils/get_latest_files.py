import os
import glob 
import re
import pandas as pd
from typing import Tuple, Optional 

# --- Path Fix: Make all paths absolute from this file's location ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Goes up from /utils to /table_tennis_stats

# Define default paths relative to the project root
DEFAULT_MATCHES_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Matches')
DEFAULT_EVENTS_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Events')
DEFAULT_PLAYERS_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Players')

# --- Minimal Columns (Must be lists) ---
MINIMAL_MATCH_COLUMNS = ["documentCode"]
MINIMAL_EVENT_COLUMNS = ["EventId"] 
MINIMAL_PLAYER_COLUMNS = ["playerId"]


def get_latest_master_matches(master_matches_dir:str = DEFAULT_MATCHES_DIR,
                                master_matches_regex:str = r'^\d{8}_master_matches\.csv$') -> pd.DataFrame:
    """
    Parses specified directory for matches files in format yyyy_mm_dd. 
    Attempts to read latest file in this format. 

    Args:
        master_matches_dir (str): The folder where the master files are stored.
        master_matches_regex (str): The pattern to match.

    Returns:
        pd.DataFrame: returns DF with data if available or blank df if data unavailable
    """
    
    if not os.path.isdir(master_matches_dir):
        print(f"❌ {master_matches_dir} does not exist as a directory")
        return pd.DataFrame(columns=MINIMAL_MATCH_COLUMNS) 

    files = glob.glob(f"{master_matches_dir}/*.csv")
    
    master_files = []
    
    if not files:
        print(f"❌ No existing *.csv files found in MASTER Matches Directory: {master_matches_dir} ") 
        return pd.DataFrame(columns=MINIMAL_MATCH_COLUMNS) 

    for file in files:
        filename = os.path.basename(file)       
        
        if re.match(master_matches_regex, filename):
            master_files.append(file)

    if not master_files:
        print(f"❌ No existing MASTER files in format: {master_matches_regex} in {master_matches_dir}")
        return pd.DataFrame(columns=MINIMAL_MATCH_COLUMNS) 
 
    master_files.sort()     
    latest_master = master_files[-1]

    try: 
        latest_master_df = pd.read_csv(latest_master, low_memory=False)
        print(f"✅ {len(latest_master_df)} matches found in latest MASTER: {latest_master} ") 
        return latest_master_df
        
    except Exception as e:
        print(f"❌ Error reading lastest MASTER, {latest_master}: {e}")
        return pd.DataFrame(columns=MINIMAL_MATCH_COLUMNS)




def get_latest_master_events(master_dir: str = DEFAULT_EVENTS_DIR, 
                             master_regex: str = r'^\d{8}_master_events\.csv$') -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Parses specified directory for events files in format yyyy_mm_dd. 
    Attempts to read latest file in this format. 

    Args:
        master_dir (str): The folder where the master files are stored.
        master_regex (str): The pattern to match.

    Returns:
        Tuple[pd.DataFrame,Optional[str]]: returns DF with data if available or blank df if data unavailable, and the file path
    """
    if not os.path.isdir(master_dir):
        print (f"❌{master_dir} does not exist as a directory")
        return pd.DataFrame(columns=MINIMAL_EVENT_COLUMNS), None    
    
    files = glob.glob(f"{master_dir}/*.csv")
    
    master_files = []
    
    if not files:
        print(f"❌ No existing *.csv files found in MASTER Events Directory: {master_dir} ")
        return pd.DataFrame(columns=MINIMAL_EVENT_COLUMNS), None 

    for file in files:
        filename = os.path.basename(file)    
        
        if re.match(master_regex,filename):
            master_files.append(file)

    if not master_files:
        print(f"❌ No existing MASTER files in format: {master_regex} in {master_dir}")
        return pd.DataFrame(columns=MINIMAL_EVENT_COLUMNS), None 
    
    master_files.sort()    
    latest_master = master_files[-1]

    try: 
        latest_master_df = pd.read_csv(latest_master, low_memory=False)
        print(f"✅ {len(latest_master_df)} events found in latest MASTER: {latest_master} ")
        return latest_master_df
        
    except Exception as e:
        print (f"❌ Error reading lastest MASTER, {latest_master}: {e}")
        return pd.DataFrame(columns=MINIMAL_EVENT_COLUMNS), None 


def get_latest_master_players(master_dir: str = DEFAULT_PLAYERS_DIR, 
                              master_regex: str = r'^\d{8}_master_players\.csv$') -> Tuple[pd.DataFrame, str]:
    """
    Parses the specified directory for player master files in the format yyyy_mm_dd_master_players.csv.
    Attempts to read the latest file in this format. 

    Args:
        master_dir (str): The folder where the master files are stored.
        master_regex (str): The pattern to match.
    Returns:
        Tuple[pd.DataFrame, str]: A tuple containing the DataFrame and the path to the file found, 
                                  or a blank DataFrame and an empty string on failure.
    """
  
    if not os.path.isdir(master_dir):
        print(f"❌ {master_dir} does not exist as a directory.")
        return pd.DataFrame(columns=MINIMAL_PLAYER_COLUMNS), ""
    
  
    files = glob.glob(f"{master_dir}/*.csv")
    master_players_files = []
    
    if not files:
        print(f"❌ No existing *.csv files found in MASTER Players Directory: {master_dir}") 
        return pd.DataFrame(columns=MINIMAL_PLAYER_COLUMNS), ""


    for file in files:
        filename = os.path.basename(file)    
        
        if re.match(master_regex, filename):
            master_players_files.append(file)

    if not master_players_files:
        print(f"❌ No existing MASTER files in format: {master_regex} in {master_dir}")
        return pd.DataFrame(columns=MINIMAL_PLAYER_COLUMNS), ""
    
 
    master_players_files.sort()     
    latest_master_players_file_path = master_players_files[-1]

   
    try: 
        latest_master_players_df = pd.read_csv(latest_master_players_file_path, low_memory=False)
        print(f"✅ {len(latest_master_players_df)} players found in latest MASTER: {latest_master_players_file_path}") 
        return latest_master_players_df
        
    except Exception as e:
        print(f"❌ Error reading latest MASTER player file, {latest_master_players_file_path}: {e}")
        return pd.DataFrame(columns=MINIMAL_PLAYER_COLUMNS), ""

