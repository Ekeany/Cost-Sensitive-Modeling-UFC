import numpy as np
import pandas as pd
from tqdm import tqdm
from math import log, isnan
from FeatureEngineering.time_utils import Time_difference_days, Time_difference_between_consectuive_dates_in_column


def extract_stats(row, fighter, red_column, blue_column, opponent=False):

    if opponent:

        if row.R_fighter == fighter:
            return(row[blue_column])
        
        elif row.B_fighter == fighter:
            return(row[red_column])

    else:

        if row.R_fighter == fighter:
            return(row[red_column])
        
        elif row.B_fighter == fighter:
            return(row[blue_column])


def list_fighters_attribute(df, fighter, red_column, blue_column):
    values = df.apply(lambda x : extract_stats(x, fighter, red_column, blue_column, opponent=False), axis = 1)
    return(values)


def list_opponent_attributes(df, fighter, red_column, blue_column):
    values = df.apply(lambda x : extract_stats(x, fighter, red_column, blue_column, opponent=True), axis = 1)
    return(values)



def check_if_red_or_blue(df2, fighter, index):
    
    if df2.loc[index,'R_fighter'] == fighter:
        return('Red')
    
    else:
        return('Blue')


def check_if_each_row_is_either_red_or_blue(df,df2):

    blue_or_red = []
    for _, row in df.iterrows():
        blue_or_red.append(check_if_red_or_blue(df2, row['Fighters'], row['Index']))
        
    df['Blue_or_Red'] = blue_or_red
    return(df)


def who_won(df, fighter):

    if df.R_fighter == fighter and df.Winner == 'Red':
        won = 1
    
    elif df.B_fighter == fighter and df.Winner == 'Blue':
        won = 1
        
    elif df.Winner == 'Draw' or df.win_by == 'DQ':
        won = 0.5
    
    else:
        won = 0
    
    return(won)


def streaks_who_won(df, fighter):

    if df.R_fighter == fighter and df.Winner == 'Red':
        won = 1
    
    elif df.B_fighter == fighter and df.Winner == 'Blue':
        won = 1
    
    elif df.Winner == 'Draw' or df.win_by == 'DQ':
        won = 0.5
    else:
        won = -1

    return(won)


def calculate_winLoss(df, fighter):
    
    result  = []
    winLoss = []
    indices   = []
    
    for index, row in df.iterrows():
        # store results
        result.append(who_won(row, fighter))
        # calculate the winLoss ratio and store value for
        # each time iteration
        winLoss.append(sum(result)/len(result))
        indices.append(index)

    return(indices, winLoss)


def check_if_fight_was_finished(df, fighter):

    if df.R_fighter == fighter:
        
        if(df['R_win_by_KO/TKO'] == 1) | (df['R_win_by_Submission'] == 1) | (df['R_win_by_TKO_Doctor_Stoppage'] == 1):
            return 1
        
        else:
            return 0

    elif df.B_fighter == fighter:
        
        if(df['B_win_by_KO/TKO'] == 1) | (df['B_win_by_Submission'] == 1) | (df['B_win_by_TKO_Doctor_Stoppage'] == 1):
            
            return 1
        else:
            return 0
    
    else:
        return 0


def calculate_FinshRatio(df, fighter):
    
    result  = []
    finish_ratio = []
    indices   = []
    
    for index, row in df.iterrows():
        # store results
        result.append(check_if_fight_was_finished(row, fighter))
        # calculate the winLoss ratio and store value for
        # each time iteration
        finish_ratio.append(sum(result)/len(result))
        indices.append(index)

    return(indices, finish_ratio)



def calculate_variance_from_mean_in_odds(df, fighter, red_column ,blue_column):
    
    varience_storage  = [0]
    
    for row in range(1,len(df)):
        
        df_slice = df.loc[:row,:].copy()

        stats = [extract_stats(row_, fighter, red_column, blue_column, opponent=False) for index, row_ in df_slice.iterrows()]
        
        mean = sum(stats[:-1])/len(stats[:-1])
        varience = stats[-1] - mean
        varience_storage.append(varience)

    return varience_storage



