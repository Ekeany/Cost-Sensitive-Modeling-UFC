import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from typing import 	List, Dict, Tuple
from pathlib import Path
import os
import pandas as pd
import numpy as np
from createdata.print_progress import print_progress
from createdata.make_soup import make_soup
import pickle


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options


HEADER: str = 'R_fighter;B_fighter;R_KD;B_KD;R_SIG_STR.;B_SIG_STR.\
;R_SIG_STR_pct;B_SIG_STR_pct;R_TOTAL_STR.;B_TOTAL_STR.;R_TD;B_TD;R_TD_pct\
;B_TD_pct;R_SUB_ATT;B_SUB_ATT;R_PASS;B_PASS;R_REV;B_REV;R_HEAD;B_HEAD;R_BODY\
;B_BODY;R_LEG;B_LEG;R_DISTANCE;B_DISTANCE;R_CLINCH;B_CLINCH;R_GROUND;B_GROUND\
;R_KD_R1;B_KD_R1;R_SIG_STR._R1;B_SIG_STR._R1;R_SIG_STR_pct_R1;B_SIG_STR_pct_R1\
;R_TOTAL_STR._R1;B_TOTAL_STR._R1;R_TD_R1;B_TD_R1;R_TD_pct_R1;B_TD_pct_R1\
;R_SUB_ATT_R1;B_SUB_ATT_R1;R_PASS_R1;B_PASS_R1;R_REV_R1;B_REV_R1\
	;R_KD_R2;B_KD_R2;R_SIG_STR._R2;B_SIG_STR._R2;R_SIG_STR_pct_R2;B_SIG_STR_pct_R2\
;R_TOTAL_STR._R2;B_TOTAL_STR._R2;R_TD_R2;B_TD_R2;R_TD_pct_R2;B_TD_pct_R2\
;R_SUB_ATT_R2;B_SUB_ATT_R2;R_PASS_R2;B_PASS_R2;R_REV_R2;B_REV_R2\
	;R_KD_R3;B_KD_R3;R_SIG_STR._R3;B_SIG_STR._R3;R_SIG_STR_pct_R3;B_SIG_STR_pct_R3\
;R_TOTAL_STR._R3;B_TOTAL_STR._R3;R_TD_R3;B_TD_R3;R_TD_pct_R3;B_TD_pct_R3\
;R_SUB_ATT_R3;B_SUB_ATT_R3;R_PASS_R3;B_PASS_R3;R_REV_R3;B_REV_R3\
	;R_KD_R4;B_KD_R4;R_SIG_STR._R4;B_SIG_STR._R4;R_SIG_STR_pct_R4;B_SIG_STR_pct_R4\
;R_TOTAL_STR._R4;B_TOTAL_STR._R4;R_TD_R4;B_TD_R4;R_TD_pct_R4;B_TD_pct_R4;R_SUB_ATT_R4\
;B_SUB_ATT_R4;R_PASS_R4;B_PASS_R4;R_REV_R4;B_REV_R4\
	;R_KD_R5;B_KD_R5;R_SIG_STR._R5;B_SIG_STR._R5;R_SIG_STR_pct_R5;B_SIG_STR_pct_R5\
;R_TOTAL_STR._R5;B_TOTAL_STR._R5;R_TD_R5;B_TD_R5;R_TD_pct_R5;B_TD_pct_R5;R_SUB_ATT_R5\
;B_SUB_ATT_R5;R_PASS_R5;B_PASS_R5;R_REV_R5;B_REV_R5\
;R_HEAD_STR_RD_1;B_HEAD_STR_RD_1;R_BODY_STR_RD_1;B_BODY_STR_RD_1;R_LEG_STR_RD_1;B_LEG_STR_RD_1\
;R_DST_STR_RD_1;B_DST_STR_RD_1;R_CLINCH_STR_RD_1;B_CLINCH_STR_RD_1;R_GROUND_STR_RD_1\
;B_GROUND_STR_RD_1\
;R_HEAD_STR_RD_2;B_HEAD_STR_RD_2;R_BODY_STR_RD_2;B_BODY_STR_RD_2;R_LEG_STR_RD_2;B_LEG_STR_RD_2\
;R_DST_STR_RD_2;B_DST_STR_RD_2;R_CLINCH_STR_RD_2;B_CLINCH_STR_RD_2;R_GROUND_STR_RD_2\
;B_GROUND_STR_RD_2\
;R_HEAD_STR_RD_3;B_HEAD_STR_RD_3;R_BODY_STR_RD_3;B_BODY_STR_RD_3;R_LEG_STR_RD_3;B_LEG_STR_RD_3\
;R_DST_STR_RD_3;B_DST_STR_RD_3;R_CLINCH_STR_RD_3;B_CLINCH_STR_RD_3;R_GROUND_STR_RD_3\
;B_GROUND_STR_RD_3\
;R_HEAD_STR_RD_4;B_HEAD_STR_RD_4;R_BODY_STR_RD_4;B_BODY_STR_RD_4;R_LEG_STR_RD_4;B_LEG_STR_RD_4\
;R_DST_STR_RD_4;B_DST_STR_RD_4;R_CLINCH_STR_RD_4;B_CLINCH_STR_RD_4;R_GROUND_STR_RD_4\
;B_GROUND_STR_RD_4\
;R_HEAD_STR_RD_5;B_HEAD_STR_RD_5;R_BODY_STR_RD_5;B_BODY_STR_RD_5;R_LEG_STR_RD_5;B_LEG_STR_RD_5\
;R_DST_STR_RD_5;B_DST_STR_RD_5;R_CLINCH_STR_RD_5;B_CLINCH_STR_RD_5;R_GROUND_STR_RD_5\
;B_GROUND_STR_RD_5\
;win_by;last_round;last_round_time;Format;Referee;date;location;Fight_type;Winner'
	

