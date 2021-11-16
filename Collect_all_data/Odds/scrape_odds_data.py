from Code.Get_Odds import get_odds
from Code.Get_Historic_Event_Names_Wiki import get_wiki_links, get_info_about_UFC_event_links
from Code.BestFightOddsEvents import create_get_odds_urls
from Code.Odds_processing import process_odds, process_all_odds
from io import StringIO
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import numpy as np
import os


if __name__ == "__main__":


    root_folder = os.getcwd()
   
    event_name_path = os.path.join(root_folder, 'UFC_event_names.csv')
    event_name_path = Path(event_name_path)

    event_url_path  = os.path.join(root_folder, 'UFC_event_urls.csv')
    event_url_path = Path(event_url_path)
    
    odds_path = os.path.join(root_folder, 'data')
    odds_path = Path(odds_path)

    processed_odds_filename  = 'processed_odds.csv'
    processed_odds_folder = os.path.join(root_folder, processed_odds_filename)


    print('Odds Scraper Started: Scraping all UFC Events from: https://en.wikipedia.org/wiki/List_of_UFC_events')
    links = get_wiki_links()
    events = get_info_about_UFC_event_links(links)
    events.to_csv(event_name_path, index=False)


    print('Updating the Event Url table')
    create_get_odds_urls(event_name_path, event_url_path)
    event_urls = pd.read_csv(event_url_path)


    print('Starting to Scrape Individual Event Odds')
    for i in tqdm(range(len(event_urls))):
        
        if (event_urls['scraped'].iloc[i] != 1):

            if (event_urls['fight_odds_url'].iloc[i] is not np.nan):

                data = get_odds(event_urls['fight_odds_url'].iloc[i])
                data['odds'] = pd.to_numeric(data['odds'])

                event_urls['scraped'].iloc[i] = 1
                filename = event_urls['Events'].iloc[i] + '.csv'
                filepath = os.path.join(odds_path, filename)
                data.to_csv(filepath, index=False)

            else:
                event_urls['scraped'].iloc[i] = 1
    

    print('Finished Scraping')
    event_urls.to_csv(event_url_path, index=False)


    print('Processing new Odds')
    path_to_files = os.path.join(root_folder, 'data')
    processed_odds = process_all_odds(odds_path, processed_odds_folder)

  
       
