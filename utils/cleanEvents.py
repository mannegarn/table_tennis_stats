import pandas as pd
import glob


def filter_by_payloads(shortlist_df: pd.DataFrame, singles_payloads_dir:str) -> pd.DataFrame:
    
    print("--- 🟠 Filtering Events By Payloads 🟠 ---")
    """
    Function is used to further filter down the events_shortlist.
    Only keeping events where valid, non-doubles, match payloads are available.

    Returns a new DF containing these selected events with valid payloads.
    """
    valid_event_ids = []
    payloads_files = glob.glob(f"{singles_payloads_dir}/*csv")
    for file in payloads_files:
        try: 
            payloads_df = pd.read_csv(file)
            event_id = payloads_df["eventId"].iloc[0]
           
            valid_event_ids.append(event_id)
        except Exception as e:
            print (e,file)
   


    mask = shortlist_df["eventId"].isin(valid_event_ids)
    valid_events_df = shortlist_df[mask].copy()
    valid_events_df = valid_events_df.reset_index(drop=True, inplace=False)

    print(f"\n--- ✅ Found {len(valid_events_df)} events with valid payloads ---")
    return valid_events_df    

def resolve_duplicate_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies events with duplicate names and appends the abbreviated month and 
    full year (e.g., 'Oct 2021') from StartDateTime to distinguish them.
    
    Args:
        df (pd.DataFrame): DataFrame containing 'EventName' and 'StartDateTime'.
        
    Returns:
        pd.DataFrame: DataFrame with unique 'EventName' entries.
    """
    
    working_df = df.copy() # Work on a copy for safety

    # 1. Ensure StartDateTime is in datetime format for strftime
    # NOTE: Assuming this has already been done by the convert_dates function prior to this call
    working_df['StartDateTime'] = pd.to_datetime(working_df['StartDateTime']) 

    # 2. Identify duplicate event names
    name_counts = working_df['EventName'].value_counts()
    duplicate_names = name_counts[name_counts > 1].index.tolist()

    # 3. Create a mask for rows that need renaming
    mask = working_df['EventName'].isin(duplicate_names)

    # 4. Apply the transformation using .loc and .apply()
    if not working_df[mask].empty:
        working_df.loc[mask, 'EventName'] = working_df.loc[mask].apply(
            # Format: 'Event Y (Oct 2021)'
            lambda row: f"{row['EventName']} ({row['StartDateTime'].strftime('%b %Y')})",
            axis=1
        )
        print(f"--- ✅ Resolved {len(duplicate_names)} duplicate event names by adding month and year.")
    else:
        print("--- INFO: No event names required disambiguation. ---")

    return working_df