BASE_PATH = Path(os.getcwd())/'data'


def pad_data(array:np.array):
	'''
	pad data as not every fight goes the distance so we need to 
	add nans for rounds that did not happen.
	'''
	
	length = len(array)
	slice_ = int(length/2)
	# 5 rounds is the max so everyone needs that
	pad_number = (10-length)/2

	totals = np.full((5, 20), np.NaN, dtype='object')
	significant_strikes = np.full((5, 18), np.NaN, dtype='object')
	if pad_number > 0:
		
		total = array[:slice_]
		significant_strike = array[slice_:]
		
		totals[:slice_] = total
		significant_strikes[:slice_] = significant_strike
		# both total and sig strikes contain the first 4 columns no need
		totals = np.delete(totals, np.s_[:2], axis=1)
		significant_strikes = np.delete(significant_strikes, np.s_[:6], axis=1)

		return np.append(totals, significant_strikes)

	else:
		
		array = np.array(array, dtype='object')

		total = np.stack(array[:slice_], axis=0)
		significant_strike = np.stack(array[slice_:], axis=0 )
		
		totals = np.delete(total, np.s_[:2], axis=1)
		significant_strikes = np.delete(significant_strike, np.s_[:6], axis=1)

		return np.append(totals, significant_strikes)



def split_into_sublists(array:list, condition:str) -> np.array:
	'''
	splits the array into sub arrays for each round
	the three pops are for an empty arry at the start and the totals round counts
	are also scraped which are removed for simplicity
	'''
	array = np.array(array)
	arrays = np.split(array, np.where(array[:-1] == condition)[0])
	midpoint = int(len(arrays)/2)

	arrays.pop(0)
	sig_strikes = arrays.pop(midpoint)
	totals  = arrays.pop(0)
	
	return arrays, totals, sig_strikes


def create_driver():
	
	binary = 'C:/Program Files/Mozilla Firefox/firefox.exe'
	executable_path = "C:/Users/egnke/PythonCode/UFC-Odds/UFC_Final/code/Web_Scraping/gecko driver/geckodriver.exe"
	options = Options()
	options.headless = True
	options.binary = binary
	cap = DesiredCapabilities().FIREFOX
	cap["marionette"] = True #optional

	driver = webdriver.Firefox(options=options,
							   capabilities=cap,
							   executable_path=executable_path)

	return driver



def get_round_data(event_soup: BeautifulSoup) -> str:

	columns = ''
	for para in event_soup.findAll('p', {'class': 'b-fight-details__table-text'}):

		if columns == '':
			columns = para.text
		
		else:
			columns = columns + ',' +(para.text.strip())
		

	columns = columns.split(',')
	columns = [value.strip() for value in columns]

	fighter_one = columns[0]
	fighter_two = columns[1]

	data, totals, sig_strikes = split_into_sublists(columns, fighter_one)
	data = list(map(str, pad_data(data)))

	# total fight stats not round data
	total_fight_stats = np.append(totals,sig_strikes[6:])
	data = np.append(total_fight_stats, data)
	event_info = ';'.join(data)

	return event_info


def expand_collapsed_items(driver:webdriver, URL:str) -> BeautifulSoup:
	
	driver.get(URL)
	driver.find_element_by_xpath('/html/body/section/div/div/section[3]/a').click()
	driver.find_element_by_xpath('/html/body/section/div/div/section[5]/a').click()
	page_source = driver.page_source
	
	soup = BeautifulSoup(page_source, 'lxml')
	return soup


def get_fight_stats(fight_soup: BeautifulSoup) -> str:
	tables = fight_soup.findAll('tbody')
	total_fight_data = [tables[0],tables[2]]
	fight_stats = []
	for table in total_fight_data:
		row = table.find('tr')
		stats = ''
		for data in row.findAll('td'):
			if stats == '':
				stats = data.text
			else:    
				stats = stats + ',' + data.text
		fight_stats.append(stats.replace('  ', '').replace('\n\n', '')\
			.replace('\n', ',').replace(', ', ',').replace(' ,',','))
	
	fight_stats[1] = ';'.join(fight_stats[1].split(',')[6:])
	fight_stats[0] = ';'.join(fight_stats[0].split(','))
	fight_stats = ';'.join(fight_stats)
	return fight_stats


