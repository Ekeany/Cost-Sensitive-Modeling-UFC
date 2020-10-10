import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import numpy as np
import re
from urllib.request import Request, urlopen
import time
import os
from pathlib import Path

from typing import List, Dict, Tuple


def get_data(link):

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



def get_fighter_name_and_details(fighter_name_and_link: Dict[str, List[str]]) -> Dict[str, List[str]]:
	
	fighter_name_and_details = {}
	
	l = len(fighter_name_and_link)
	print('Scraping all fighter data: ')
	print_progress(0, l, prefix = 'Progress:', suffix = 'Complete')
	
	for index, (fighter_name, fighter_url) in enumerate(fighter_name_and_link.items()):
		another_soup = make_soup(fighter_url)
		divs = another_soup.findAll('li', {'class':"b-list__box-list-item b-list__box-list-item_type_block"})
		data = []
		for i, div in enumerate(divs):
			if i == 5:
				break
			data.append(div.text.replace('  ', '').replace('\n', '').replace('Height:', '').replace('Weight:', '')\
	                   .replace('Reach:', '').replace('STANCE:', '').replace('DOB:', ''))
		
		fighter_name_and_details[fighter_name] = data
		print_progress(index + 1, l, prefix = 'Progress:', suffix = 'Complete')
		
	return fighter_name_and_details



def google_search(query):
	
	query = query.replace(' ','%20')
	url = 'https://google.com/search?q='+ query
	
	page = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}))
	soup = BeautifulSoup(page, 'html.parser')

	for link in soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)")):
		
		url = re.split(":(?=http)", link["href"].replace("/url?q=",""))[0]

		if (url.find('https://www.tapology.com/fightcenter/fighters/') != -1):
			return url.split('&')[0]


	return None



'''
need to add stance so need to google search for a ufc stats as well
'''

BASE_PATH = Path(os.getcwd())
outputfile = BASE_PATH/'data/fighter_details_missing_filled.csv'
data = pd.read_csv(BASE_PATH/'data/fighter_details_missing_values.csv')


rows = []
for _ , row in tqdm(data.iterrows()):

	temp = {}
	link = google_search(row['fighter_name'] + ' UFC tapology')

	if link is not None:
		data = get_data(link)

	else:
		data = {'Given Name': None,
				'Pro MMA Record': None, 
				'Nickname': None, 'Current Streak': None, 
				'Date of Birth': None,
				'Last Fight': None, 'Last Weigh-In': None,
				'Affiliation': None, 'Reach': None,
				'Career Disclosed Earnings': None,
				'Born': None, 'Fighting out of': None,
				'Fighter Links': None, 'Personal Links': None}

	try:
		temp['fighter_name'] = row['fighter_name']
		temp['Affiliation'] = data['Affiliation']
		temp['Born'] = data['Born']
		temp['Fighting out of'] = data['Fighting out of']
		temp['Reach'] = data['Reach']
		temp['Date of Birth'] = data['Date of Birth']

	except:
		temp['fighter_name'] = row['fighter_name']
		temp['Affiliation'] = None
		temp['Born'] = None
		temp['Fighting out of'] = None
		temp['Reach'] = None
		temp['Date of Birth'] = None


	rows.append(temp)
	data = pd.DataFrame.from_dict(rows, orient='columns')
	data.to_csv(outputfile, index = False)
	time.sleep(15)

