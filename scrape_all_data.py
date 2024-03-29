from createdata.scrape_fight_links import get_all_links
from createdata.scrape_fight_data import create_fight_data_csv
from createdata.scrape_fighter_details import create_fighter_data_csv
from createdata.ScrapeOdds import ScrapeOdds

event_and_fight_links = get_all_links()

create_fight_data_csv(event_and_fight_links)

create_fighter_data_csv()

scraper = ScrapeOdds()
scraper.run()