def get_fight_details(fight_soup: BeautifulSoup) -> str:
	columns = ''
	for div in fight_soup.findAll('div', {'class':'b-fight-details__content'}):
		for col in div.findAll('p', {'class': 'b-fight-details__text'}):
			if columns == '':
				columns = col.text
			else:
				columns = columns + ',' +(col.text)

	columns = columns.replace('  ', '').replace('\n\n\n\n', ',')\
	.replace('\n', '').replace(', ', ',').replace(' ,',',')\
	.replace('Method: ', '').replace('Round:', '').replace('Time:', '')\
	.replace('Time format:', '').replace('Referee:', '')

	fight_details = ';'.join(columns.split(',')[:5])
	
	return fight_details


def get_event_info(event_soup: BeautifulSoup) -> str:
	event_info = ''
	for info in event_soup.findAll('li', {'class':'b-list__box-list-item'}):
		if event_info == '':
			event_info = (info.text)
		else:
			event_info = event_info + ';' + info.text 
		
	event_info = ';'.join(event_info.replace('Date:','').replace('Location:','')\
		.replace('Attendance:','').replace('\n','').replace('  ', '').split(';')[:2])

	return event_info


def get_fight_result_data(fight_soup: BeautifulSoup) -> str:
	winner = ''
	for div in fight_soup.findAll('div', {'class': 'b-fight-details__person'}):
		if div.find('i', {'class': 
			'b-fight-details__person-status b-fight-details__person-status_style_green'})!=None:
			winner = div.find('h3', {'class':'b-fight-details__person-name'})\
			.text.replace(' \n', '').replace('\n', '')
	
	fight_type = fight_soup.find("i",{"class":"b-fight-details__fight-title"})\
	.text.replace('  ', '').replace('\n', '')
	
	return fight_type + ';' + winner


def get_total_fight_stats(event_and_fight_links: Dict[str, List[str]]) -> str:
	total_stats = ''
	
	l = len(event_and_fight_links)
	print('Scraping all fight data: ')
	print_progress(0, l, prefix = 'Progress:', suffix = 'Complete')

	
	for index, (event,fights) in enumerate(event_and_fight_links.items()):
		event_soup = make_soup(event)
		event_info = get_event_info(event_soup)

		for fight in fights:
			
			try:
				driver = create_driver()
				fight_soup = expand_collapsed_items(driver, fight)
				driver.close()
				driver.quit()

				#fight_stats   = get_fight_stats(fight_soup)
				fight_details = get_fight_details(fight_soup)
				result_data   = get_fight_result_data(fight_soup)
				round_data    = get_round_data(fight_soup)
			
			except:
				print(fight)
				continue
			
			
			total_fight_stats = round_data + ';' + fight_details + ';' + event_info + \
							';' + result_data

			if total_stats == '':
				total_stats = total_fight_stats
			else:
				total_stats = total_stats + '\n' + total_fight_stats


		print_progress(index + 1, l, prefix = 'Progress:', suffix = 'Complete')

	return total_stats


def save_string_to_csv(string, filename, header: str = HEADER):

	with open(filename.as_posix(), 'wb') as file:
			file.write(bytes(header, encoding='ascii', errors='ignore'))
			file.write(bytes(string, encoding='ascii', errors='ignore'))

	return None


def convert_to_structured_data(input_data:str, header:list=HEADER) -> pd.DataFrame:

	structured_data = []
	for row in input_data.split('\n'):
		structured_data.append(row.split(';'))

	return pd.DataFrame(structured_data, columns=HEADER.replace('\n','').split(';'))


def pickle_file(the_file, filename):

	pickle_out = open(filename.as_posix(),"wb")
	pickle.dump(the_file, pickle_out)
	pickle_out.close()



def create_fight_data_csv(event_and_fight_links: Dict[str, List[str]], 
						filename: str = 'total_fight_data.csv') -> None:
	
	CSV_PATH = BASE_PATH/filename

	if CSV_PATH.exists() != True:
		
		total_stats = get_total_fight_stats(event_and_fight_links)
		data = convert_to_structured_data(total_stats)
		data.to_csv(CSV_PATH, index=False)

	elif event_and_fight_links is not None:
		past_fight_data = pd.read_csv(CSV_PATH)
		total_stats = get_total_fight_stats(event_and_fight_links)

		new_fight_data = convert_to_structured_data(total_stats)
		latest_fight_data = pd.concat([new_fight_data, past_fight_data],
									 ignore_index=True, sort=False)

		latest_fight_data.to_csv(CSV_PATH, index=False)

	else:
		pass