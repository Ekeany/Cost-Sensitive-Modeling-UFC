from createdata.BestFightOddsEvents import create_get_odds_urls
from createdata.Get_Odds import get_odds

create_get_odds_urls(filename='bestfightodds_urls.pickle')

get_odds(event_urls_path='C:/Users/egnke/PythonCode/UFC/Cost-Sensitive-Modeling-UFC/data/future_bestfightodds_urls.pickle',
        already_done_path="C:/Users/egnke/PythonCode/UFC/Cost-Sensitive-Modeling-UFC/data/odds_data",
        executable_path="C:/Users/egnke/PythonCode/UFC-Odds/UFC_Final/code/Web_Scraping/gecko driver/geckodriver.exe")