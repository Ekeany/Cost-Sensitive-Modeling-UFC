import requests
from bs4 import BeautifulSoup
import pickle
import os
from pathlib import Path
from urllib.request import urlopen
from typing import List, Dict, Tuple
from createdata.make_soup import make_soup
from tqdm import tqdm
import pandas as pd


ALL_EVENTS_URL = 'http://ufcstats.com/statistics/events/completed?page=all'
BASE_PATH = Path(os.getcwd())/'data'
EVENT_AND_FIGHT_LINKS_PATH = BASE_PATH/'event_and_fight_links.pickle'
PAST_EVENT_LINKS_PATH = BASE_PATH/'past_event_links.pickle'
FUTURE_EVENT_LINKS_PATH = BASE_PATH/'future_event_link.pickle'


def clean_string(string:str):
    return " ".join(string.split())


def pickle_file(the_file, filename):
	pickle_out = open(filename.as_posix(),"wb")
	pickle.dump(the_file, pickle_out)
	pickle_out.close()


def pickle_load(filename):
	pickle_in = open(filename.as_posix(),"rb")
	past_event_links = pickle.load(pickle_in)
	pickle_in.close()
	return past_event_links


def get_link_of_past_events(all_events_url: str=ALL_EVENTS_URL) -> List[str]:

	print('Getting Links of Past Events:')
	links  = []
	events = []
	dates  = []
	soup = make_soup(all_events_url)
	for link in tqdm(soup.findAll('td',{'class': 'b-statistics__table-col'})):
		
		for href in link.findAll('a'):
			foo  = href.get('href')
			bar = clean_string(href.text)

			links.append(foo)
			events.append(bar)

		for date in link.find_all('span', {'class' : 'b-statistics__date'}):
			tmp_date = clean_string(date.get_text())

			dates.append(tmp_date)


	past_events = pd.DataFrame({'Events':events,
								'Links':links,
								'Date':dates})

	future_event = past_events.iloc[[0]]
	past_events  = past_events[1:]

	pickle_file(future_event, FUTURE_EVENT_LINKS_PATH)

	return past_events


def get_event_and_fight_links(event_links: pd.DataFrame) -> Dict[str, List[str]]:
	
	print('Getting event and fight Links')
	event_and_fight_links = {}

	for link in tqdm(event_links.Links.tolist()):
		event_fights = []
		soup = make_soup(link)
		for row in soup.findAll('tr', {'class': 'b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click'}):
			href = row.get('data-link')
			event_fights.append(href)
		event_and_fight_links[link] = event_fights

	pickle_out = open(EVENT_AND_FIGHT_LINKS_PATH.as_posix(),"wb")
	pickle.dump(event_and_fight_links, pickle_out)
	pickle_out.close()

	return event_and_fight_links


def get_the_difference_between_dfs(df1, df2, on='Events'):
    '''
    gets the difference betweeen rows it is not symetric so the most recent or larger df
    should be df1
    '''
    difference = df1.merge(df2, how = 'outer' , on=on, indicator=True)
    difference = difference.loc[difference['_merge'] == 'left_only']

    difference.rename(columns={"Links_x": "Links",
                               "Date_x":'Date'}, inplace=True)
    del difference['Links_y']
    del difference['_merge']
    del difference['Date_y']

    return difference


def get_all_links() -> Dict[str, List[str]]:


	if PAST_EVENT_LINKS_PATH.exists()!= True:
		past_event_links = get_link_of_past_events()
		pickle_file(past_event_links, PAST_EVENT_LINKS_PATH)
		next_event = pd.DataFrame()

	else:
		new_past_event_links = get_link_of_past_events()
		last_past_event_links = pickle_load(PAST_EVENT_LINKS_PATH)
		next_event = get_the_difference_between_dfs(new_past_event_links,
													last_past_event_links,
													on='Events')

		pickle_file(new_past_event_links, PAST_EVENT_LINKS_PATH)
		print(next_event)
	
	if EVENT_AND_FIGHT_LINKS_PATH.exists()!= True:
		# need to either get all new event links or just one 
		event_and_fight_links = get_event_and_fight_links(past_event_links)
		return event_and_fight_links
	
	elif not next_event.empty:
		past_event_and_fight_links = pickle_load(EVENT_AND_FIGHT_LINKS_PATH)
		event_and_fight_links = get_event_and_fight_links(next_event)
		
		updated_event_and_fight_links = {**event_and_fight_links, **past_event_and_fight_links}
		pickle_file(updated_event_and_fight_links, EVENT_AND_FIGHT_LINKS_PATH)

	else:
		event_and_fight_links = None


	return event_and_fight_links

