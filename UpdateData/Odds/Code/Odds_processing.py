import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta



def read_files(path='C:/Users/egnke/PythonCode/UFC-Odds/UFC_Final/data/'):
    
    filepath = Path(path)
    filenames = [fname for fname in filepath.iterdir() if fname.is_file() and fname.suffix == '.csv']
    
    data_storage = []
    for fname in filenames:
        df = pd.read_csv(path/fname)
        data_storage.append(df)

    data = pd.concat(data_storage, sort = False)
    data['dates'] = pd.to_datetime(data['dates'], unit = 'ms')

    return data


def filter_odds_based_on_date(df, time_difference=False):

    if time_difference:
        # get time odds quotesd will be taken from. 16 hours before final odd quoted for a UFC card by any site
        df['odds_close_time'] = df.groupby('url')['dates'].transform("max") - timedelta(hours = 16)

    else:
        df['odds_close_time'] = df.groupby('url')['dates'].transform("max")

    df['recent_odds_window']= df['odds_close_time'] - timedelta(days = 7)

    # only consider odds between a week and 16hrs before a fight
    output = df[(df['dates'] <= df['odds_close_time']) & 
            (df['dates'] >= df['recent_odds_window'])]
    
    # take the last date for each bet
    byval = ['fighter1', 'fighter2', 'url', 'Bet', 'betsite', 'dates']
    get_opening_price = output.sort_values(byval).groupby(byval[0:-1]).nth(0).reset_index()
    
    output = output.sort_values(byval).groupby(byval[0:-1]).nth(-1).reset_index()
    output['momentum'] =  (output['odds'] - get_opening_price['odds'])/get_opening_price['odds']
    return output


def check_for_substrings_in_string(string, sub_strings=[]):

    count = 1
    for sub_string in sub_strings:

        if sub_string in string:

            if (count % 2) == 0:
                string = string.replace(sub_string , 'blue_fighter')

            else:
                string = string.replace(sub_string , 'red_fighter')

            return string
            break
            
    
        else:
            count += 1


    return string


def get_second_name(string):
    string = str(string).lower()
    return string.split()[-1]


def clean_string(string):
    return str(string).lower()


def replace_fighters_names_with_generic_fighter_one_or_two(row):

    bet = clean_string(row.Bet)

    fighter_one = clean_string(row.fighter1)
    fighter_two = clean_string(row.fighter2)

    fighter_one_last_name = get_second_name(fighter_one)
    fighter_two_last_name = get_second_name(fighter_two)

    return check_for_substrings_in_string(string=bet, sub_strings=[fighter_one, fighter_two,
                                                                   fighter_one_last_name, fighter_two_last_name])



def pivot_table(df, col, momentum=False):
    
    keepcol = ['fighter1', 'fighter2', 'url', 'odds_close_time']

    df = df.copy()
    if momentum:
        df['bets'] = df['bets'].apply(lambda x: 'momentum ' + x)

    pivoted_df = df[keepcol+[col, 'bets']].pivot_table(values = [ col], columns = ['bets'],
                    index = keepcol,
                    aggfunc='first').reset_index()

    return pivoted_df



def get_columns(pivoted_df, odd_type, col):

    if(odd_type == 'blue_fighter') | (odd_type == 'red_fighter'):
        return pivoted_df[col].columns[pivoted_df[col].columns.str.endswith(odd_type)].to_list()

    else:
        return [col for col in pivoted_df[col].columns if odd_type in col]


def calculate_stats(df):

    df = df.copy()
    mean   =  df.mean(axis=1)
    median =  df.median(axis=1)
    std    =  df.std(axis=1)
    max_   =  df.max(axis=1)

    return mean, median, max_


def get_the_mean_median_and_varience_of_odds(pivoted_df, col):

    df = pivoted_df[['fighter1', 'fighter2', 'url', 'odds_close_time']].copy()

    odd_types = ["blue_fighter", "red_fighter", "over 2½ rounds", "under 2½ rounds",
                "red_fighter wins by decision", "blue_fighter wins by decision", 
                "red_fighter wins by submission", "blue_fighter wins by submission",
                "red_fighter wins by tko/ko", "blue_fighter wins by tko/ko",
                "red_fighter wins in round 1", "red_fighter wins in round 3",
                "red_fighter wins in round 2", "blue_fighter wins in round 3",
                "blue_fighter wins in round 2", "blue_fighter wins in round 1"]
    
    for odd_type in odd_types:
        
        cols_for_odd_type = get_columns(pivoted_df, odd_type=odd_type, col=col)
        subset = pivoted_df[col][cols_for_odd_type].copy()
        
        if col == 'odds':
            df[odd_type + ' mean'], df[odd_type + ' median'], df[odd_type + ' max'] = calculate_stats(subset)

        else:
            df[odd_type + ' mean momentum'], df[odd_type + ' median momentum'], df[odd_type + ' max momentum'] = calculate_stats(subset)

    return df


def bb(x):
    inverted_odds = x**-1
    zz = np.sum(inverted_odds) - 1.0
    return (inverted_odds - zz)/(1-zz)


def convert_negative_american_odds(odds):
    odds = abs(odds)
    if odds != 0:
        return((100/odds)+1)
    else:
        return 0


def convert_positve_american_odds(odds):
    return((odds/100)+1)


