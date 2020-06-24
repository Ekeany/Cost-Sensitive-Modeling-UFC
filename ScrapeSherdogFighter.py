from bs4 import BeautifulSoup
from createdata.print_progress import print_progress
from urllib.request import Request, urlopen
from pathlib import Path
import requests
import datetime
import numpy as np
import pandas as pd
import os


class ScrapeSherdog:


    def __init__(self):

        self.BASE_PATH = Path(os.getcwd())/'data'
        self.filename  = self.BASE_PATH/'fighter_details.csv'
        self.outputfile = self.BASE_PATH/'sherdog_fighter_info.csv'
        self.fighters = self.check_if_fighters_file_exists()
        self.unique_fighters = self.fighters.fighter_name.unique()
        self.run()


    def check_if_fighters_file_exists(self):

        if os.path.exists(self.filename):
            return pd.read_csv(self.filename)

        else:
            raise FileNotFoundError('The fighter_details.csv file was not found ')
    
    
        
    def run(self):

        rows = []
        l = len(self.unique_fighters)
        print_progress(0, l, prefix = 'Progress:', suffix = 'Complete')
        for index, fighter in enumerate(self.unique_fighters):
            row = self.find_fighter_page_and_scrape_data(fighter)
            rows.append(row)
            print_progress(index + 1, l, prefix = 'Progress:', suffix = 'Complete')

        data = pd.DataFrame.from_dict(rows, orient='columns')
        data.to_csv(self.outputfile, index = False)


    
    @staticmethod
    def fetch_url(url):

        """Fetch a url and return it's contents as a string"""

        uf = requests.get(url)
        return uf.text


    @staticmethod
    def get_html(url):

        page = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}))
        soup = BeautifulSoup(page, 'html.parser')
        return soup


    @staticmethod
    def find_links_to_fighters_actual_page(soup):

        # get table where results are
        table =  soup.find('table', {'class':'fightfinder_result'})
        
        # get all the links to fighters pages in table
        fighter_links = list(table.find_all('a', href=True))

        return fighter_links


    @staticmethod
    def find_which_link_of_true_fighter(links, fighter_name):

        for link in links:
            if link.text.lower() == fighter_name.lower():
                link = 'https://www.sherdog.com' + str(link.get('href'))
                break

        return link
    

    def find_fighter_page_and_scrape_data(self, fighter_name):

        fighter_name_search = fighter_name.lower().replace(' ','+')
        search_query = 'https://www.sherdog.com/stats/fightfinder?SearchTxt=' + fighter_name_search + '&weight=&association='
        
        soup = self.get_html(search_query)
        try:
            links = self.find_links_to_fighters_actual_page(soup)
            fighter_url = self.find_which_link_of_true_fighter(links, fighter_name)
            return self.scrape_fighter_data(fighter_url, fighter_name)

        except:
            print(fighter_name + ' was not found on Sherdog.com')
            result = {
                    'name': fighter_name,
                    'birth_date': np.NaN,
                    'locality': np.NaN,
                    'nationality': np.NaN,
                    'height_cm': np.NaN,
                    'weight_kg': np.NaN,
                    'camp_team': np.NaN,
                    'wins': np.NaN,
                    'losses': np.NaN,
                    'draws': np.NaN,
                    'last_fight': np.NaN,
                    }
            return result


    def scrape_fighter_data(self, fighter_url, fighter_name):

        """Retrieve and parse a fighter's details from sherdog.com"""

        # fetch the required url and parse it
        url_content = self.fetch_url(fighter_url)
        soup = BeautifulSoup(url_content, features='lxml')

        # get the fighter's birth date
        try:
            birth_date = soup.find('span', {'itemprop': 'birthDate'}).contents[0]
        except AttributeError:
            birth_date = None
        else:
            if birth_date == 'N/A':
                birth_date = None
            else:
                birth_date = datetime.datetime.strptime(birth_date, '%Y-%m-%d')
                birth_date = birth_date.isoformat()

        # get the fighter's locality
        try:
            locality = soup.find('span', {'itemprop': 'addressLocality'}).contents[0]
        except AttributeError:
            locality = None

        # get the fighter's locality
        try:
            nationality = soup.find('strong', {'itemprop': 'nationality'}).contents[0]
        except AttributeError:
            nationality = None

        # get the fighter's height in CM
        try:
            height_cm = soup.find('span', {'class': 'item height'}).contents[-1].lstrip().rstrip().replace(' cm', '')
        except AttributeError:
            height_cm = None

        # get the fighter's weight in KG
        try:
            weight_kg = soup.find('span', {'class': 'item weight'}).contents[-1].lstrip().rstrip().replace(' kg', '')
        except AttributeError:
            weight_kg = None

        # get the fighter's camp/team
        try:
            camp_team = soup.find('h5', {'class': 'item association'}).strong.span.a.span.contents[0]
        except AttributeError:
            camp_team = None

        wld = {}
        wld['wins'] = 0
        wld['losses'] = 0
        wld['draws'] = 0
        wlds = soup.findAll('span', {'class': 'result'})
        for x in wlds:
            wld[x.contents[0].lower()] = x.findNextSibling('span').contents[0]

        last_fight = soup.find('span', {'class': 'sub_line'}).contents[0]
        last_fight = datetime.datetime.strptime(last_fight, '%b / %d / %Y')
        last_fight = last_fight.isoformat()

        # build a dict with the scraped data and return it
        result = {
            'name': fighter_name,
            'birth_date': birth_date,
            'locality': locality,
            'nationality': nationality,
            'height_cm': height_cm,
            'weight_kg': weight_kg,
            'camp_team': camp_team,
            'wins': wld['wins'],
            'losses': wld['losses'],
            'draws': wld['draws'],
            'last_fight': last_fight,
        }
        return result



ScrapeSherdog()
