import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import urllib.parse
import re
import os
from pathlib import Path
from tqdm import tqdm
import pickle

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_event_urls(events):

    search = events['Events'].apply(lambda x: 'https://www.bestfightodds.com/search?query=' + urllib.parse.quote(x))
    events['Date'] = pd.to_datetime(events['Date'])
    fightodds_url = [''] * events.shape[0]

    for i in tqdm(range(events.shape[0])):  

        date_of_card = events.iloc[i]['Date']
        page = requests.get(search.iloc[i], verify=False)
        soup = BeautifulSoup(page.text, 'lxml')
        

        # skip if no possible matches found
        if soup.find('table') == None or page.text.lower().find("No betting lines available for this event".lower()) != -1:
            search.iloc[i]
            fightodds_url[i] = ''
            continue 
        

        # if query redirects to exact match take query as url
        if soup.find('tr', class_ = 'even')  != None:
            fightodds_url[i] = search.iloc[i]
            continue
            
        
        table = soup.find_all('table', class_ = 'content-list') [-1].find_all('tr')
        final_url = ''
        for p in table:
            if pd.to_datetime(p.find('td').text) == date_of_card:
                final_url = 'https://www.bestfightodds.com'+ p.find_all('td')[1].a['href']
                fightodds_url[i] = final_url
                break
        

        # in some cases time zones cause dates to be off by a day. 
        if final_url == '':
            for p in table:
                if np.abs((pd.to_datetime(p.find('td').text) - date_of_card) / pd.to_timedelta(1, unit='D')) <= 1 :
                    final_url = 'https://www.bestfightodds.com'+ p.find_all('td')[1].a['href']
                    fightodds_url[i] = final_url
                    break
                

    events['fight_odds_url'] =  fightodds_url

    return events



def manually_fill_in_missing_events(events):

    events.loc[events['Events'] == 'UFC Fight Night: Błachowicz vs. Jacaré', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-on-espn-22-blachowicz-vs-jacare-1755'
    events.loc[events['Events'] == 'UFC Fight Night: Błachowicz vs. Santos', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-on-espn-3-blachowicz-vs-santos-1638'
    events.loc[events['Events'] == 'UFC on Fox: Evans vs. Davis', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-on-fox-2-482'
    events.loc[events['Events'] == 'UFC Fight Night: Shields vs. Ellenberger', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-fight-night-25-battle-on-the-bayou-406'
    events.loc[events['Events'] == 'UFC Live: Kongo vs. Barry', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-on-versus-4-379'
    events.loc[events['Events'] == 'UFC Live: Jones vs. Matyushenko', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-on-versus-2-281'
    events.loc[events['Events'] == 'The Ultimate Fighter: Team McGregor vs. Team Faber Finale', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-the-ultimate-fighter-22-finale-edgar-vs-mendes-1011'
    events.loc[events['Events'] == 'The Ultimate Fighter: Heavy Hitters Finale', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-the-ultimate-fighter-28-finale-dos-anjos-vs-usman-1586'
    events.loc[events['Events'] == 'The Ultimate Fighter: American Top Team vs. Blackzilians Finale', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-the-ultimate-fighter-21-finale-ellenberger-vs-thompson-971'
    events.loc[events['Events'] == 'The Ultimate Fighter: Undefeated Finale', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-the-ultimate-fighter-27-finale-tavares-vs-adesanya-1503'
    events.loc[events['Events'] == 'The Ultimate Fighter Latin America 3 Finale: dos Anjos vs. Ferguson', 'fight_odds_url'] = 'https://www.bestfightodds.com/events/ufc-fight-night-98-dos-anjos-vs-ferguson-1164'
    
    return events
        
    
def remove_missing_events(events):
    events = events[~(events.fight_odds_url.isna() | (events.fight_odds_url == ''))]
    return events



def save_file(the_file, filepath):
    the_file.to_csv(filepath, index=False)


def pickle_file(the_file, filename):
	pickle_out = open(filename.as_posix(),"wb")
	pickle.dump(the_file, pickle_out)
	pickle_out.close()



def check_if_event_already_exists(future_events, past_events, on='Events'):
    
    df = future_events.copy()

    if isinstance(df, pd.DataFrame):

        df['Indicator'] = df[on].isin(past_events[on]).astype(int)
        filtered_df = df[df['Indicator'] == 0]
        del filtered_df['Indicator']
        return filtered_df

    else:

        if past_events[on].str.contains(df[on]).any():
            return None
        
        else:
            return df.to_frame()


def pickle_load(filename):
	pickle_in = open(filename.as_posix(),"rb")
	past_event_links = pickle.load(pickle_in)
	pickle_in.close()
	return past_event_links



def create_get_odds_urls(filename: str = 'bestfightodds_urls.pickle') -> None:
    
    BASE_PATH = Path(os.getcwd())/'data'
    # future event
    FUTURE_EVENT_LINKS_PATH = BASE_PATH/'future_event_link.pickle'
    # past events
    PAST_EVENT_LINKS_PATH = BASE_PATH/'past_event_links.pickle'
    
    ODDS_URLS_PATH   = BASE_PATH/filename
    FUTURE_URLS_PATH = BASE_PATH/'future_bestfightodds_urls.pickle'
    
    if ODDS_URLS_PATH.exists() != True:
        
        past_events = pickle_load(PAST_EVENT_LINKS_PATH)
        past_event_odd_urls = get_event_urls(past_events)
        past_event_odd_urls = manually_fill_in_missing_events(past_event_odd_urls)
        pickle_file(past_event_odd_urls, ODDS_URLS_PATH)
        
    elif ODDS_URLS_PATH.exists():
        
        future_events = pickle_load(FUTURE_EVENT_LINKS_PATH)
        past_odds_url = pickle_load(ODDS_URLS_PATH)
        
        filtered_future_events = check_if_event_already_exists(future_events,
                                                               past_odds_url,
                                                               on='Events')

        if(filtered_future_events is not None) | (not filtered_future_events.empty):
            
            future_events_url = get_event_urls(future_events)
            event_url = pd.concat([future_events_url, past_odds_url],
                                   ignore_index=True, sort=False)

            pickle_file(event_url, ODDS_URLS_PATH)
            pickle_file(future_events_url, FUTURE_URLS_PATH)

        else:
            pass