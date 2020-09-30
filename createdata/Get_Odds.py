import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import os 
import itertools
import time
from itertools import compress
import sys
from pathlib import Path
import pickle


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from tqdm import tqdm



def xpath_soup(element):
    """
    Generate xpath of soup element
    :param element: bs4 text or node
    :return: xpath as string
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        """
        @type parent: bs4.element.Tag
        """
        previous = itertools.islice(parent.children, 0,parent.contents.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)



def run_process(df, already_done_path, 
                executable_path, sleeptime = .01):


    binary = 'C:/Program Files/Mozilla Firefox/firefox.exe'
    options = Options()
    options.headless = True
    options.binary = binary
    cap = DesiredCapabilities().FIREFOX
    cap["marionette"] = True #optional

    driver = webdriver.Firefox(options=options,
                               capabilities=cap,
                               executable_path=executable_path)
    
    urls = df['fight_odds_url']
    event_names = df['Events']

    for event_index in tqdm(range(len(urls))):

            event_name = event_names.iat[event_index]
            url = urls.iat[event_index]
            page = requests.get(url, verify=False)
            driver.get(url)
            soup = BeautifulSoup(page.text, 'lxml')
            columns = ['class']+[t.text for t in soup.find_all('table', class_ = 'odds-table')[1].thead.tr.find_all('th')][0:-1]+['meanodds']
            rowtable = soup.find_all('table', class_ = 'odds-table')[1].tbody.find_all('tr')
    
            #filter to only non prop bets. comment line below if prop bets are needed
            #rowtable = list(compress(rowtable, [row['class'][0]  in ['even', 'odd'] for row in rowtable]))
            # loop over betting rows to extract info
            urldfs = []
            date_cell = driver.find_element_by_xpath(xpath_soup(soup.find(class_ = "table-header-date"))) 
            fighter1 = np.nan
            fighter2 = np.nan

            for rownum, row in enumerate(rowtable):  

                rowclass = row['class'][0]
                betname = row.find('th').text
                bets = row.find_all('td')

                if betname.lower() == 'event props':
                    break
    
                if rowclass == 'even':
                    fighter1 = betname
                    fighter2 = rowtable[rownum + 1].find('th').text
                    
                    try:
                        driver.find_element_by_xpath(xpath_soup(bets[-1])).click()
                    
                    except:
                        pass
                
                
                bets = bets[0:-2]

                # for each bet get the time series
                for index, bet in enumerate(bets):
					#get chart to appear
					#sometimes field is populated with a nonsense value and must be skiped over
                    try:
                        if bet.text == '':
                            continue

                        betid = bet.span.span["id"]
                        driver.find_element_by_id(betid).click()
                        time.sleep(sleeptime)
                        driver.switch_to.active_element

                    except:
                        continue
                    

                    chart_number = driver.find_element_by_id('chart-area').get_attribute('data-highcharts-chart')

                    try:
                        chart_data = driver.execute_script('return Highcharts.charts[' + chart_number + '].series[0].options.data')
                    
                        # pull chart data
                        dates = [None] * len(chart_data)
                        vals = [None] * len(chart_data)
                        for i, point in enumerate(chart_data):
                            e = driver.execute_script('return oneDecToML('+ str(point.get('y')) + ')')
                            dates[i] = point.get('x')
                            vals[i] = e
        
                        celldf = pd.DataFrame({'dates':dates, 'odds':vals, \
                                        'Bet':[betname] * len(chart_data), 'betsite':[columns[2 + index]] * len(chart_data),
                                            'fighter1':[fighter1] * len(chart_data), \
                                                'fighter2':[fighter2]* len(chart_data), 'class':[rowclass]*len(chart_data)},
                                            columns = [ 'Bet', 'betsite', 'dates', 'odds', 'fighter1', 'fighter2', 'class'])
                        urldfs.append(celldf)

                        try:
                            date_cell.click() # make chart disappear so it can't cover up the next cell
                        
                        except:
                            driver.find_element_by_id("search-box1").click()
                    
                    except:
                        pass


            # concatenate the dfs to get all data for this urls
            urldf = pd.concat(urldfs)
            urldf['url'] = url
            event_name_cleaned = re.sub(r"[^A-Za-z0-9_]", "_", event_name)
            urldf.to_csv(already_done_path + "/ordinarybet_datatest_test" + event_name_cleaned + ".csv", index = False)
            urldf.to_csv('C:/Users/egnke/PythonCode/UFC/Cost-Sensitive-Modeling-UFC/data/future_fight_odds.csv', index=False)


def pickle_load(filename):
	pickle_in = open(filename,"rb")
	past_event_links = pickle.load(pickle_in)
	pickle_in.close()
	return past_event_links


def get_odds(event_urls_path,
            already_done_path="C:/Users/egnke/PythonCode/UFC/Cost-Sensitive-Modeling-UFC/data/odds_data",
            executable_path="C:/Users/egnke/PythonCode/UFC-Odds/UFC_Final/code/Web_Scraping/gecko driver/geckodriver.exe"):

    event_urls = pickle_load(event_urls_path)
    event_urls = event_urls.loc[(event_urls['fight_odds_url'].notna()) & (event_urls['fight_odds_url'] != '') , :]

    event_urls['output'] = event_urls['Events'].apply(lambda x: re.sub(r"[^A-Za-z0-9_]", "_", x))
    event_urls['output'] = event_urls['output'].apply(lambda x:"ordinarybet_datatest_test"+x+".csv")

    alreadydone = os.listdir(already_done_path)
    event_urls = event_urls.loc[event_urls['output'].isin(alreadydone) == False  , : ]

    run_process(event_urls, already_done_path,  executable_path, 0.3)


