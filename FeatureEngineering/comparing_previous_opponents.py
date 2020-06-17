import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler
from PreProcessing.Imputer import Imputer
from ModelProcessing.GetDifferenceBetweenFighterAttributes import GetTheDifferenceBetweenFighterAttributes


subset_cols = ['R_fighter','B_fighter','date','title_bout', 'win_by','weight_class', 'Average_Odds_f1', 'Average_Odds_f2',
                   'red_fighters_elo','blue_fighters_elo','red_Fighter_Odds','blue_Fighter_Odds','Winner',
                   'R_Fight_Number', 'R_Height_cms', 'R_Reach_cms', 'R_age', 'R_WinLossRatio', 
                   'R_RingRust','R_Winning_Streak','R_Losing_Streak','R_AVG_fight_time','R_total_title_bouts',
                   'R_Takedown_Defense', 'R_Takedown Accuracy','R_Strikes_Per_Minute', 'R_Log_Striking_Ratio' , 'R_Striking Accuracy',
                   'R_Strikes_Absorbed_per_Minute','R_Striking Defense','R_knockdows_per_minute','R_Submission Attempts',
                   'R_Average_Num_Takedowns','R_win_by_Decision_Majority','R_win_by_Decision_Split','R_win_by_Decision_Unanimous',
                   'R_win_by_KO/TKO', 'R_win_by_Submission', 'R_win_by_TKO_Doctor_Stoppage','R_Power_Rating','red_skill',
                   'wrestling_red_skill','striking_red_skill','g_and_p_red_skill', 'jiujitsu_red_skill', 'grappling_red_skill',
                   'R_Log_Striking_Defense', 
                   'B_Fight_Number',
                   'B_Height_cms','B_Reach_cms', 'B_age','B_WinLossRatio','B_RingRust','B_Winning_Streak', 
                   'B_Losing_Streak','B_AVG_fight_time', 'B_total_title_bouts','B_Takedown_Defense', 'B_Takedown Accuracy', 
                   'B_Strikes_Per_Minute','B_Striking Accuracy','B_Log_Striking_Ratio','B_Strikes_Absorbed_per_Minute','B_Striking Defense',
                   'B_knockdows_per_minute','B_Submission Attempts','B_Average_Num_Takedowns','B_win_by_Decision_Majority',
                   'B_win_by_Decision_Split','B_win_by_Decision_Unanimous','B_win_by_KO/TKO','B_win_by_Submission',
                   'B_win_by_TKO_Doctor_Stoppage','B_Power_Rating','blue_skill', 'wrestling_blue_skill', 'striking_blue_skill',
                   'g_and_p_blue_skill', 'jiujitsu_blue_skill', 'grappling_blue_skill',
                   'B_Log_Striking_Defense']

cols_to_keep_whole = ['R_fighter','B_fighter','date', 'Average_Odds_f1', 'Average_Odds_f2',
                    'win_by','weight_class','Winner','R_win_by_Decision_Majority','R_win_by_Decision_Split', 'R_win_by_Decision_Unanimous',
                    'R_win_by_KO/TKO', 'R_win_by_Submission','R_win_by_TKO_Doctor_Stoppage','B_win_by_Decision_Majority',
                    'B_win_by_Decision_Split', 'B_win_by_Decision_Unanimous','B_win_by_KO/TKO', 'B_win_by_Submission',
                    'B_win_by_TKO_Doctor_Stoppage']


def Impute_median(df, cols, group='weight_class'):

    temp = df.copy()
    for col in cols:
        temp[col] = temp.groupby(group)[col].transform(lambda x: x.fillna(x.median()))

    return temp


def BasicFeatureEngineeringFromInferenceInModelBuilding(df, subset_cols, cols_to_keep_whole):

    df = df[subset_cols].copy()

    imputer = Imputer(df)
    cleaned_df = imputer.impute('bfill')

    second_imputer = Imputer(cleaned_df)
    cleaned_df = second_imputer.impute_missing_values()

    difference = GetTheDifferenceBetweenFighterAttributes(cleaned_df)
    difference.get_difference_between_fighters_stats(cols_to_keep_whole=cols_to_keep_whole)
    difference.drop_solo_columns()
    df = difference.get_data()

    return df



def Normalize_Features(df, subset_cols, cols_to_keep_whole):

    df = df.copy()
    cols = ['difference_Fighter_Odds','difference_Log_Striking_Ratio',
    'difference_Log_Striking_Defense', 'difference_age', 'difference_RingRust',
    'striking_difference_skill','difference_fighters_elo','difference_Takedown_Defense',
    'wrestling_difference_skill','difference_Power_Rating','g_and_p_difference_skill',
    'jiujitsu_difference_skill','R_win_by_KO/TKO', 'B_win_by_KO/TKO']


    # get the difference between cols
    df = BasicFeatureEngineeringFromInferenceInModelBuilding(df, subset_cols, cols_to_keep_whole)

    # Drop col to merge back on
    norm = StandardScaler().fit_transform(df[cols].values)
    df.drop(cols, inplace=True, axis=1)
    
    norm_df = pd.DataFrame(norm, index=df.index, columns=cols)
    norm_df = pd.merge(df, norm_df, left_index=True, right_index=True)
    #imputed_norm_df = Impute_median(norm_df, cols, group='weight_class')
    
    return norm_df


def get_stats_of_previous_fighters_who_they_beat(df, fighter):


    blue_cols = [df['difference_Fighter_Odds'], df['difference_Log_Striking_Ratio'],
                df['difference_Log_Striking_Defense'],  df['difference_age'],
                df['difference_RingRust'], df['striking_difference_skill'],
                df['difference_fighters_elo'],  df['difference_Takedown_Defense'],
                df['wrestling_difference_skill'],  df['difference_Power_Rating'],
                df['g_and_p_difference_skill'], df['jiujitsu_difference_skill'],
                df['B_win_by_KO/TKO']]

    red_cols  = [df['difference_Fighter_Odds'], df['difference_Log_Striking_Ratio'],
                df['difference_Log_Striking_Defense'],  df['difference_age'],
                df['difference_RingRust'], df['striking_difference_skill'],
                df['difference_fighters_elo'],  df['difference_Takedown_Defense'],
                df['wrestling_difference_skill'],  df['difference_Power_Rating'],
                df['g_and_p_difference_skill'], df['jiujitsu_difference_skill'],
                df['R_win_by_KO/TKO']]


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
    df = Normalize_Features(df, subset_cols, cols_to_keep_whole)
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