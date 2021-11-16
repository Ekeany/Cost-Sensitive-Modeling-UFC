from Code.scrape_fight_links import get_all_links
from Code.scrape_fight_data import scrape_fight_data_csv
from Code.Scrape_fighter_attributes import get_fighter_details
from io import StringIO
import pandas as pd
import datetime
import os



if __name__ == "__main__":
    
    cwd = os.getcwd()
        
    fight_data_file = 'fight_data.csv'
    fight_data_path = os.path.join(cwd, fight_data_file)


    fighter_data_file = 'fighter_details.csv'
    fighter_data_path = os.path.join(cwd, fighter_data_file)


    # check if fighter details exist as agin we don't need to scrape
    # data that that we already have.
    fighters_with_details = []
    if os.path.isfile(fighter_data_path):
        print('reading fighter details')
        figher_details = pd.read_csv(fighter_data_path)
        fighters_with_details = figher_details.fighter_name.tolist()



    # if fight data exists only need to scrape fights that are missing from
    # the most recent fight until present day:
    if os.path.isfile(fight_data_path):

        print('found existing fight data')
        latest_fight_data = pd.read_csv(fight_data_path)
        most_recent_date = max(pd.to_datetime(latest_fight_data.date))
        print('most recent date event was on: ' + str(most_recent_date))

        print('getting event links')
        event_links, future_events = get_all_links(last_date_from_data=most_recent_date)

        if event_links is not None:

            print('Scraping new fight data')
            data_to_update = scrape_fight_data_csv(event_links)

            
            latest_fight_data = pd.concat([data_to_update, latest_fight_data],
                                           ignore_index=True, sort=False)

            
            print('Saving fight data to ' + str(fight_data_path) + ' ...')
            latest_fight_data.to_csv(fight_data_path, index=False)

            

        all_fighters = latest_fight_data['R_fighter'].tolist() + latest_fight_data['B_fighter'].tolist()
        fighters_without_details = list(set(all_fighters) - set(fighters_with_details))

        

    else:
    
        # need to scrape all the on fight info
        start_date = '01/01/1980'
        start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
        
        print('getting event links')
        event_links, future_events = get_all_links(last_date_from_data=start_date)


        print('Scraping new fight data')
        data_to_update = scrape_fight_data_csv(event_links)
        
 
        print('Saving fight data to ' + str(fight_data_path) + ' ...')
        data_to_update.to_csv(fight_data_path, index=False)

        print('checking for new fighters')
        # get all unique fighters names

        all_fighters = data_to_update['R_fighter'].tolist() + data_to_update['B_fighter'].tolist()
        fighters_without_details = list(set(all_fighters) - set(fighters_with_details))



    if len(fighters_without_details) > 0:
        # need to get the latest date from s3 here
        print('Scraping new fighter details')

        new_fighter_data = get_fighter_details(fighters=list(fighters_without_details))

        if os.path.exists(fighter_data_path):
     
            new_fighter_data = pd.concat([new_fighter_data, figher_details],
                                        ignore_index=True, sort=False)


        print('Save fighter details to ' + str(fighter_data_path) + ' ...')
        new_fighter_data.to_csv(fighter_data_path, index=False)


    print('Finished')







