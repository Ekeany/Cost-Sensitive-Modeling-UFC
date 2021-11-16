import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from urllib.request import Request, urlopen
import time
import os
from pathlib import Path

from typing import List, Dict, Tuple
from Code.make_soup import make_soup



def get_tapology_fighter_details(link:str) -> Dict[str,str]:

	'''
	This function will take the link to a fighter's tapology page 
	and scrape the fighters attributes.

	-------------------------------------------------
	inputs:
		link string url to the fighters ufc stat page.

	returns:
		dictionary of the fighter's attributes where each key is an attribute
		and the value is it's associated value. 

	'''

	page = urlopen(Request(link, headers={'User-Agent': 'Mozilla/5.0'}))
	soup = BeautifulSoup(page, 'html.parser')

	# get table where results are
	html_list =  soup.find('div', {'class':'details details_two_columns'})

	data = {}
	for ultag in html_list.find_all('ul', {'class': 'clearfix'}):

		for litag in ultag.find_all('li'):
			
			try:
				field = litag.find_all('strong')[-1].get_text().replace('| ','').replace(':','')

			except:
				field = None

			try:
				value = litag.find_all('span')[-1].get_text()
			
			except:
				value = None

			data[field] = value
		
		try:
			data['Date of Birth'] = str(datetime.datetime.strptime(data['Date of Birth'].replace(" ", ""), '%Y.%m.%d'))[:10]

		except:

			data['Date of Birth'] = '1900-20-30'

	return data


def get_ufc_stats_fighter_details(link:str) -> Dict[str, str]:
	
	'''
	This function will take the link to the a fighter ufc stats page 
	and scrape the fighters attributes.

	-------------------------------------------------
	inputs:
		link string url to the fighters ufc stat page.

	returns:
		dictionary of the fighter's attributes where each key is an attribute
		and the value is it's associated value. 

	'''
	another_soup = make_soup(link)
	divs = another_soup.findAll('li', {'class':"b-list__box-list-item b-list__box-list-item_type_block"})
	data = {}
	for i, div in enumerate(divs):

		if i == 5:
			break
		
		column, text = div.text.replace('\n','').split(':')

		data[column.strip().lower()] = text.strip().lower()
		
		
	return data


def google_search(query:str, website:str) -> str:
	
	'''
	This funciton will use google to search for a query and retrive 
	the correct website which we want to retrive.

	--------------------------------------------------
	inputs:
		query: string of the google query

		website: string code for the webiste domain we want from the
			google search

	returns:
		the website url as a string.

	'''
	
	if website=='ufc-stats':
		website_url = 'ufcstats.com/fighter-details/'

	elif website=='tapology':
		website_url = 'https://www.tapology.com/fightcenter/fighters/'

	else:
		raise AttributeError('The webiste you are searching for needs to be specified')


	query = query.replace(' ','%20')
	url = 'https://google.com/search?q='+ query
	
	page = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}))
	soup = BeautifulSoup(page, 'html.parser')

	for link in soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)")):
		
		url = re.split(":(?=http)", link["href"].replace("/url?q=",""))[0]
		
		if website_url in url:
			return url.split('&')[0]


	return None



def scrape_fighter_details(fighter_name:str) -> Dict[str,str]:

	'''
	Given a fighters name this function will create two seperate google
	searches and return the links to both the fighters tapology and ufc stats page.
	It then will scrape both and return the merged dictionaries of both.

	-------------------------------------------------------------
	Inputs:
		fighter_name a string of the name of the fighter wish we 
		want to scrape their details.

	Returns:
		a dictionary that combines the attributes from both websites
		again the key is the attribute and the value is the attribute's
		associated value. Any missing data is filled with Na
	'''

	ufc_stats_search = fighter_name.lower() + ' UFC stats'
	tapology_search  = fighter_name.lower() + ' UFC tapology'
	
	ufc_stat_link = google_search(ufc_stats_search,
								website='ufc-stats')

	tapology_link = google_search(tapology_search,
								website='tapology')

	ufc_stats = get_ufc_stats_fighter_details(ufc_stat_link)
	tapology_stats = get_tapology_fighter_details(tapology_link)

	if ufc_stats is None:

		ufc_stats = {'Height': np.NaN, 
		'Weight': np.NaN,
		'Reach': np.NaN,
		'STANCE': np.NaN,
		'DOB': np.NaN}

	elif tapology_stats is None:

		tapology_stats = {'Given Name': np.NaN,
		'Pro MMA Record': np.NaN, 
		'Nickname': np.NaN, 'Current Streak': np.NaN, 
		'Date of Birth': np.NaN,'Last Fight': np.NaN,
		'Last Weigh-In': np.NaN,'Affiliation': np.NaN,
		'Reach': np.NaN,'Career Disclosed Earnings': np.NaN,
		'Born': np.NaN, 'Fighting out of': np.NaN,
		'Fighter Links': np.NaN, 'Personal Links': np.NaN}


	return dict(tapology_stats, **ufc_stats)



def get_fighter_details(fighters:List[str]) -> pd.DataFrame:

	rows = []
	for fighter in fighters:
		
		try:
			temp_storage = {}
			fighter_details = scrape_fighter_details(fighter)

			temp_storage['fighter_name'] = fighter
			temp_storage['Height'] = fighter_details['height']
			temp_storage['Weight'] = fighter_details['weight']
			temp_storage['Reach'] = fighter_details['reach']
			temp_storage['Stance'] = fighter_details['stance']
			temp_storage['DOB'] = fighter_details['dob']
			temp_storage['Affiliation'] = fighter_details['Affiliation']
			temp_storage['Born'] = fighter_details['Born']
			temp_storage['Fighting out of'] = fighter_details['Fighting out of']

			rows.append(temp_storage)
		
		except:
			print('Exception occured scraping the attributes of ' + str(fighter))



		time.sleep(10)
	
	data = pd.DataFrame.from_dict(rows, orient='columns')

	return data

