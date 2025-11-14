import asyncio
import aiohttp
import json
import pandas as pd
from typing import Union, List
import os 

#### Path Definitions (needed for now maybe to do with using notebooks - check this!!!)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Goes up one level from /utils
DEFAULT_EVENTS_DIR = os.path.join(PROJECT_ROOT, 'Data', 'Master', 'Events')

async def get_events_by_year(session: aiohttp.ClientSession, year: Union[int, str]) -> Union[pd.DataFrame, bool]:
    """
    [ASYNC Function used to scrape events via the WTT for a specified year. 
    
    Data available in the API includes all events listed in the ITTF/WTT database including non-WTT events.
    
    Reverse engineered from https://www.worldtabletennis.com/events_calendar]
    
    Args:
        session (aiohttp.ClientSession): The active aiohttp session.
        year (int or str): The year to fetch events for (e.g., 2024).
        
    Returns:
        pd.DataFrame or bool: DataFrame containing all event details for the year, 
                                or False if an error occurs or no data is found.
    """
    
    # Converts the input year to a string if passed as an int.
    year = str(year)
    
    # API endpoint that can return all events listings for a specified year.
    url = 'https://wtt-website-api-prod-3-frontdoor-bddnb2haduafdze9.a01.azurefd.net/api/eventcalendar'

    # Including all headers from the cURL to maximize request fidelity and bypass simple API checks.
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en;q=0.9,es;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://www.worldtabletennis.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.worldtabletennis.com/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',       
        'secapimkey': 'S_WTT_882jjh7basdj91834783mds8j2jsd81', 
        'user-agent': 'Mozilla/5.0 (Linux; Android 11.0; Surface Duo) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36'
    }

    # API requires a custom filter JSON in order to specify the year.
    data = {
        "custom_filter": f"[{{\"name\":\"StartDateTime\",\"value\":{year},\"custom_handling\":\"multimatch_year_or_filter\",\"condition\":\"or_start\"}},{{\"name\":\"FromStartDate\",\"value\":{year},\"custom_handling\":\"multimatch_year_or_filter\",\"condition\":\"or_end\"}}]"
    }

    try:
        # print(f"Fetching events for {year}...") # <-- Suppressed
        # POST request required as JSON payload is expected
        async with session.post(url, headers=headers, json=data) as response:
            # Raise exception for bad status codes (4xx request errors or 5xx server errors)
            response.raise_for_status() 

            response_data = await response.json()
            
            # Response is a dictionary with inside a list.
            events_list = response_data[0].get('rows')

            # Check if data has been returned ana accessed successfully
            if not (events_list and isinstance(events_list, list)):
                # print(f"No event data found for {year}.") # <-- Suppressed
                return False

            # Create DataFrame containing all events listings found and return it.
            df = pd.DataFrame(events_list)
            # print(f"Found {len(df)} events from {year}") # <-- Suppressed
            
            return df

    # except specified errors or other unexpected ones.
    except aiohttp.ClientResponseError as err:
        print(f"❌ HTTP Error: {err.status} {err.message} for year {year}")
    except aiohttp.ContentTypeError:
        print(f"❌ Error: The response for {year} was not valid JSON (likely HTML or empty).")
    except Exception as err:       
        print(f"❌ An unexpected error occurred for {year}: {err}")
    
    return False

async def main_events_scraper(years_to_scrape: List[int], output_dir: str = DEFAULT_EVENTS_DIR):
    """
    Main asynchronous function to coordinate scraping tasks.
    Saves each year's data to a separate CSV file and prints a final summary.
    """
    print("--- 🟢 Commencing Event Scraper 🟢---")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files_count = 0
    total_events_saved = 0 # <-- Added counter for total events
    
    # Create a single session that is reused for all requests
    async with aiohttp.ClientSession() as session:
        # Create a list of tasks (one for each year)
        tasks = [get_events_by_year(session, year) for year in years_to_scrape]
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Process the results
        # Use zip to pair the year with its corresponding result
        for year, df in zip(years_to_scrape, results):
            if isinstance(df, pd.DataFrame):
                # Define the output filename
                filename = os.path.join(output_dir, f"{year}_events_raw.csv")
                
                try:
                    # Save the DataFrame to its own CSV
                    df.to_csv(filename, index=False)
                    # Update counters instead of printing verbose message
                    saved_files_count += 1
                    total_events_saved += len(df)
                except Exception as e:
                    print(f"❌ Failed to save file {filename}: {e}")

    # --- FINAL SUMMARY PRINTING ---
    if saved_files_count > 0:
        print(f"\n--- ✅ Scraping Complete ---")
        print(f"Successfully saved {total_events_saved} events across {saved_files_count} files to {output_dir}")
    else:
        print("\n--- ⚠️ Scraping Complete ---")
        print("No event data was successfully retrieved or saved.")