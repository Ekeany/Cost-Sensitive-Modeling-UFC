from bs4 import BeautifulSoup
from createdata.print_progress import print_progress
from urllib.request import Request, urlopen
from pathlib import Path
import datetime
import requests
import datetime
import numpy as np
import pandas as pd
import os
import re
import time
from tqdm import tqdm


class ScrapeTapology:


    def __init__(self):

        self.BASE_PATH = Path(os.getcwd())/'data'
        self.filename  = self.BASE_PATH/'filtered_fighter_details.csv'
        self.outputfile = self.BASE_PATH/'Tapology_fighter_info.csv'
        self.proxies = self.get_proxies()
        self.proxies_index = 0
        self.fighters = self.check_if_fighters_file_exists()
        self.unique_fighters = self.fighters.fighter_name.unique()
        self.fighters = self.check_if_fighters_info_already_collected()
        self.fighters = self.convert_DOB_to_correct_format(self.fighters)
        self.run()


    def check_if_fighters_file_exists(self):

        if os.path.exists(self.filename):
            return pd.read_csv(self.filename)

        else:
            raise FileNotFoundError('The fighter_details.csv file was not found ')

    
    def check_if_fighters_info_already_collected(self):

        if os.path.exists(self.outputfile):
            output = pd.read_csv(self.outputfile)
            already_collected = output['Name'].values
            print('original size:' + str(len(self.fighters)))
            self.fighters = self.fighters[~self.fighters['fighter_name'].isin(already_collected)]
            print('original size:' + str(len(self.fighters)))
            return self.fighters

        else:
            return self.fighters


    @staticmethod
    def get_proxies():

        site = requests.get('https://free-proxy-list.net')
        content = BeautifulSoup(site.text, 'lxml')
        table = content.find('table')
        rows = table.find_all('tr')

        cols = [[col.text for col in row.find_all('td')] for row in rows]

        proxies = []
        for col in cols:

            try:
                if col[4] == 'elite proxy' and col[6] == 'yes':
                    proxies.append('https://' + col[0] + ':' + col[1])

            except:
                pass

        return proxies



    @staticmethod
    def convert_DOB_to_correct_format(df):
        df = df.copy()

        df.DOB = pd.to_datetime(df.DOB)
        df.DOB = df.DOB.apply(lambda x: str(x)[:10])

        return df


   
    def get_html(self, url):

        flag = True
        while flag:

            try:
                time.sleep(10)
                page = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}))
                soup = BeautifulSoup(page, 'html.parser')
                break
            
            except:
                time.sleep(300)

        return soup



    def find_fighter_page_and_scrape_data(self, fighter_name, fighter_dob):

        fighter_name_search = fighter_name.lower().replace(' ','+')
        search_query = 'https://www.tapology.com/search?term=' + fighter_name_search + '&commit=Submit&model%5Bfighters%5D=fightersSearch'

        soup = self.get_html(search_query)
        links = self.find_links_to_fighters_actual_page(soup)

        if links is not None:
            fighter_data = self.find_which_link_of_true_fighter(links, fighter_dob)
        else:
            fighter_data = {'Given Name': None,
                'Pro MMA Record': None, 
                'Nickname': None, 'Current Streak': None, 
                'Date of Birth': None,
                'Last Fight': None, 'Last Weigh-In': None,
                'Affiliation': None, 'Reach': None,
                'Career Disclosed Earnings': None,
                'Born': None, 'Fighting out of': None,
                'Fighter Links': None, 'Personal Links': None}

        return fighter_data


    def run(self):

        rows = []
        for _ , row in tqdm(self.fighters.iterrows()):
            temp = {}
            data = self.find_fighter_page_and_scrape_data(row['fighter_name'], row['DOB'])

            temp['Name'] = row['fighter_name']
            temp['Affiliation'] = data['Affiliation']
            temp['Born'] = data['Born']
            temp['Fighting out of'] = data['Fighting out of']

            rows.append(temp)
            data = pd.DataFrame.from_dict(rows, orient='columns')
            data.to_csv(self.outputfile, index = False)





    @staticmethod
    def find_links_to_fighters_actual_page(soup):
        
        # get table where results are
        table =  soup.find('table', {'class':'fcLeaderboard'})
        
        if table is not None:
            # get all the links to fighters pages in table
            fighter_links = list(table.find_all('a', href=True))

            return fighter_links

        else:
            return None



    def get_data(self, link):

        soup = self.get_html(link)

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



    def find_which_link_of_true_fighter(self, links, fighters_dob):

        for link in links:
            link = 'https://www.tapology.com' + str(link.get('href'))
            data = self.get_data(link)
            if data['Date of Birth'] == fighters_dob:
                return data
                

        return {'Given Name': None,
                'Pro MMA Record': None, 
                'Nickname': None, 'Current Streak': None, 
                'Date of Birth': None,
                'Last Fight': None, 'Last Weigh-In': None,
                'Affiliation': None, 'Reach': None,
                'Career Disclosed Earnings': None,
                'Born': None, 'Fighting out of': None,
                'Fighter Links': None, 'Personal Links': None}


            

ScrapeTapology()   