def check_if_number_pos_or_neg(number):
  if(number > 0):
    return(True)
  else:
    return(False)


def convert_american_odds_to_decimal(odds):
  if check_if_number_pos_or_neg(odds) == True:
    return(convert_positve_american_odds(odds))
  else:
    return(convert_negative_american_odds(odds))


def convert_to_balanced_book(row, fighter_one_cols, fighter_two_cols):
    
    for fighter_one, fighter_two in zip(fighter_one_cols, fighter_two_cols):
        
        odds_array = np.array([row[fighter_one], row[fighter_two]])
        odds = bb(odds_array)
        row[fighter_one], row[fighter_two] = odds[0], odds[1]

    return row


def find_fighter1_and_fighter2_cols(df):

    subset_cols_one = [col for col in df.columns.to_list() if 'red_fighter' in col]
    subset_cols_two = [col.replace('red_fighter', 'blue_fighter') for col in subset_cols_one]

    return subset_cols_one, subset_cols_two



def get_momentum_columns(df):
    return [col for col in df.columns if 'momentum' in col]



def process_all_odds(path_to_files, output_file):
    
    df = read_files(path=path_to_files)
    df= filter_odds_based_on_date(df,  time_difference=True)
    
    df['Cleaned_Bet'] = df.apply(replace_fighters_names_with_generic_fighter_one_or_two, axis=1)
    df['bets'] = df['betsite'] + ' ' + df['Cleaned_Bet']
    df = df.groupby("bets").filter(lambda x: len(x) > 500)

    pivoted_df_odds = pivot_table(df, 'odds')
    pivoted_df_momentum = pivot_table(df, 'momentum', momentum=True)

    final_df_odds = get_the_mean_median_and_varience_of_odds(pivoted_df_odds, col='odds')
    final_df_odds.columns = final_df_odds.columns.droplevel(1)

    final_df_momentum = get_the_mean_median_and_varience_of_odds(pivoted_df_momentum, col='momentum')
    final_df_momentum.columns = final_df_momentum.columns.droplevel(1)


    fighter_one_cols = ['red_fighter mean', 'red_fighter median']
    fighter_two_cols = ['blue_fighter mean', 'blue_fighter median']
    all_odds = fighter_one_cols + fighter_two_cols

    new_columns = ['Converted_red_fighter mean',  'Converted_red_fighter median',
               'Converted_blue_fighter mean', 'Converted_blue_fighter median']

    final_df_odds[new_columns] = final_df_odds[all_odds].applymap(convert_american_odds_to_decimal)
    final_df_odds = final_df_odds.apply(lambda x: convert_to_balanced_book(x, new_columns[:2] , new_columns[2:]), axis=1)


    subset = get_momentum_columns(final_df_momentum)
    final_df_odds[subset] = final_df_momentum[subset]
    final_df = final_df_odds

    final_df['odds_close_time'] = final_df['odds_close_time'].dt.normalize()
    final_df.rename(columns={'odds_close_time': 'Date'}, inplace=True)
    print(final_df.shape)
    final_df.to_csv(output_file,
                    index=False)

    print('saved')



def process_odds(new_odds, old_odds):

    new_odds['dates'] = pd.to_datetime(new_odds['dates'], unit = 'ms')
    new_odds = filter_odds_based_on_date(new_odds,  time_difference=False)

    new_odds['Cleaned_Bet'] = new_odds.apply(replace_fighters_names_with_generic_fighter_one_or_two, axis=1)
    new_odds['bets'] = new_odds['betsite'] + ' ' + new_odds['Cleaned_Bet']
    #new_odds = new_odds.groupby("bets").filter(lambda x: len(x) > 500)

    pivoted_df_odds = pivot_table(new_odds, 'odds')
    pivoted_df_momentum = pivot_table(new_odds, 'momentum', momentum=True)

    final_df_odds = get_the_mean_median_and_varience_of_odds(pivoted_df_odds, col='odds')
    final_df_odds.columns = final_df_odds.columns.droplevel(1)

    final_df_momentum = get_the_mean_median_and_varience_of_odds(pivoted_df_momentum, col='momentum')
    final_df_momentum.columns = final_df_momentum.columns.droplevel(1)


    fighter_one_cols = ['red_fighter mean', 'red_fighter median']
    fighter_two_cols = ['blue_fighter mean', 'blue_fighter median']
    all_odds = fighter_one_cols + fighter_two_cols

    new_columns = ['Converted_red_fighter mean',  'Converted_red_fighter median',
               'Converted_blue_fighter mean', 'Converted_blue_fighter median']

    final_df_odds[new_columns] = final_df_odds[all_odds].applymap(convert_american_odds_to_decimal)
    final_df_odds = final_df_odds.apply(lambda x: convert_to_balanced_book(x, new_columns[:2] , new_columns[2:]), axis=1)


    subset = get_momentum_columns(final_df_momentum)
    final_df_odds[subset] = final_df_momentum[subset]
    final_df = final_df_odds

    final_df['odds_close_time'] = final_df['odds_close_time'].dt.normalize()
    final_df.rename(columns={'odds_close_time': 'Date'}, inplace=True)


    return final_df[old_odds.columns], pd.concat([final_df[old_odds.columns], old_odds])



