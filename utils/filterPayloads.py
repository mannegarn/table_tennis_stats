import os
import glob 
import re
import pandas as pd
from typing import Tuple, Optional, List

# --- Path Fix: Make all paths absolute from this file's location ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Goes up from /utils to /table_tennis_stats


def filter_singles_payloads(raw_payloads_dir: str, output_dir: str, REMOVE_STRINGS: str) -> Tuple[List[int], List[int], List[int], List[int]]:
    """
    Filters raw match payload CSVs to keep only singles matches.
    Here, Teams Matches alongside Singles matches are kept.
    There MAY be cases where a teams match was doubles format (shall be filtered out later)
    Saves filtered singles payloads to the specified output directory.
    Returns lists of event ids: to be used for user checking of results.
    1. success_ids: Events where singles payloads were found
    2. only_doubles_ids: Events with data but no singles matches (e.g only doubles matches)
    3. empty_payload_ids: Events whose payload files contiained no payloads
    4. error_ids: Events where reading the file caused an unexpected error
    """
    
    print("--- 🟠 Filtering Singles Payloads 🟠 ---")
    
    os.makedirs(output_dir, exist_ok= True)
    # get the paths to all raw ppayloads_files
    payloads_files = glob.glob(f"{raw_payloads_dir}/*csv")
    payloads_files.sort()

    success_ids = []
    no_singles_ids = []
    no_data_ids = []
    error_ids = [] 

    pattern = "|".join(REMOVE_STRINGS)

    # loop through each file
    for file in payloads_files:
        
        # get event id from filename, less robust but  (avoids errors if df can not be read)
        event_id = os.path.basename(file).split('_')[0]
        if not event_id.isdigit():
            print(f"SKIPPING file: not in expected naming formnat")
            error_ids.append(event_id)
            continue        

    
        try:
            # get df of the match payloads
            payloads_df = pd.read_csv(file)         

            # filter to select only the singles match paylods 
            remove_mask = payloads_df["subEventType"].str.contains(pattern, na=False, case=False)
            
            singles_payloads_df = payloads_df[~remove_mask].copy()

        
            # If the singles payloads df is not empty, 
            if not singles_payloads_df.empty:
                # get filepath for saving as csv
                filepath = os.path.join(output_dir,f"{event_id}_singles_payloads.csv" )
                singles_payloads_df.to_csv(filepath)
                success_ids.append(event_id)
            else:               
                no_singles_ids.append(event_id)

        # if pandas can't read the empty file, catch the error and add id to to no_data list      
        except pd.errors.EmptyDataError:
            
            no_data_ids.append(event_id)
            continue # Go to the next file

        # catches other unexpected i/o errors.
        except Exception as e: 
            print(f"❌ Error processing event {event_id} ({os.path.basename(file)}): {e}")
            error_ids.append(event_id)
            continue
    
            
    print(f"\n--- ✅ Filtering Complete ---")
    print(f"Successfully processed and saved singles payloads for: {len(success_ids)} events")
    print(f"Events found with ONLY non-singles payloads: {len(no_singles_ids)} events")
    print(f"Events found with EMPTY payload files: {len(no_data_ids)} events")
    if len(error_ids):
        print(f"⚠️ Encountered unexpected errors processing: {len(error_ids)} events") 
        
        
    return success_ids, no_singles_ids, no_data_ids, error_ids           