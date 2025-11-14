import os 
import pandas as pd
from typing import List, Union, Tuple, Dict, Any
import asyncio
import aiohttp
import random
import glob
import re
import json
import base64
from tqdm.asyncio import tqdm # For progress bars!

# --- Path Definitions ---
# This pattern ensures paths are relative to this file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Goes up one level from /utils
DEFAULT_PAYLOADS_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Raw', 'Match_payloads')


def get_payloads_to_scrape(events_shortlist: pd.DataFrame, 
                              directory: str = DEFAULT_PAYLOADS_DIR) -> List[str]:
    """
    Compares a list of target eventIds against CSVs already saved in a directory.
    Returns a list of eventIds that do not yet have a corresponding CSV.
    
    Args:
        events_shortlist (pd.DataFrame): DataFrame containing at least an 'eventId' column.
        directory (str): The directory to check for existing files.
        
    Returns:
        List[str]: A list of eventId strings that need to be scraped.
    """
    print("--- 🟠 Reconciling event list with existing payload files... ---")
    
    # 1. Get all event IDs from the master list (as strings)
    try:
        all_event_ids = set(events_shortlist['eventId'].astype(str).unique())
    except KeyError:
        print("❌ Error: 'eventId' column not found in events_shortlist DataFrame.")
        return []
        
    print(f"Total events in master list: {len(all_event_ids)}")

    # 2. Get all event IDs that already exist on disk
    os.makedirs(directory, exist_ok=True) # Ensure directory exists
    all_files = glob.glob(f"{directory}/*.csv")
    
    # Regex to extract the Event ID (any number of digits)
    file_pattern = re.compile(r'^(\d+)_match_payloads\.csv$')
    
    existing_ids = set()
    for file in all_files:
        filename = os.path.basename(file)
        match = file_pattern.match(filename)
        if match:
            event_id_from_file = match.group(1)
            existing_ids.add(event_id_from_file)
            
    print(f"Found {len(existing_ids)} existing payload files in {directory}.")

    # 3. Find the difference
    ids_to_scrape = list(all_event_ids - existing_ids)

    # --- MODIFICATION: Re-scrape 'Ongoing' events ---
    # Get 'Ongoing' event IDs from the shortlist
    ongoing_ids = events_shortlist[events_shortlist['EventStatus'] == 'Ongoing']['eventId'].astype(str).unique()
    
    # Add them to the scrape list (union)
    ids_to_scrape = list(set(ids_to_scrape) | set(ongoing_ids))
    ids_to_scrape.sort()
    # --- END MODIFICATION ---
    
    print(f"🟢 {len(ids_to_scrape)} new/ongoing events to scrape.")
    
    return ids_to_scrape


async def get_match_payloads(session: aiohttp.ClientSession, event_id: Union[int, str]) -> Union[pd.DataFrame, bool]:
    """
    [ASYNC Function] Scrapes all match payloads for a single specified event.
    This is the data needed to get individual match details.

    Args:
        session (aiohttp.ClientSession): The active aiohttp session.
        event_id (int or str): The event id of the event to be scraped.
        
    Returns:
        pd.DataFrame or bool: DataFrame containing all match payloads for this event 
                                (empty DataFrame if no payloads found), 
                                or False if an error occurs.
    """
    event_id = str(event_id)

    # Define API endpoint URL and necessary params + headers.
    url = "https://wttwebsiteprodapi-liveevents.trafficmanager.net/api/cms/GetOfficialResult"
    params = {'EventId': event_id, "DocumentCode": "TTE"}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.worldtabletennis.com/',
        'Origin': 'https://www.worldtabletennis.com',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11.0; Surface Duo) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36',
        'secapimkey': 'S_WTT_882jjh7basdj91834783mds8j2jsd81' # Added this key from your other requests
    }

    await asyncio.sleep(random.uniform(0.5, 1))
    
    try:
        async with session.get(url, params=params, headers=headers, timeout=30) as response:
            response.raise_for_status() 

            response_text = await response.text()
            if 'base64,' in response_text:
                base64_data = response_text.split(',')[1]
                decoded_data = base64.b64decode(base64_data)
                json_string = decoded_data.decode('utf-8-sig')
                payloads_list = json.loads(json_string)
            else:
                payloads_list = json.loads(response_text) 
            
            # --- MODIFICATION: Handle Empty vs. Invalid ---
            if isinstance(payloads_list, list):
                # Success: API returned a list (even if it's empty)
                df = pd.DataFrame(payloads_list)
                return df
            else:
                # API returned valid JSON, but not a list (unexpected format)
                print(f"❌ Error: The response for {event_id} was not a list.")
                return False
            # --- END MODIFICATION ---
            
    except aiohttp.ClientResponseError as err:
        print(f"❌ HTTP Error: {err.status} {err.message} for event {event_id}")
    except (json.JSONDecodeError, aiohttp.ContentTypeError):
        print(f"❌ Error: The response for {event_id} was not valid JSON (likely HTML or empty).")
    except asyncio.TimeoutError as err: # <-- FIX: Changed to asyncio.TimeoutError
        print(f"❌ Timeout Error: {err} for event {event_id}")
    except Exception as err:      
        print(f"❌ An unexpected error occurred for {event_id}: {err}")
    
    return False

async def main_payload_scraper(events_to_scrape: List[Union[int,str]], output_dir: str = DEFAULT_PAYLOADS_DIR):
    """
    Main asynchronous function to coordinate scraping tasks.
    Saves each event's match payloads to a separate CSV file and prints a final summary.
    """
    print("--- 🟢 Commencing Match Payloads Scraper 🟢---")
    
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files_count = 0
    total_payloads_saved = 0 # <-- FIX: Renamed variable
    
    async with aiohttp.ClientSession() as session:
        tasks = [get_match_payloads(session, event) for event in events_to_scrape]
        
        # Use tqdm.asyncio.gather to show a progress bar
        print(f"Scraping {len(tasks)} events...")
        results = await tqdm.gather(*tasks)
        
        empty_events = []
        
        print("\n--- 💾 Processing and saving results... ---")
        # --- FIX: Changed to if/elif ---
        for event_id, df in zip(events_to_scrape, results):
            if df is False:
                # This was an error
                empty_events.append(event_id)
            elif isinstance(df, pd.DataFrame):
                # This is a success (df can be empty or full)
                filename = os.path.join(output_dir, f"{event_id}_match_payloads.csv")
                
                try:
                    df.to_csv(filename, index=False)
                    saved_files_count += 1
                    total_payloads_saved += len(df) # len(df) is 0 for empty DFs
                except Exception as e:
                    print(f"❌ Failed to save file {filename}: {e}")

    # --- FINAL SUMMARY PRINTING ---
    print("Empty or Failed events:", empty_events)
    if saved_files_count > 0:
        print(f"\n--- ✅ Scraping Complete ---")
        print(f"Successfully saved {total_payloads_saved} payloads across {saved_files_count} files to {output_dir}")
    else:
        print("\n--- ⚠️ Scraping Complete ---")
        print("No new match_payloads data was successfully retrieved or saved.")