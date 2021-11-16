import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
from urllib.request import urlopen
from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime
from Code.make_soup import make_soup



def clean_string(string:str):
    return " ".join(string.split())


def get_link_of_past_events() -> List[str]:

	links  = []
	events = []
	dates  = []

	all_events_url = 'http://ufcstats.com/statistics/events/completed?page=all'
	soup = make_soup(all_events_url)
	for link in soup.findAll('td',{'class': 'b-statistics__table-col'}):
		
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

	past_events['Date'] = pd.to_datetime(past_events['Date'])

	return past_events


def get_event_and_fight_links(event_links: pd.DataFrame) -> Dict[str, List[str]]:
	
	event_and_fight_links = {}

	for link in event_links.Links.tolist():
		event_fights = []
		soup = make_soup(link)
		for row in soup.findAll('tr', {'class': 'b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click'}):
			href = row.get('data-link')
			event_fights.append(href)
		event_and_fight_links[link] = event_fights

	return event_and_fight_links


def get_all_links(last_date_from_data=datetime) -> Dict[str, List[str]]:

	event_links = get_link_of_past_events()
	current_date = datetime.now()

	future_events = event_links[(event_links['Date'] >= current_date)]
	events_to_scrape = event_links[(event_links['Date'] > last_date_from_data) & 
							  (event_links['Date'] < current_date)]

	if not events_to_scrape.empty:
		event_and_fight_links = get_event_and_fight_links(events_to_scrape)
		return event_and_fight_links, future_events

	else:
		return None, None


