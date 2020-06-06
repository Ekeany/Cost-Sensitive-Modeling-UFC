import pandas as pd
from createdata.print_progress import print_progress
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from pathlib import Path
import os
import re
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class ScrapeOdds:

    def __init__(self):

        self.BASE_PATH = Path(os.getcwd())/'data'
        self.filename  = self.BASE_PATH/'fighter_details.csv'
        self.Fightersfile = self.BASE_PATH/'raw_fighter_odds.csv'
        self.fighters = self.check_if_fighters_file_exists()
        self.unique_fighters = self.fighters.fighter_name.unique()
        print('Scraping Figter Odds:')


    def check_if_fighters_file_exists(self):

        if os.path.exists(self.filename):
            return pd.read_csv(self.filename)

        else:
            raise FileNotFoundError('The fighter_details.csv file was not found ')

    
    def run(self):

        dataframes_ = []
        l = len(self.unique_fighters)
        print_progress(0, l, prefix = 'Progress:', suffix = 'Complete')
        for index, fighter in enumerate(self.unique_fighters):
            dataframes_.append(self.retrive_odds(fighter))
            print_progress(index + 1, l, prefix = 'Progress:', suffix = 'Complete')
        
        result = pd.concat(dataframes_)
        result['duplicates'] = result.Fighter_one + result.Fighter_two + result.Average_Odds_f2 + result.Average_Odds_f1
        result['duplicates'] = result['duplicates'].apply(lambda x: x.replace(" ", "").replace(".",""))
        result['duplicates'] = result['duplicates'].apply(lambda x: ''.join(sorted(x)))

        result.drop_duplicates(subset='duplicates', keep = "first", inplace = True)
        result.to_csv(self.Fightersfile, index=False)



    def retrive_odds(self, fighter_):

        domain = 'https://www.bestfightodds.com'
        search_domain = 'https://www.bestfightodds.com/search?query='
        search_fighter = search_domain + str(fighter_.replace(' ','+'))


        page = urlopen(Request(search_fighter, headers={'User-Agent': 'Mozilla/5.0'}))
        soup = BeautifulSoup(page, 'html.parser')


        opening_odds  = []
        closing_odds  = []
        average_odds  = []

        fighter_table = soup.find('table', {'class': 'content-list'})
        Text =  [obj.text.strip() for obj in soup.find_all('div',{'id':'page-content'})]
        if fighter_table != None:
            links = fighter_table.find_all('a')
            Page_Odds = urlopen(Request(domain + str(links[0]['href']), headers={'User-Agent': 'Mozilla/5.0'}))
            soup_odds = BeautifulSoup(Page_Odds, 'html.parser')

            odds = soup_odds.find_all('td',{'class':'moneyline'})
            odds = [odd.text.strip().replace('n/a','NaN') for odd in odds]
            odds = ["NaN" if odd == '' else odd for odd in odds]
            opening_odds, closing_odds, average_odds = self.slice_per_(odds,3)
            opening_odds_f1, opening_odds_f2 = self.slice_per_(opening_odds,2)
            closing_odds_f1, closing_odds_f2 = self.slice_per_(closing_odds,2)
            average_odds_f1, average_odds_f2 = self.slice_per_(average_odds,2)


            fighters = soup_odds.find_all('th', {'class':'oppcell'})
            fighter_one, fighter_two = self.slice_per(fighters,2)

            event_and_date = soup_odds.find_all('td',{'class':'item-non-mobile'})
            event, date = self.slice_per(event_and_date,2)

            data = pd.DataFrame({'Fighter_one':fighter_one, 'Fighter_two':fighter_two,
                    'Opening_Odds_f1':opening_odds_f1, 'Closing_Odds_f1': closing_odds_f1,
                    'Average_Odds_f1':average_odds_f1, 'Opening_Odds_f2':opening_odds_f2,
                    'Closing_Odds_f2': closing_odds_f2, 'Average_Odds_f2':average_odds_f2,
                    'Event': event,'Date':date })

            return(data)

        elif re.search('No matching fighters or events found',Text[0]) != None:
            pass
            

        else:
            odds = soup.find_all('td',{'class':'moneyline'})
            odds = [odd.text.strip().replace('n/a','NaN') for odd in odds]
            odds = ["NaN" if odd == '' else odd for odd in odds]
            opening_odds, closing_odds, average_odds = self.slice_per_(odds,3)
            opening_odds_f1, opening_odds_f2 = self.slice_per_(opening_odds,2)
            closing_odds_f1, closing_odds_f2 = self.slice_per_(closing_odds,2)
            average_odds_f1, average_odds_f2 = self.slice_per_(average_odds,2)


            fighters = soup.find_all('th', {'class':'oppcell'})
            fighter_one, fighter_two = self.slice_per(fighters,2)

            event_and_date = soup.find_all('td',{'class':'item-non-mobile'})
            event, date = self.slice_per(event_and_date,2)

            data = pd.DataFrame({'Fighter_one':fighter_one, 'Fighter_two':fighter_two,
                        'Opening_Odds_f1':opening_odds_f1, 'Closing_Odds_f1': closing_odds_f1,
                        'Average_Odds_f1':average_odds_f1, 'Opening_Odds_f2':opening_odds_f2,
                        'Closing_Odds_f2': closing_odds_f2, 'Average_Odds_f2':average_odds_f2,
                        'Event': event,'Date':date })
                        
            return(data)

        
    @staticmethod
    def slice_per(source, step):

        temp = []
        for thing in source:
            temp.append(thing.text.strip())
        return [temp[i::step] for i in range(step)]


    @staticmethod
    def slice_per_(source, step):
        return [source[i::step] for i in range(step)]
    


    
