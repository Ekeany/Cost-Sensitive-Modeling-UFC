from Code.Get_Odds import get_odds
from Code.Get_event_link import get_latest_event_link
from Code.Odds_processing import process_odds
from io import StringIO
import pandas as pd
import boto3



def s3_save_csv(df, bucket_name, filename):

    s3_resource = boto3.resource('s3')
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3_resource.Object(bucket_name, filename).put(Body=csv_buffer.getvalue())


def s3_read_csv(bucket_name, filename):
    
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket= bucket_name, Key= filename) 
    # get object and file (key) from bucket
    df = pd.read_csv(obj['Body'])

    return df


if __name__ == "__main__":

   
    print('Odds Scraper Started: finding link to new event')
    link, event = get_latest_event_link()
    print('Scraping Odds Data for new event ' + str(event) + ' at the following url: ' + str(link))
    
    data = get_odds(link)
    data['odds'] = pd.to_numeric(data['odds'])
    
    print('Finished Scraping')

    print('Saving event data to s3')
    bucket_name = 'ufc-eoghan'
    odds_filename = 'training-data/odds_data/'+ str(event) +'.csv'
    s3_save_csv(data, bucket_name, odds_filename)

    print('Reading the proceesed Odds')
    process_odds_filename = 'training-data/Processed_Odds.csv'
    processed_odds = s3_read_csv(bucket_name, process_odds_filename)
    
    print('Processing new Odds')
    latest_odds, processed_odds = process_odds(data, processed_odds)

    print('Saving Processed New Odds')
    s3_save_csv(processed_odds, bucket_name, process_odds_filename)

    print('Saving Latest Odds Seperatley')
    s3_save_csv(latest_odds, bucket_name, 'training-data/next_fight_odds.csv')
    
