from createdata.scrape_fight_links import get_all_links
from createdata.scrape_fight_data import create_fight_data_csv
from createdata.scrape_fighter_details import create_fighter_data_csv


# PAST_EVENT_LINKS_PATH dataframe with name of event and link to webpage
# FUTURE_EVENT_LINKS_PATH is dataframe of the next event and link to webpage
# EVENT_AND_FIGHT_LINKS_PATH dictionary with key being event page and values are links to each fight stat page in event
event_and_fight_links = get_all_links()

'''
event_and_fight_links = {'http://ufcstats.com/event-details/805ad1801eb26abb':
                        ['http://ufcstats.com/fight-details/0005e00b07cee542',
                        'http://ufcstats.com/fight-details/ba6093c9136f99e9',
                        'http://ufcstats.com/fight-details/81b16b26774be5d1',
                        'http://ufcstats.com/fight-details/c00a8682fb5b71bd',
                        'http://ufcstats.com/fight-details/1e7caef3f6dfde10',
                        'http://ufcstats.com/fight-details/24ff0bb908095565',
                        'http://ufcstats.com/fight-details/f4e262b04f4e94bd',
                        'http://ufcstats.com/fight-details/15a422574c3b89e1',
                        'http://ufcstats.com/fight-details/87105c63df95f929', 
                        'http://ufcstats.com/fight-details/ac6b2a5f24c2b8bd', 
                        'http://ufcstats.com/fight-details/d866afa89d62a4ae']}

'''
create_fight_data_csv(event_and_fight_links=event_and_fight_links,
                    filename='total_fight_data.csv')

#create_fighter_data_csv(path_to_past_name_details='C:/Users/egnke/PythonCode/UFC/Cost-Sensitive-Modeling-UFC/data/fighter_details.csv')

