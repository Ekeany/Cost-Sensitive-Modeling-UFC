import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import numpy as np

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options


def make_soup(url: str) -> BeautifulSoup:
    source_code = requests.get(url, allow_redirects=False)
    plain_text = source_code.text.encode('ascii', 'replace')
    return BeautifulSoup(plain_text,'html.parser')


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

        print(totals)
        return np.append(totals, significant_strikes)

    else:
        return array.flatten()


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

    total_fight_stats = np.append(totals,sig_strikes[6:])
    data = np.append(total_fight_stats, data)
    event_info = ';'.join(data)

    return event_info


header: str = 'R_fighter;B_fighter;R_KD;B_KD;R_SIG_STR.;B_SIG_STR.\
;R_SIG_STR_pct;B_SIG_STR_pct;R_TOTAL_STR.;B_TOTAL_STR.;R_TD;B_TD;R_TD_pct\
;B_TD_pct;R_SUB_ATT;B_SUB_ATT;R_PASS;B_PASS;R_REV;B_REV;R_HEAD;B_HEAD;R_BODY\
;B_BODY;R_LEG;B_LEG;R_DISTANCE;B_DISTANCE;R_CLINCH;B_CLINCH;R_GROUND;B_GROUND\
;R_KD_R1;B_KD_R1;R_SIG_STR._R1;B_SIG_STR.\
_R1;R_SIG_STR_pct_R1;B_SIG_STR_pct_R1;R_TOTAL_STR._R1;B_TOTAL_STR._R1;R_TD_R1;B_TD_R1;R_TD_pct\
_R1;B_TD_pct_R1;R_SUB_ATT_R1;B_SUB_ATT_R1;R_PASS_R1;B_PASS_R1;R_REV_R1;B_REV_R1\
;R_KD_R2;B_KD_R2;R_SIG_STR._R2;B_SIG_STR.\
_R2;R_SIG_STR_pct_R2;B_SIG_STR_pct_R2;R_TOTAL_STR._R2;B_TOTAL_STR._R2;R_TD_R2;B_TD_R2;R_TD_pct\
_R2;B_TD_pct_R2;R_SUB_ATT_R2;B_SUB_ATT_R2;R_PASS_R2;B_PASS_R2;R_REV_R2;B_REV_R2\
;R_KD_R3;B_KD_R3;R_SIG_STR._R3;B_SIG_STR.\
_R3;R_SIG_STR_pct_R3;B_SIG_STR_pct_R3;R_TOTAL_STR._R3;B_TOTAL_STR._R3;R_TD_R3;B_TD_R3;R_TD_pct\
_R3;B_TD_pct_R3;R_SUB_ATT_R3;B_SUB_ATT_R3;R_PASS_R3;B_PASS_R3;R_REV_R3;B_REV_R3\
;R_KD_R4;B_KD_R4;R_SIG_STR._R4;B_SIG_STR.\
_R4;R_SIG_STR_pct_R4;B_SIG_STR_pct_R4;R_TOTAL_STR._R4;B_TOTAL_STR._R4;R_TD_R4;B_TD_R4;R_TD_pct\
_R4;B_TD_pct_R4;R_SUB_ATT_R4;B_SUB_ATT_R4;R_PASS_R4;B_PASS_R4;R_REV_R4;B_REV_R4\
;R_KD_R5;B_KD_R5;R_SIG_STR._R5;B_SIG_STR.\
_R5;R_SIG_STR_pct_R5;B_SIG_STR_pct_R5;R_TOTAL_STR._R5;B_TOTAL_STR._R5;R_TD_R5;B_TD_R5;R_TD_pct\
_R5;B_TD_pct_R5;R_SUB_ATT_R5;B_SUB_ATT_R5;R_PASS_R5;B_PASS_R5;R_REV_R5;B_REV_R5\
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
;B_GROUND_STR_RD_5'


URL = 'http://ufcstats.com/fight-details/7c76b3c48a5583df'

driver = create_driver()


def expand_collapsed_items(driver, URL):
    
    driver.get(URL)
    driver.find_element_by_xpath('/html/body/section/div/div/section[3]/a').click()
    driver.find_element_by_xpath('/html/body/section/div/div/section[5]/a').click()
    page_source = driver.page_source
    
    soup = BeautifulSoup(page_source, 'lxml')
    return soup

soup = expand_collapsed_items(driver, URL)
get_round_data(soup)