def average_odd(df, fighter, red_column ,blue_column):
    
    average_odds_fighter    = [extract_stats(df.iloc[0], fighter, red_column, blue_column, opponent=False)]
    average_odds_opponenet  = [extract_stats(df.iloc[0], fighter, red_column, blue_column, opponent=True)]

    for row in range(1,len(df)):
        
        df_slice = df.loc[:row,:].copy()

        stats_fighter   = [extract_stats(row_, fighter, red_column, blue_column, opponent=False) for index, row_ in df_slice.iterrows()]
        stats_opponenet = [extract_stats(row_, fighter, red_column, blue_column, opponent=True) for index, row_ in df_slice.iterrows()]

        mean_fighter = sum(stats_fighter[:-1])/len(stats_fighter[:-1])
        mean_opponenet = sum(stats_opponenet[:-1])/len(stats_opponenet[:-1])

        average_odds_fighter.append(mean_fighter)
        average_odds_opponenet.append(mean_opponenet)

    return average_odds_fighter, average_odds_opponenet



def which_fighter_won(df, fighter):

    if df.R_fighter == fighter and df.Winner == 'Red':
        won, lost = df.B_fighter, ''
    
    elif df.B_fighter == fighter and df.Winner == 'Blue':
        won, lost = df.R_fighter, ''
        
    elif df.Winner == 'Draw' or df.win_by == 'DQ':
        won, lost = '',''
    
    elif df.B_fighter == fighter and df.Winner == 'Red':
        won, lost = '', df.R_fighter

    elif df.R_fighter == fighter and df.Winner == 'Blue':
        won, lost = '', df.B_fighter
    
    return(won, lost)


def calculate_fighters_beat_and_lost(df, fighter):
    
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
            won, lost = which_fighter_won(row, fighter)

            if len(won) > 0:
                beat_list.append(won)

            elif len(lost) > 0:
                lost_list.append(lost)

            else:
                pass

        overall_beat.append(beat_list)
        overall_lost.append(lost_list)
        

    return(overall_beat, overall_lost)


def calculate_streaks(series):
    
    df = pd.DataFrame({'index':series.index, 'Column': series.values})
    
    sign_ = np.sign(df['Column'])
    s = sign_.groupby((sign_!=sign_.shift()).cumsum()).cumsum()
    newdf = df.assign(u_streak=s.where(s>0, 0.0), d_streak=s.where(s<=0, 0.0).abs())
    
    winning_streak = newdf.u_streak.to_list()
    losing_streak  = newdf.d_streak.to_list()
    return(winning_streak,losing_streak)


def remove_nans_at_start_of_carrer(x):
    
    for index, element in x.items():
        if(np.isnan(element) == True):
            x.loc[index] = 1
        else:
            break

    return(x)


