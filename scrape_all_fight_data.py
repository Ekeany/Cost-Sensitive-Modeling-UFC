from createdata.scrape_fight_links import get_all_links
from createdata.scrape_fight_data import create_fight_data_csv
from createdata.scrape_fighter_details import create_fighter_data_csv


# PAST_EVENT_LINKS_PATH dataframe with name of event and link to webpage
# FUTURE_EVENT_LINKS_PATH is dataframe of the next event and link to webpage
# EVENT_AND_FIGHT_LINKS_PATH dictionary with key being event page and values are links to each figh stat page in event
event_and_fight_links = get_all_links()

create_fight_data_csv(event_and_fight_links)

create_fighter_data_csv(path_to_past_name_details='C:/Users/egnke/PythonCode/UFC/Cost-Sensitive-Modeling-UFC/data/fighter_names_and_links.csv')

