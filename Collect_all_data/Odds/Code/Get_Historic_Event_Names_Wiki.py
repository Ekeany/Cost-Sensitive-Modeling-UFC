import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import random
import pandas as pd


'''
script from https://github.com/inspiration07/UFC-Data-WikipediaScraper/blob/main/UFC%20data%20python%20scraper.ipynb
collects all the names of the UFC events from wikipedia. 
'''

def get_wiki_links():

    #Getting the soup object
    wikiurl = 'https://en.wikipedia.org/'
    url = "https://en.wikipedia.org/wiki/List_of_UFC_events"

    openweb = requests.get(url)
    readweb = openweb.text
    soup = BeautifulSoup(readweb, 'html.parser')
    main_tag = soup.find('table',{"id":"Past_events"})
    tr_tag = main_tag.findAll('td')
    links = []

    #Getting the links of each UFC event till date
    for href in tr_tag:

        try:
            anchor_tags = href.findAll('a')

            for getting_href in anchor_tags:

                link = getting_href.get('href','Yes')
                #print(link)
                if '#cite_note-' in link:
                    link.remove()
                elif 'UFC_Apex' in link:
                    link.remove()
                #elif '#cite_note-' in link:
                # link.remove()
                elif 'UFC_' in link:
                    full_link = urljoin(wikiurl,link)
                    links.append(full_link)

        except:
            continue
    

    return links



def get_info_about_UFC_event_links(links):

    #Finding each html tag and parsing the same with BeautifulSoup
    multi_url = links
    start_time = time.time()
    Promotion = []
    Event = []
    Date = []
    Venue = []
    City = []
    Attendance = []
    Total_Gate = []
    Buyrate = []
    datalist = []

    length = len(links)

    for pages in range(0, length):

        openweb2 = requests.get(multi_url[pages])
        readweb2 = openweb2.text
        soup = BeautifulSoup(readweb2, 'html.parser')
        main_tag = soup.find('table',{'class':'infobox'})
        ultimate_tags = soup.find('th',attrs={'class':'infobox-label'},text='Promotion')
        Date_tags = soup.find('td',attrs={'class':'infobox-data'},text='Ultimate Fighting Championship')
        venue_tags = soup.find('th',attrs={'class':'infobox-label'},text='Venue')
        city_tags = soup.find_all('td',attrs={'class':"infobox-data"})
        attendance_tags = soup.find('th',attrs={'class':'infobox-label'},text='Attendance')
        Total_Gate_tag = soup.find('th',{'class':'infobox-label'},text = 'Total gate')
        Buyrate_tag = soup.find('th',{'class':'infobox-label'},text = 'Buyrate')
        heading_tag = soup.find('h1',{'class':'firstHeading'}).text
    
        
        Event.append(heading_tag)


        try:

            if (ultimate_tags is None) or (not ultimate_tags):
                ultimate_tags = None

            else:
                ultimate_tags=ultimate_tags.find_next('td',attrs={'class':'infobox-data'}).text

            Promotion.append(ultimate_tags)



            if (Date_tags is None) or (not Date_tags):
                Date_tags = None
                
            else:
                Date_tags=Date_tags.find_next('td',attrs={'class':'infobox-data'}).text

            Date.append(Date_tags)


        except:
            pass



        try:

            if (venue_tags is None) or (not venue_tags):
                venue_tags = None

            else:
                venue_tags = venue_tags.find_next('td',attrs={'class':'infobox-data'}).text

            Venue.append(venue_tags)



            if (city_tags is None) or (not city_tags):
                city_tags = None

            else:
                city_tags=city_tags[3].text

            City.append(city_tags)


        except:
            pass



        try:

            if (attendance_tags is None) or (not attendance_tags):
                attendance_tags = None

            else:
                attendance_tags = attendance_tags.find_next('td',attrs={'class':'infobox-data'}).text 
                attendance_tags = attendance_tags.replace('[1]','').replace('[2]','')

            Attendance.append(attendance_tags)


        except:
            pass


        try:

            if (Total_Gate_tag is None) or (not Total_Gate_tag):
                Total_Gate_tag = None

            else:        
                Total_Gate_tag = Total_Gate_tag.find_next('td',attrs={'class':'infobox-data'}).text
                Total_Gate_tag =  Total_Gate_tag.replace('[1]','').replace('[2]','')

            Total_Gate.append(Total_Gate_tag)


        except:
            pass



        try:
            if (Buyrate_tag is None) or (not Buyrate_tag):
                Buyrate_tag = None

            else:
                Buyrate_tag = Buyrate_tag.find_next('td',attrs={'class':'infobox-data'}).text
                Buyrate_tag = Buyrate_tag.replace('[1]','').replace('[2]','')


            Buyrate.append(Buyrate_tag)

        except:
            pass


    #Converting the data into a dictionary 
    data = {'Events':Event, 'Date': Date,'Venue': Venue,
            'City': City,'Attendance':Attendance,
            'Total Gate': Total_Gate,'Buyrate': Buyrate}

    
    return pd.DataFrame(data)



