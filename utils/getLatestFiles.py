import os
import glob 
import re
from unittest.mock import DEFAULT
import pandas as pd
from typing import Tuple, Optional 

# --- Path Fix: Make all paths absolute from this file's location ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Goes up from /utils to /table_tennis_stats

# Define default paths relative to the project root
DEFAULT_MATCHES_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Matches')
DEFAULT_EVENTS_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Events')
DEFAULT_PLAYERS_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Players')
DEFAULT_WINRATES_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Winrates')
DEFAULT_RATINGS_HISTORY_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Ratings_History')
DEFAULT_RATINGS_SUMMARY_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Ratings_Summary')
DEFAULT_CLEANED_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Processed', 'Cleaned')

# --- Minimal Columns (Must be lists) ---
MINIMAL_MATCH_COLUMNS = ["documentCode"]
MINIMAL_EVENT_COLUMNS = ["EventId"] 
MINIMAL_PLAYER_COLUMNS = ["playerId"]
MINIMAL_COLUMNS = ["playerId"]



def get_data():
    
 
    master_players_df = get_latest_master_players()
    master_events_df = get_latest_master_events()
    master_matches_df = get_latest_master_matches()

    return master_events_df, master_matches_df, master_players_df


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
                             master_regex: str = r'^\d{8}_master_events\.csv$') -> pd.DataFrame:
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
        return pd.DataFrame(columns=MINIMAL_EVENT_COLUMNS) 
    
    files = glob.glob(f"{master_dir}/*.csv")
    
    master_files = []
    
    if not files:
        print(f"❌ No existing *.csv files found in MASTER Events Directory: {master_dir} ")
        return pd.DataFrame(columns=MINIMAL_EVENT_COLUMNS)

    for file in files:
        filename = os.path.basename(file)    
        
        if re.match(master_regex,filename):
            master_files.append(file)

    if not master_files:
        print(f"❌ No existing MASTER files in format: {master_regex} in {master_dir}")
        return pd.DataFrame(columns=MINIMAL_EVENT_COLUMNS)
    
    master_files.sort()    
    latest_master = master_files[-1]

    try: 
        latest_master_df = pd.read_csv(latest_master, low_memory=False)
        print(f"✅ {len(latest_master_df)} events found in latest MASTER: {latest_master} ")
        return latest_master_df
        
    except Exception as e:
        print (f"❌ Error reading lastest MASTER, {latest_master}: {e}")
        return pd.DataFrame(columns=MINIMAL_EVENT_COLUMNS)


def get_latest_master_players(master_dir: str = DEFAULT_PLAYERS_DIR, 
                              master_regex: str = r'^\d{8}_master_players\.csv$') ->pd.DataFrame:
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
        return pd.DataFrame(columns=MINIMAL_PLAYER_COLUMNS)
    
  
    files = glob.glob(f"{master_dir}/*.csv")
    master_players_files = []
    
    if not files:
        print(f"❌ No existing *.csv files found in MASTER Players Directory: {master_dir}") 
        return pd.DataFrame(columns=MINIMAL_PLAYER_COLUMNS)


    for file in files:
        filename = os.path.basename(file)    
        
        if re.match(master_regex, filename):
            master_players_files.append(file)

    if not master_players_files:
        print(f"❌ No existing MASTER files in format: {master_regex} in {master_dir}")
        return pd.DataFrame(columns=MINIMAL_PLAYER_COLUMNS)
    
 
    master_players_files.sort()     
    latest_master_players_file_path = master_players_files[-1]

   
    try: 
        latest_master_players_df = pd.read_csv(latest_master_players_file_path, low_memory=False)
        print(f"✅ {len(latest_master_players_df)} players found in latest MASTER: {latest_master_players_file_path}") 
        return latest_master_players_df
        
    except Exception as e:
        print(f"❌ Error reading latest MASTER player file, {latest_master_players_file_path}: {e}")
        return pd.DataFrame(columns=MINIMAL_PLAYER_COLUMNS)


def get_latest_winrates( info_string:str,
                        master_dir: str = DEFAULT_WINRATES_DIR
                        ) -> pd.DataFrame:

    if (info_string == "") or (not isinstance(info_string, str)) or (info_string.isspace()):
        print (f"❌ Please specify a valid info_string: {info_string} \n❌ File not saved")
        return None 

    files = glob.glob(f"{master_dir}/*.csv")
    winrates_files = []
    
    if not files:
        print(f"❌ No existing *.csv files found in MASTER Winrates Directory: {master_dir}") 
        return pd.DataFrame(columns=MINIMAL_COLUMNS)

    
    for file in files:
        filename = os.path.basename(file)    
        
        if re.match(r'^\d{8}_winrates_.*\.csv$', filename):
            winrates_files.append(file)

    if not winrates_files:
        print(f"❌ No existing MASTER files in format: {r'^\d{8}_winrates_.*\.csv$'} in {master_dir}")
        return pd.DataFrame(columns=MINIMAL_COLUMNS)
    
    safe_label = info_string.upper().replace(' ', '_')
    search_pattern = re.compile(rf'^\d{{8}}_winrates_{re.escape(safe_label)}\.csv$')

    matching_files = [file for file in winrates_files if search_pattern.match(os.path.basename(file))]

    if not matching_files:
        print(f"❌ No existing MASTER files in format: {search_pattern} in {master_dir}")
        return pd.DataFrame(columns=MINIMAL_COLUMNS)

    matching_files.sort()
    latest_winrates = matching_files[-1]

    try: 
        latest_winrates_df = pd.read_csv(latest_winrates, low_memory=False)
        print(f"✅ {len(latest_winrates_df)} winrates found in latest MASTER: {latest_winrates} ")
        return latest_winrates_df
        
    except Exception as e:
        print (f"❌ Error reading lastest MASTER, {latest_winrates}: {e}")
        return pd.DataFrame(columns=MINIMAL_COLUMNS)