def feature_engineering_fighter_level_loop(df):

    Red_fighters  = list(df['R_fighter'].values)
    Blue_fighters = list(df['B_fighter'].values)
    All_fighters  = Red_fighters + Blue_fighters

    unique_fighters = list(set(All_fighters))

    rank_indexs  = []; fight_number = []
    winLossindex = []; winLossValues = []
    ringRust     = []; fighters = []
    average_fight_time = []; winning_streak = []
    losing_streak = []; takedown_defense = []
    takedown_accuracy = []; strikes_per_minute = []
    striking_accuarcy = []; strikes_absorbed_per_min = []
    striking_defense = []; submission_attempts = []
    average_num_takedowns = []; knockdowns_per_minute = []
    power = []; log_striking_ratio = []
    beaten = []; lost_to = []
    log_of_striking_defense = []; total_takedown_percentage=[]
    average_strikes_or_grapple = []; opp_log_striking_ratio = []
    opponents_avg_strikes_or_grapple = []; opp_log_of_striking_defense = []
    odds_varience = []; finish_ratio = []
    average_fighter_odds = []; average_opponent_odds = []


    df = df.sort_values(by='date', ascending=True)
    for fighter in tqdm(unique_fighters):
        
        fights = df[(df.R_fighter == fighter) | (df.B_fighter == fighter)]

        fighters = fighters + ([fighter] * len(fights))
        # calculates the number of fights a fighter has had at particular point in time

        rank = fights['date'].rank(ascending=True)
        rank_indexs = rank_indexs + list(rank.index)
        fight_number = fight_number + list(rank.values)

        # calculates the win loss ratio at particular point in time
        indices, winLossratio = calculate_winLoss(fights, fighter)
        winLossindex  = winLossindex  + indices
        winLossValues = winLossValues + winLossratio


        # calculate_FinshRatio
        _, FinshRatio = calculate_FinshRatio(fights, fighter)
        finish_ratio = finish_ratio + FinshRatio


        # fighters names who they have either beaten or lost too
        beaten_, lost_to_ = calculate_fighters_beat_and_lost(fights, fighter)
        beaten  = beaten + beaten_
        lost_to = lost_to + lost_to_

        # ring rust feature exapnding standard deviation over time
        ringRust_ = Time_difference_between_consectuive_dates_in_column(fights, 'date').expanding(2).std()
        ringRust  = ringRust + list(ringRust_.values)

        # average fight time
        avg_fight_time = fights['total_fight_time'].expanding(2).mean()
        average_fight_time = average_fight_time + list(avg_fight_time.values)


        # average odds of fighter and opponent
        avg_fighter_odds, avg_opponent_odds = average_odd(fights, fighter, 'red_fighter median', 'blue_fighter median')
        average_fighter_odds = average_fighter_odds + avg_fighter_odds
        average_opponent_odds = average_opponent_odds + avg_opponent_odds


        # wining streak and losing streak
        wins = fights.apply(lambda x: streaks_who_won(x,fighter),axis=1)
        win_streak, lose_streak = calculate_streaks(wins)

        winning_streak = winning_streak + win_streak
        losing_streak  = losing_streak  + lose_streak

        # Takedown Defense
        td_defense = list_fighters_attribute(fights, fighter, 'red_td_defense', 'blue_td_defense')
        td_defense = remove_nans_at_start_of_carrer(td_defense).expanding(2).mean()
        td_defense = td_defense.to_list()
        
        takedown_defense = takedown_defense + td_defense

        # Takedown Accuarcy
        td_accuarcy = list_fighters_attribute(fights, fighter, 'red_td_accuracy', 'blue_td_accuracy')
        td_accuarcy = remove_nans_at_start_of_carrer(td_accuarcy).expanding(2).mean()
        td_accuarcy = td_accuarcy.to_list()
        
        takedown_accuracy = takedown_accuracy + td_accuarcy


        # Total Takedown Percentage
        Tot_takedown_perc = list_fighters_attribute(fights, fighter, 'red_total_takedown_percentage', 'blue_total_takedown_percentage')
        Tot_takedown_perc = remove_nans_at_start_of_carrer(Tot_takedown_perc).expanding(2).mean()
        Tot_takedown_perc = Tot_takedown_perc.to_list()

        total_takedown_percentage = total_takedown_percentage + Tot_takedown_perc


        # strikes per minute
        strike_per_min = list_fighters_attribute(fights, fighter, 'red_strikes_per_minute', 'blue_strikes_per_minute')
        strike_per_min = remove_nans_at_start_of_carrer(strike_per_min).expanding(2).mean()
        strike_per_min = strike_per_min.to_list()
        
        strikes_per_minute = strikes_per_minute + strike_per_min

        # log striking ratio
        strike_ratio = list_fighters_attribute(fights, fighter, 'red_total_striking_ratio', 'blue_total_striking_ratio')
        strike_ratio = remove_nans_at_start_of_carrer(strike_ratio).expanding(2).mean()
        strike_ratio = strike_ratio.to_list()
        strike_ratio = [i if i != 0.0 else 1 for i in strike_ratio]
        strike_ratio  = [log(record) for record in strike_ratio]
  
        log_striking_ratio = log_striking_ratio + strike_ratio 


        # knockdowns per minute
        knockdowns_per_min = list_fighters_attribute(fights, fighter, 'red_knockdowns', 'blue_knockdowns')
        knockdowns_per_min = remove_nans_at_start_of_carrer(knockdowns_per_min).expanding(2).mean()
        knockdowns_per_min = knockdowns_per_min.to_list()
        
        knockdowns_per_minute = knockdowns_per_minute + knockdowns_per_min

        # Power
        power_rating = list_fighters_attribute(fights, fighter, 'red_power', 'blue_power')
        power_rating = remove_nans_at_start_of_carrer(power_rating).expanding(2).mean()
        power_rating = power_rating.to_list()
        
        power = power + power_rating
        
        # striking Accuracy
        strike_accuracy = list_fighters_attribute(fights, fighter, 'red_striking_accuracy', 'blue_striking_accuracy')
        strike_accuracy = remove_nans_at_start_of_carrer(strike_accuracy).expanding(2).mean()
        strike_accuracy = strike_accuracy.to_list()
        
        striking_accuarcy = striking_accuarcy + strike_accuracy

        # Strikes absorbed per minute
        strike_absorbed = list_fighters_attribute(fights, fighter, 'red_strikes_absorbed_per_minute', 'blue_strikes_absorbed_per_minute')
        strike_absorbed = remove_nans_at_start_of_carrer(strike_absorbed).expanding(2).mean()
        strike_absorbed = strike_absorbed.to_list()
        
        strikes_absorbed_per_min = strikes_absorbed_per_min + strike_absorbed

        # Striking Defense
        striking_def = list_fighters_attribute(fights, fighter, 'red_striking_defense', 'blue_striking_defense')
        striking_def = remove_nans_at_start_of_carrer(striking_def).expanding(2).mean()
        striking_def = striking_def.to_list()
        
        striking_defense = striking_defense + striking_def


        # log of Striking Defense
        log_striking_def = list_fighters_attribute(fights, fighter, 'red_striking_defense', 'blue_striking_defense')
        log_striking_def = remove_nans_at_start_of_carrer(log_striking_def).expanding(2).mean()
        log_striking_def = log_striking_def.to_list()
        log_striking_def = [i if i != 0.0 else 1 for i in log_striking_def]
        log_striking_def  = [log(record) for record in log_striking_def]
  
        log_of_striking_defense = log_of_striking_defense + log_striking_def


        # Submission Attempts per 15mins
        sub_attempts = list_fighters_attribute(fights, fighter, 'red_avg_submissions', 'blue_avg_submissions')
        sub_attempts = remove_nans_at_start_of_carrer(sub_attempts).expanding(2).mean()
        sub_attempts = sub_attempts.to_list()
        
        submission_attempts = submission_attempts + sub_attempts
        

        # Average Number of Takedowns per Minute
        avg_takedowns = list_fighters_attribute(fights, fighter, 'red_avg_takedowns', 'blue_avg_takedowns')
        avg_takedowns = remove_nans_at_start_of_carrer(avg_takedowns).expanding(2).mean()
        avg_takedowns = avg_takedowns.to_list()
        
        average_num_takedowns = average_num_takedowns + avg_takedowns


        # striking grapling ratio
        strikes_or_grapple = list_fighters_attribute(fights, fighter, 'red_strikes_or_grapple', 'blue_strikes_or_grapple')
        avg_strikes_or_grapple = remove_nans_at_start_of_carrer(strikes_or_grapple).expanding(2).mean()
        avg_strikes_or_grapple = avg_strikes_or_grapple.to_list()
        
        average_strikes_or_grapple = average_strikes_or_grapple + avg_strikes_or_grapple


        # opponents striking grapling ratio
        opp_strikes_or_grapple = list_opponent_attributes(fights, fighter, 'red_strikes_or_grapple', 'blue_strikes_or_grapple')
        opp_avg_strikes_or_grapple = remove_nans_at_start_of_carrer(opp_strikes_or_grapple).expanding(2).mean()
        opp_avg_strikes_or_grapple = opp_avg_strikes_or_grapple.to_list()
        
        opponents_avg_strikes_or_grapple = opponents_avg_strikes_or_grapple + opp_avg_strikes_or_grapple


        # opponents log striking ratio
        opp_strike_ratio = list_opponent_attributes(fights, fighter, 'red_total_striking_ratio', 'blue_total_striking_ratio')
        opp_strike_ratio = remove_nans_at_start_of_carrer(opp_strike_ratio).expanding(2).mean()
        opp_strike_ratio = opp_strike_ratio.to_list()
        opp_strike_ratio = [i if i != 0.0 else 1 for i in opp_strike_ratio]
        opp_strike_ratio  = [log(record) for record in opp_strike_ratio]
  
        opp_log_striking_ratio = opp_log_striking_ratio + opp_strike_ratio


        # opponents log of Striking Defense
        opp_log_striking_def = list_opponent_attributes(fights, fighter, 'red_striking_defense', 'blue_striking_defense')
        opp_log_striking_def = remove_nans_at_start_of_carrer(opp_log_striking_def).expanding(2).mean()
        opp_log_striking_def = opp_log_striking_def.to_list()
        opp_log_striking_def = [i if i != 0.0 else 1 for i in opp_log_striking_def]
        opp_log_striking_def  = [log(record) for record in opp_log_striking_def]
  
        opp_log_of_striking_defense = opp_log_of_striking_defense + opp_log_striking_def



        # variation in odds from mean
        varience_of_odds = calculate_variance_from_mean_in_odds(fights, fighter, 'red_fighter median', 'blue_fighter median')
        odds_varience = odds_varience + varience_of_odds



    return(pd.DataFrame({'Index':rank_indexs,'Fighters':fighters,
                        'Fight_Number':fight_number, 'WinLossRatio':winLossValues,
                        'RingRust':ringRust,'AVG_fight_time':average_fight_time,
                        'Winning_Streak':winning_streak, 'Losing Streak': losing_streak,
                        'Takedown_Defense': takedown_defense, 'Takedown Accuracy':takedown_accuracy,
                        'Strikes_Per_Minute':strikes_per_minute, 'Striking Accuracy':striking_accuarcy,
                        'Strikes_Absorbed_per_Minute':strikes_absorbed_per_min,
                        'Striking Defense':striking_defense, 'Submission Attempts':submission_attempts,
                        'Average_Num_Takedowns':average_num_takedowns, 'knockdows_per_minute':knockdowns_per_minute,
                        'Power_Rating':power, 'Log_Striking_Ratio': log_striking_ratio,
                        'Beaten_Names':beaten, 'Lost_to_names':lost_to,
                        'Log_Striking_Defense':log_of_striking_defense,
                        'Total_Takedown_Percentage':total_takedown_percentage,
                        'average_strikes_or_grapple':average_strikes_or_grapple,
                        'opponents_avg_strikes_or_grapple':opponents_avg_strikes_or_grapple,
                        'opp_log_striking_ratio':opp_log_striking_ratio,
                        'opp_log_of_striking_defense':opp_log_of_striking_defense,
                        'odds_varience':odds_varience, 'finish_ratio':finish_ratio,
                        'average_fighter_odds':average_fighter_odds,
                        'average_opponent_odds':average_opponent_odds}))