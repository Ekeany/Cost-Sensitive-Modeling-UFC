from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import pandas as pd

def make_soup(url: str) -> BeautifulSoup:
    source_code = requests.get(url, allow_redirects=False)
    plain_text = source_code.text.encode('ascii', 'replace')
    return BeautifulSoup(plain_text,'html.parser')


def get_latest_event_link():

    base_url = 'https://www.bestfightodds.com'
    soup = make_soup(base_url)

    events = []
    links  = []
    dates  = []
    for table_header in soup.findAll('div',{'class': 'table-header'}):
        
        try:
            event = table_header.find('a').getText().lower()

            if 'ufc' in event:
                events.append(event)
                links.append(table_header.find('a')['href'])
                dates.append(table_header.find('span').text)
        
        except:
            pass

    page_data = pd.DataFrame({'Events':events,
                            'Links':links,
                            'Dates':dates})
                            
    link  = str(page_data['Links'].iloc[0])
    event = str(page_data['Events'].iloc[0])
    
    return base_url + link, event.replace(' ','_')

