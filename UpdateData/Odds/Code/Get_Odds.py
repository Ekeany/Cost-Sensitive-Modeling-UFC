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


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


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


def create_firefox_driver():
    
    from selenium.webdriver.firefox.options import Options

    binary = 'C:/Program Files/Mozilla Firefox/firefox.exe'
    executable_path="C:/Users/egnke/PythonCode/UFC-Odds/UFC_Final/code/Web_Scraping/gecko driver/geckodriver.exe"
    options = Options()
    options.headless = True
    options.binary = binary
    cap = DesiredCapabilities().FIREFOX
    cap["marionette"] = True #optional

    driver = webdriver.Firefox(options=options,
                               capabilities=cap,
                               executable_path=executable_path)
    
    return driver



def set_chrome_options():
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


def create_chrome_driver():
	chrome_options = set_chrome_options()
	return webdriver.Chrome(options=chrome_options)


def run_process(url, sleeptime = .01):

    '''
    retrives all odds data including collaspsed java script
    for a given event url from the www.bestfightodds.com
    '''

    driver = create_chrome_driver()
    #driver = create_firefox_driver()

    page = requests.get(url, verify=False)
    driver.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    columns = ['class']+[t.text for t in soup.find_all('table', class_ = 'odds-table')[1].thead.tr.find_all('th')][0:-1]+['meanodds']
    
    rowtable = soup.find_all('table', class_ = 'odds-table')[1].tbody.find_all('tr')

    # loop over betting rows to extract info
    urldfs = []
    date_cell = driver.find_element_by_xpath(xpath_soup(soup.find(class_ = "table-header-date"))) 
    fighter1 = np.nan
    fighter2 = np.nan

    for rownum, row in enumerate(rowtable):  

        #figure out if props bet
        try:
            row_class = row.find('th').find('span').get('class')[0].lower()
        except:
            row_class = None
       
        
        if(rownum % 2 == 0) and (row_class == 't-b-fcc'):
            rowclass = 'even'
        else:
            rowclass = 'odd'

        betname = row.find('th').text
        bets = row.find_all('td')

        if betname.lower() == 'event props':
            break

        if rowclass == 'even':
            fighter1 = betname
            fighter2 = rowtable[rownum + 1].find('th').text
            
            try:
                # open up prop bets
                if "prop-cell prop-cell-exp" in str(bets[-1]):
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

                betid = bet.find('span').get('id')

                # open chart
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
    
    driver.quit()
    data = pd.concat(urldfs)
    data['url'] = url
    return data
        


def get_odds(event_url):
    odds = run_process(event_url, 0.3)
    return odds

