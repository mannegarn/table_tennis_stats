import os 
import glob 
import re
import pandas as pd
from typing import List, Tuple, Dict, Any
from datetime import datetime, timezone, timedelta
import numpy as np

# --- Path Definitions ---
# This pattern ensures paths are relative to this file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Goes up one level from /utils
DEFAULT_RAW_EVENTS_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Raw', 'Events') # Assuming raw data input

# --- Default Constants for Functions ---
DEFAULT_REMOVE_STRINGS = ['Youth', 'Junior', 'Para', 'Hopes', 'Veteran']
DEFAULT_AGE_PATTERN = r'U\d{2}' # Matches U11, U13, U15, etc.
DEFAULT_NAME_MAP = {
    'Singles World Cup': 'World Cup',
    'WTTC': 'World Championships'
}

def collate_raw_events (directory: str = DEFAULT_RAW_EVENTS_DIR) -> pd.DataFrame:
    """
    Loads all individual event CSV files from the specified directory and compiles them 
    into a single DataFrame.
    """
    all_events_list = [] 
    # print(f"--- 🟠 Combining Raw Event Files from {directory} 🟠 ---")

    # Use glob to find all CSV files in the directory
    all_files = glob.glob(f"{directory}/*.csv")
    
    if not all_files:
        print(f"❌ Error: No CSV files found in {directory}.")
        # Return blank DataFrame if no data found
        return pd.DataFrame() 

    # Define the pattern to match
    file_pattern = r'^\d{4}_events_raw\.csv$'

    # Iterate through the list of files found by glob
    for file in all_files:
        # Get just the filename for logging
        filename = os.path.basename(file)
        
        # Check if the filename matches the regex pattern
        if re.match(file_pattern, filename):
            # print(f"Reading file: {filename}")

            # read the file, convert to DF, and store in all_events_list container.
            try:
                df = pd.read_csv(file)
                all_events_list.append(df)
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}. Skipping file.")
        else:
            # print(f"Skipping file (does not match pattern): {filename}") # Optional: uncomment for debugging
            pass

    if not all_events_list:
        print(f"❌ Error: No files matching '{file_pattern}' found in {directory}.")
        return pd.DataFrame() 
    
    print (f"--- 🟠 Combined {len(all_events_list)} Raw Event Files from {len(all_events_list)} files (years) in {directory} 🟠 ---")

    all_events_df = pd.concat(all_events_list, ignore_index=True)
    
    # Rename for consistency, as seen in your other processing
    all_events_df.rename(columns={'EventId': 'eventId'}, inplace=True)

    return all_events_df

    
def filter_selected_events(df: pd.DataFrame,
                             remove_strings: List[str] = DEFAULT_REMOVE_STRINGS,
                             age_pattern: str = DEFAULT_AGE_PATTERN
                            ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Filters a dataframe of events data in order to keep only the desired events as specified by the inputs.
    Here: Keeping all standard, senior events. Checks event names and event types for patterns to be removed.
    Returns a tuple of [kept_df, removed_df

    """
    

    print(f"\n--- 🟠 Filtering from {len(df)} Events 🟠 ---")

    # Create a copy of the df for the function scope and remove duplicates from it.
    function_df = df.copy()
    function_df = function_df.drop_duplicates(subset=["eventId"], keep = "first", inplace = False)
    
    # here "|" denotes "OR" for regex pattern. If the event name has any of these terms it will be removed
    string_pattern = "|".join(remove_strings)
    
    # create a mask for conditions to filter the DF - here select all event names with those strings.
    string_mask = (function_df["EventName"].str.contains(string_pattern, case=False, na=False) | 
                   function_df["EventType"].str.contains(string_pattern, case=False, na=False))
                   
    # mask for age using age pattern as defined in config (UXX regex to remove U13, U21 etc)
    age_mask = (function_df["EventName"].str.contains(age_pattern, case=False, na=False) | 
                function_df["EventType"].str.contains(age_pattern, case=False, na=False))
                                                      
    # define a mask to check event name and type for any strings to be removed.
    remove_mask = string_mask | age_mask

    # use filter condition ~mask to select entries that DO NOT contain the filtered patterns.
    kept_df = function_df[~remove_mask].copy() 
    # use filter condition ~mask to select entries that  contain the filtered patterns.
    removed_df = function_df[remove_mask].copy()

    print(f"From total: {len(df)} events , kept: {len(kept_df)}, removed: {len(removed_df)}, duplicates: {len(df) - len(function_df)}") 
    
    return kept_df, removed_df
    

def standardize_event_names(df: pd.DataFrame, name_map: dict = DEFAULT_NAME_MAP) -> pd.DataFrame:
    """
    Changes event names from the original event list to simpler names for Clarity.
    e.g., ['Singles World Cup', "WTTC"] to ["World Cup", "World Championships"]
    
    World Cup (newer, annual) and World Championship (older, biannnual) are often confused.
    Name changes can be specified in name_map variable.
    
    """
    # Use .loc to explicitly change names of input df.
    df["EventType"] = df["EventType"].replace(name_map)
    return df


def convert_dates(df:pd.DataFrame) -> pd.DataFrame:
    """Converts the dates in the events data to pd.datetime objects for easier processing.
    Current format returned by WTT API is (YYYY-MM-DDTHH:MM:SS)
    """
    # create a copy for safety
    working_df = df.copy()
    
    
    working_df['StartDateTime'] = pd.to_datetime(working_df['StartDateTime'])
    working_df['EndDateTime'] = pd.to_datetime(working_df['EndDateTime'])

    return  working_df

def tag_event_status(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a column to flag events that are currently ongoing or in the future.
    completed events , completed = True, future and ongoing events, completed = False
    This uses the Start and End dates from api response. There are fields for rearranged start and end times.
    But these are blank for all relevant events and so only StartDate and EndDate from api will be considered.
    """
    # create a copy for safety and ensure datetimes are used
    working_df = df.copy()
    working_df['EndDateTime'] = pd.to_datetime(working_df['EndDateTime'])
    working_df['StartDateTime'] = pd.to_datetime(working_df['StartDateTime'])
    
    # create utc times for yesterday and tomorrow for one day buffer in the dates
    # this is used as it is not clear what time zone the events data is in 
    now_utc = pd.to_datetime(datetime.now(timezone.utc))
    yesterday_utc = now_utc - timedelta(days=1)
    tomorrow_utc = now_utc + timedelta(days=1)

    yesterday = yesterday_utc.replace(tzinfo=None)
    tomorrow = tomorrow_utc.replace(tzinfo=None)
    now = now_utc.replace(tzinfo=None)
    
    # Tag True if the EndDateTime is in the future relative to 'now'
    working_df['EventStatus'] = np.select(
    # Array of Conditions (checked in order)
    condlist=[
        #  Completed: end time is in past (i.e it completed before yesterday)
        working_df['EndDateTime'] < yesterday,
        
        # Future: if it starts / started  before tomorrow
        working_df['StartDateTime'] > tomorrow,
    ],
    # Array of Corresponding Values
    choicelist=[
        'Completed', 
        'Future',    
    ],
    # Default Value (If neither condition above is met)
    default='Ongoing')
    
    return  working_df