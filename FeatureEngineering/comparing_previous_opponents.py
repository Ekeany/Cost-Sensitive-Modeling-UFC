import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler
from PreProcessing.Imputer import Imputer


def Impute_median(df, cols, group='weight_class'):

    temp = df.copy()
    for col in cols:
        temp[col] = temp.groupby(group)[col].transform(lambda x: x.fillna(x.median()))

    return temp

def Normalize_Features(df):

    df = df.copy()
    cols = ['blue_Fighter_Odds', 'B_Takedown Accuracy',
             'B_age', 'B_RingRust','B_Striking Defense',
             'B_Takedown_Defense','blue_skill',  'striking_blue_skill',
             'wrestling_blue_skill',  'B_Power_Rating',
             'g_and_p_blue_skill', 'jiujitsu_blue_skill',
             'B_Strikes_Absorbed_per_Minute', 'B_AVG_fight_time',
             'red_Fighter_Odds', 'R_Takedown Accuracy',
             'R_age', 'R_RingRust', 'R_Striking Defense',
             'R_Takedown_Defense','red_skill',  'striking_red_skill',
             'wrestling_red_skill',  'R_Power_Rating',
             'g_and_p_red_skill', 'jiujitsu_red_skill',
             'R_Strikes_Absorbed_per_Minute', 'R_AVG_fight_time']

    # Drop col to merge back on
    norm = StandardScaler().fit_transform(df[cols].values)
    df.drop(cols, inplace=True, axis=1)
    
    norm_df = pd.DataFrame(norm, index=df.index, columns=cols)
    norm_df = pd.merge(df, norm_df, left_index=True, right_index=True)
    #imputed_norm_df = Impute_median(norm_df, cols, group='weight_class')
    imputer = Imputer(norm_df)
    cleaned_norm = imputer.impute('bfill')

    second_imputer = Imputer(cleaned_norm)
    cleaned_norm = second_imputer.impute_missing_values()
    
    return cleaned_norm


def get_stats_of_previous_fighters_who_they_beat(df, fighter):

    blue_cols = [df['blue_Fighter_Odds'], df['B_Takedown Accuracy'],
                df['B_age'],   df['B_RingRust'],
                df['B_Striking Defense'], df['B_Takedown_Defense'],
                df['blue_skill'],  df['striking_blue_skill'],
                df['wrestling_blue_skill'],  df['B_Power_Rating'],
                df['g_and_p_blue_skill'], df['jiujitsu_blue_skill'],
                df['B_Strikes_Absorbed_per_Minute'], df['B_AVG_fight_time']]

    red_cols  = [df['red_Fighter_Odds'], df['R_Takedown Accuracy'],
                df['R_age'],   df['R_RingRust'],
                df['R_Striking Defense'], df['R_Takedown_Defense'],
                df['red_skill'],  df['striking_red_skill'],
                df['wrestling_red_skill'],  df['R_Power_Rating'],
                df['g_and_p_red_skill'], df['jiujitsu_red_skill'],
                df['R_Strikes_Absorbed_per_Minute'], df['R_AVG_fight_time']]

    if df.R_fighter == fighter and df.Winner == 'Red':
        beaten, lost_to = blue_cols , ''
    
    elif df.B_fighter == fighter and df.Winner == 'Blue':
        beaten, lost_to = red_cols , ''
        
    elif df.Winner == 'Draw' or df.win_by == 'DQ':
        beaten, lost_to = '',''
    
    elif df.B_fighter == fighter and df.Winner == 'Red':
        beaten, lost_to = '', red_cols

    elif df.R_fighter == fighter and df.Winner == 'Blue':
        beaten, lost_to = '', blue_cols

    else:
        beaten, lost_to = '',''
    
    return(beaten, lost_to)


def calculate_stats_of_previous_fighters_who_they_beat(df, fighter):
    
    overall_beat = []
    overall_lost = []
    df.reset_index(drop=True,inplace=True)
    for row_ in range(len(df)):

        df_slice = df.loc[:row_,:].copy()
        df_slice = df_slice[:-1]
        beat_list = []
        lost_list = []
        for _, row in df_slice.iterrows():
            # store results
            beat, lost_to = get_stats_of_previous_fighters_who_they_beat(row, fighter)

            if len(beat) > 0:
                beat_list.append(beat)
            elif len(lost_to) > 0:
                lost_list.append(lost_to)
            else:
                pass

        overall_beat.append(beat_list)
        overall_lost.append(lost_list)
        

    return(overall_beat, overall_lost)


def get_stats_of_fighters_who_they_have_beaten_or_lost_to(df):

    Red_fighters  = list(df['R_fighter'].values)
    Blue_fighters = list(df['B_fighter'].values)
    All_fighters  = Red_fighters + Blue_fighters

    unique_fighters = list(set(All_fighters))

    fighters = []; rank_indexs  = []
    stats_beaten = []; stats_lost_to = []
    df = df.sort_values(by='date', ascending=True)
    df = Normalize_Features(df)
    for fighter in tqdm(unique_fighters):
        
        fights = df[(df.R_fighter == fighter) | (df.B_fighter == fighter)]
        fighters = fighters + ([fighter] * len(fights))

        rank = fights['date'].rank(ascending=True)
        rank_indexs = rank_indexs + list(rank.index)
        
        beaten, lost_to = calculate_stats_of_previous_fighters_who_they_beat(fights, fighter)
        stats_beaten  = stats_beaten + beaten
        stats_lost_to = stats_lost_to + lost_to

    return pd.DataFrame({'Stats_of_Opponents_they_have_beaten':stats_beaten,
                         'Stats_of_Opponents_they_have_lost_to':stats_lost_to,
                         'Fighters':fighters,
                         'Index':rank_indexs})