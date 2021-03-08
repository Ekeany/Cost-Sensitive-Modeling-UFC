from Code.scrape_fight_links import get_all_links
from Code.scrape_fight_data import scrape_fight_data_csv
from Code.Scrape_fighter_attributes import get_fighter_details
from io import StringIO
import pandas as pd
import boto3


def s3_read_csv(bucket_name, filename):
    
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket= bucket_name, Key= filename) 
    # get object and file (key) from bucket
    df = pd.read_csv(obj['Body'])

    return df


def s3_save_csv(df, bucket_name, filename):

    s3_resource = boto3.resource('s3')
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3_resource.Object(bucket_name, filename).put(Body=csv_buffer.getvalue())


def find_new_fighters(data_to_update, current_data):
    
    fighters_from_new_fights = set(data_to_update['R_fighter'].tolist() + \
                                   data_to_update['B_fighter'].tolist())

    fighters_from_old_fights = set(current_data['R_fighter'].tolist() + \
                                   current_data['B_fighter'].tolist())

    difference = list(fighters_from_new_fights.difference(fighters_from_old_fights))

    return difference


if __name__ == "__main__":

    bucket_name = 'ufc-eoghan'
    fight_data = 'training-data/total_fight_data.csv'
    fighter_data = 'training-data/complete_fighter_details.csv'
    future_event = 'training-data/future_event.csv'

    # need to get the latest date from s3 here
    print('reading files from s3')
    recent_fight_data = s3_read_csv(bucket_name, fight_data)
    most_recent_date = max(pd.to_datetime(recent_fight_data.date))
    
    print('getting event links')
    event_links, future_events = get_all_links(last_date_from_data=most_recent_date)

    print('saving future event to s3')
    # save future event
    s3_save_csv(future_events, bucket_name, future_event)


    if event_links is not None:

        print('Scraping new fight data')
        data_to_update = scrape_fight_data_csv(event_links)
        latest_fight_data = pd.concat([data_to_update, recent_fight_data],
									   ignore_index=True, sort=False)
        
        print('Updating fight data on s3')
        s3_save_csv(latest_fight_data, bucket_name, fight_data)

        print('checking for new fighters')
        # get all unique fighters names
        new_fighters = find_new_fighters(data_to_update=data_to_update,
                                         current_data=recent_fight_data)

        if len(new_fighters) > 0:
            # need to get the latest date from s3 here
            print('Scraping new fighter details')
            recent_fighter_data = s3_read_csv(bucket_name, fighter_data)

            new_fighter_data = get_fighter_details(fighters=list(new_fighters))
            
            latest_fighter_data = pd.concat([new_fighter_data, recent_fighter_data],
									         ignore_index=True, sort=False)

            print('Updating fighter details on s3')
            s3_save_csv(latest_fighter_data, bucket_name, fighter_data)


    print('Finished')