def get_latest_ratings_history( info_string:str,
                                 master_dir: str = DEFAULT_RATINGS_HISTORY_DIR
                                ) -> pd.DataFrame:

    if (info_string == "") or (not isinstance(info_string, str)) or (info_string.isspace()):
        print (f"❌ Please specify a valid info_string: {info_string} \n❌ Returning empty DataFrame")
        return pd.DataFrame(columns=MINIMAL_COLUMNS) 

    files = glob.glob(f"{master_dir}/*.csv")
    
    if not files:
        print(f"❌ No existing *.csv files found in MASTER Ratings History Directory: {master_dir}") 
        return pd.DataFrame(columns=MINIMAL_COLUMNS)
    
    safe_label = info_string.upper().replace(' ', '_')
    search_pattern = re.compile(rf'^\d{{8}}_ratings_history_{re.escape(safe_label)}\.csv$')

    matching_files = [file for file in files if search_pattern.match(os.path.basename(file))]

    if not matching_files:
        print(f"❌ No existing MASTER files in format: {search_pattern.pattern} in {master_dir}")
        return pd.DataFrame(columns=MINIMAL_COLUMNS)

    matching_files.sort()
    latest_file = matching_files[-1]

    try: 
        latest_df = pd.read_csv(latest_file, low_memory=False)
        print(f"✅ {len(latest_df)} match history records found in latest MASTER: {latest_file} ")
        return latest_df
        
    except Exception as e:
        print (f"❌ Error reading lastest MASTER, {latest_file}: {e}")
        return pd.DataFrame(columns=MINIMAL_COLUMNS)
    

def get_latest_ratings_summary( info_string:str,
                                master_dir: str = DEFAULT_RATINGS_SUMMARY_DIR
                            ) -> pd.DataFrame:

    if (info_string == "") or (not isinstance(info_string, str)) or (info_string.isspace()):
        print (f"❌ Please specify a valid info_string: {info_string} \n❌ Returning empty DataFrame")
        return pd.DataFrame(columns=MINIMAL_COLUMNS) 

    files = glob.glob(f"{master_dir}/*.csv")

    if not files:
        print(f"❌ No existing *.csv files found in MASTER Ratings Final Directory: {master_dir}") 
        return pd.DataFrame(columns=MINIMAL_COLUMNS)

    safe_label = info_string.upper().replace(' ', '_')
    search_pattern = re.compile(rf'^\d{{8}}_ratings_final_{re.escape(safe_label)}\.csv$')

    matching_files = [file for file in files if search_pattern.match(os.path.basename(file))]

    if not matching_files:
        print(f"❌ No existing MASTER files in format: {search_pattern.pattern} in {master_dir}")
        return pd.DataFrame(columns=MINIMAL_COLUMNS)

    matching_files.sort()
    latest_file = matching_files[-1]

    try: 
        latest_df = pd.read_csv(latest_file, low_memory=False)
        print(f"✅ {len(latest_df)} final ratings found in latest MASTER: {latest_file} ")
        return latest_df
        
    except Exception as e:
        print (f"❌ Error reading lastest MASTER, {latest_file}: {e}")
        return pd.DataFrame(columns=MINIMAL_COLUMNS)

def get_latest_cleaned_matches(cleaned_matches_dir:str = DEFAULT_CLEANED_DIR, 
                               cleaned_matches_regex:str = r'^\d{8}_cleaned_matches\.csv$') ->pd.DataFrame:
    """
    Parses specified directory for cleaned_matches_files in format yyyy_mm_dd. 
    Attempts to read latest file in this format. 

    Args:
        cleaned_matches_dir (str): The folder where the cleaned_matches_files are stored.
        cleaned_matches_regex (str): The pattern to match.

    Returns:
        Optional[pd.DataFrame]: returns DF with data if available, or None if data unavailable or error.
    """
    if not os.path.isdir(cleaned_matches_dir):
        print(f"❌ {cleaned_matches_dir} does not exist as a directory")
        return None 
            
    files = glob.glob(f"{cleaned_matches_dir}/*.csv")
    cleaned_matches_files = []

    for file in files:
        filename = os.path.basename(file)
        
        if re.match(cleaned_matches_regex, filename):
            cleaned_matches_files.append(file)
            # print(f"✅ Found cleaned_matches file: {file}") # Suppressed verbose printing

    if not cleaned_matches_files:
        print(f"❌ No existing cleaned_matches files in format: {cleaned_matches_regex} in {cleaned_matches_dir}")
        return pd.DataFrame(columns=MINIMAL_MATCH_COLUMNS)
    
    cleaned_matches_files.sort()
    latest_cleaned_matches = cleaned_matches_files[-1]

    try: 
        latest_cleaned_matches_df = pd.read_csv(latest_cleaned_matches, low_memory=False)
        print(f"✅ {len(latest_cleaned_matches_df)} matches found in latest cleaned_matches: {latest_cleaned_matches} ")
        return latest_cleaned_matches_df
        
    except Exception as e:
        print (f"❌ Error reading lastest cleaned_matches, {latest_cleaned_matches}: {e}")
        return pd.DataFrame(columns=MINIMAL_MATCH_COLUMNS)