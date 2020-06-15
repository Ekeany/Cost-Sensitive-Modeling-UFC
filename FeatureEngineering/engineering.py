import numpy as np
import pandas as pd
from tqdm import tqdm
from statistics import mean
import sys
import os
from pathlib import Path
from scipy.spatial import distance

from PreProcessing.Imputer import Imputer
from FeatureEngineering.ewma import EWMA
from FeatureEngineering.ufc_elo import calculate_elos
from FeatureEngineering.odds_utils import convert_american_odds_to_perecentage
from FeatureEngineering.WhoWonAtGraplingStriking import wrestling, striking, ground_and_pound, JiuJitsu, grappling
from FeatureEngineering.ESPNfeatures import ESPN_features
from FeatureEngineering.skill import calculate_skill
from FeatureEngineering.Fighter_Level_features import feature_engineering_fighter_level_loop, check_if_each_row_is_either_red_or_blue
from FeatureEngineering.Shift_Features import Shift_all_features
from FeatureEngineering.comparing_previous_opponents import get_stats_of_fighters_who_they_have_beaten_or_lost_to, Normalize_Features


class Engineering:

    def __init__(self):

        self.BASE_PATH  = Path(os.getcwd())
        
        self.read_files()
        self.create_total_fight_time()
        self.merge_files()
        self.create_espn_features()
        self.create_elo_ratings()
        self.create_skill_based_features()
        print('Creating Fighter Level Attributes')
        self.create_fighter_level_attributes()
        self.GetStatsOfFightersWhoTheyHaveBeatenOrLostTo()
        self.check_if_fighter_beat_anyone_who_opponent_has_lost_to()
        self.calculate_average_distance_of_opponent_to_previous_wins_loses()

        print('Shift All Features')
        self.shift_features()
        self.subset_features()
        self.Normalize_different_wins()
        self.save_file(filename='data/engineered_features.csv')

    
    def read_files(self):

        print('Reading Files')

        try:
            self.fight = pd.read_csv(self.BASE_PATH/'data/data.csv', parse_dates=['date'])
        
        except:
            raise FileNotFoundError('Cannot find the data/data.csv')

        
        try:
            self.raw_fight = pd.read_csv(self.BASE_PATH/'data/total_fight_data.csv', sep=';', parse_dates=['date'])
        
        except:
            raise FileNotFoundError('Cannot find the data/total_fight_data.csv')


        try:
            self.odds = pd.read_csv(self.BASE_PATH/'data/raw_fighter_odds.csv', parse_dates=['Date'])[['Fighter_one','Fighter_two','Average_Odds_f1','Average_Odds_f2','Date']]
            self.odds.Average_Odds_f1 = pd.to_numeric(self.odds.Average_Odds_f1)
            self.odds.Average_Odds_f2 = pd.to_numeric(self.odds.Average_Odds_f2)
        except:
            raise FileNotFoundError('Cannot find the data/raw_fighter_odds.csv')


    @staticmethod
    def create_a_merge_column(df, fighter_one, fighter_two, date):

        df['merge'] = df[fighter_one] + df[fighter_two] 
        df['merge'] = df['merge'].apply(lambda x: x.replace(" ", "").replace(".",""))
        df['merge'] = df['merge'].apply(lambda x: ''.join(sorted(x)))
        df['merge'] = df['merge'] + df[date].astype(str)

        return(df)


    @staticmethod
    def calculate_time(last_round_time, last_round):
        
        if last_round_time >= 5:
            return(last_round*5)

        else:
            return((last_round*5)+last_round_time)

    
    def create_total_fight_time(self):
        self.raw_fight.last_round_time = self.raw_fight.last_round_time.apply(lambda x: float(x.replace(':','.')))
        self.raw_fight['total_fight_time'] = (np.where(self.raw_fight.last_round_time >= 5, 
                                                       self.raw_fight.last_round*5,
                                                       ((self.raw_fight.last_round-1)*5) + self.raw_fight.last_round_time))


    def create_merge_cols(self):

        self.odds = self.create_a_merge_column(self.odds, 'Fighter_one', 'Fighter_two', 'Date')
        self.fights = self.create_a_merge_column(self.fight, 'R_fighter', 'B_fighter', 'date')
        self.raw_fight = self.create_a_merge_column(self.raw_fight, 'R_fighter', 'B_fighter', 'date')


    def merge_files(self):

        self.create_merge_cols()
        self.fights_and_odds = self.fights.merge(self.odds,on='merge')

        # swap columns when needed
        self.fights_and_odds.Average_Odds_f1, self.fights_and_odds.Average_Odds_f2 = (np.where(self.fights_and_odds.R_fighter == self.fights_and_odds.Fighter_one, 
                                                                             [self.fights_and_odds.Average_Odds_f1, self.fights_and_odds.Average_Odds_f2], 
                                                                             [self.fights_and_odds.Average_Odds_f2, self.fights_and_odds.Average_Odds_f1]))


        self.fights_and_odds['red_Fighter_Odds']   = self.fights_and_odds.Average_Odds_f1.apply(lambda x: convert_american_odds_to_perecentage(x))
        self.fights_and_odds['blue_Fighter_Odds']  = self.fights_and_odds.Average_Odds_f2.apply(lambda x: convert_american_odds_to_perecentage(x))

        
        raw_fight_selected = self.raw_fight[['win_by','total_fight_time','B_GROUND','R_GROUND','B_CLINCH','R_CLINCH','B_DISTANCE',
                                            'R_DISTANCE','B_LEG','R_LEG','B_BODY','R_BODY','B_HEAD','R_HEAD','B_REV','R_REV',
                                            'B_PASS','R_PASS','B_SUB_ATT','R_SUB_ATT','B_TD_pct','R_TD_pct','B_TD','R_TD',
                                            'B_TOTAL_STR.','R_TOTAL_STR.','B_SIG_STR_pct','R_SIG_STR_pct','B_SIG_STR.','R_SIG_STR.',
                                            'B_KD','R_KD','merge']]

        self.fights_and_odds = self.fights_and_odds.merge(raw_fight_selected, on = 'merge')


        # drop duplicates two odds for same fight
        self.fights_and_odds.drop_duplicates(subset=['merge'], keep='first',inplace=True)
        self.fights_and_odds.drop(['merge','Fighter_one','Fighter_two','Date',
                              'Referee','location'], inplace = True, axis = 1)

    
    def create_espn_features(self):

        (self.fights_and_odds['red_strikes_per_minute'],
        self.fights_and_odds['blue_strikes_per_minute'],
        self.fights_and_odds['red_striking_accuracy'],
        self.fights_and_odds['blue_striking_accuracy'],
        self.fights_and_odds['red_avg_takedowns'],
        self.fights_and_odds['blue_avg_takedowns'],
        self.fights_and_odds['red_td_accuracy'],
        self.fights_and_odds['blue_td_accuracy'],
        self.fights_and_odds['red_td_defense'],
        self.fights_and_odds['blue_td_defense'],
        self.fights_and_odds['red_strikes_absorbed_per_minute'],
        self.fights_and_odds['blue_strikes_absorbed_per_minute'],
        self.fights_and_odds['red_striking_defense'],
        self.fights_and_odds['blue_striking_defense'],
        self.fights_and_odds['red_avg_submissions'],
        self.fights_and_odds['blue_avg_submissions'],
        self.fights_and_odds['red_knockdowns'],
        self.fights_and_odds['blue_knockdowns'],
        self.fights_and_odds['red_power'],
        self.fights_and_odds['blue_power'],
        self.fights_and_odds['red_total_striking_ratio'],
        self.fights_and_odds['blue_total_striking_ratio']) = zip(*self.fights_and_odds.apply(lambda x: ESPN_features(x), axis=1))

    
    def create_elo_ratings(self):
        self.FightsOddsElos = calculate_elos(self.fights_and_odds, k = 25)


    def create_skill_based_features(self):

        self.FightsOddsElos['Who_Won_at_Wrestling']    = self.fights_and_odds.apply(lambda x: wrestling(x), axis=1)
        self.FightsOddsElos['Who_Won_at_Striking']     = self.fights_and_odds.apply(lambda x: striking(x), axis=1)
        self.FightsOddsElos['Who_Won_at_Ground&Pound'] = self.fights_and_odds.apply(lambda x: ground_and_pound(x), axis=1)
        self.FightsOddsElos['Who_Won_at_JiuJitsu']     = self.fights_and_odds.apply(lambda x: JiuJitsu(x), axis=1)
        self.FightsOddsElos['Who_Won_at_Grappling']    = self.fights_and_odds.apply(lambda x: grappling(x), axis=1)

        self.FightsOddsElos = calculate_skill(self.FightsOddsElos, 'Winner',
                                        'red_skill','blue_skill')
        self.FightsOddsElos = calculate_skill(self.FightsOddsElos, 'Who_Won_at_Wrestling',
                                        'wrestling_red_skill','wrestling_blue_skill')
        self.FightsOddsElos = calculate_skill(self.FightsOddsElos, 'Who_Won_at_Striking',
                                        'striking_red_skill','striking_blue_skill')
        self.FightsOddsElos = calculate_skill(self.FightsOddsElos, 'Who_Won_at_Ground&Pound',
                                        'g_and_p_red_skill','g_and_p_blue_skill')
        self.FightsOddsElos = calculate_skill(self.FightsOddsElos, 'Who_Won_at_JiuJitsu',
                                        'jiujitsu_red_skill', 'jiujitsu_blue_skill')
        self.FightsOddsElos = calculate_skill(self.FightsOddsElos, 'Who_Won_at_Grappling',
                                        'grappling_red_skill','grappling_blue_skill')


    def create_fighter_level_attributes(self):
        
        new_features = feature_engineering_fighter_level_loop(self.FightsOddsElos)
        add_variable_to_split = check_if_each_row_is_either_red_or_blue(new_features, self.FightsOddsElos)

        red = add_variable_to_split[add_variable_to_split.Blue_or_Red == 'Red'].rename(columns = {'Fight_Number':'R_Fight_Number',
                                                         'WinLossRatio':'R_WinLossRatio','RingRust':'R_RingRust',
                                                         'AVG_fight_time':'R_AVG_fight_time','Winning_Streak':'R_Winning_Streak',
                                                          'Losing Streak':'R_Losing_Streak',
                                                          'Takedown_Defense':'R_Takedown_Defense',
                                                          'Takedown Accuracy':'R_Takedown Accuracy',
                                                          'Strikes_Per_Minute':'R_Strikes_Per_Minute',
                                                          'Striking Accuracy':'R_Striking Accuracy',
                                                          'Strikes_Absorbed_per_Minute':'R_Strikes_Absorbed_per_Minute',
                                                          'Striking Defense':'R_Striking Defense',
                                                          'Submission Attempts':'R_Submission Attempts',
                                                          'Average_Num_Takedowns':'R_Average_Num_Takedowns',
                                                          'knockdows_per_minute':'R_knockdows_per_minute',
                                                          'Power_Rating':'R_Power_Rating',
                                                          'Log_Striking_Ratio':'R_Log_Striking_Ratio',
                                                          'Beaten_Names':'R_Beaten_Names',
                                                          'Lost_to_names': 'R_Lost_to_names'}).set_index('Index')
        red.drop(['Blue_or_Red','Fighters'], inplace=True,axis=1)

        blue = add_variable_to_split[add_variable_to_split.Blue_or_Red == 'Blue'].rename(columns = {'Fight_Number':'B_Fight_Number',
                                                         'WinLossRatio':'B_WinLossRatio','RingRust':'B_RingRust',
                                                         'AVG_fight_time':'B_AVG_fight_time','Winning_Streak':'B_Winning_Streak',
                                                          'Losing Streak':'B_Losing_Streak',
                                                          'Takedown_Defense':'B_Takedown_Defense',
                                                          'Takedown Accuracy':'B_Takedown Accuracy',
                                                          'Strikes_Per_Minute':'B_Strikes_Per_Minute',
                                                          'Striking Accuracy':'B_Striking Accuracy',
                                                          'Strikes_Absorbed_per_Minute':'B_Strikes_Absorbed_per_Minute',
                                                          'Striking Defense':'B_Striking Defense',
                                                          'Submission Attempts':'B_Submission Attempts',
                                                          'Average_Num_Takedowns':'B_Average_Num_Takedowns',
                                                          'knockdows_per_minute':'B_knockdows_per_minute',
                                                          'Power_Rating':'B_Power_Rating',
                                                          'Log_Striking_Ratio':'B_Log_Striking_Ratio',
                                                          'Beaten_Names':'B_Beaten_Names',
                                                          'Lost_to_names': 'B_Lost_to_names'}).set_index('Index')

        blue.drop(['Blue_or_Red','Fighters'], inplace=True,axis=1)

        self.Elos_and_features = self.FightsOddsElos.join(red)
        self.Elos_and_features = self.Elos_and_features.join(blue)



    def GetStatsOfFightersWhoTheyHaveBeatenOrLostTo(self):

        the_features = get_stats_of_fighters_who_they_have_beaten_or_lost_to(self.Elos_and_features)
        add_variable_to_split = check_if_each_row_is_either_red_or_blue(the_features, self.Elos_and_features)

        red_attributes = add_variable_to_split[add_variable_to_split.Blue_or_Red == 'Red'].rename(columns = {
            'Stats_of_Opponents_they_have_beaten' :'R_Stats_of_Opponents_they_have_beaten',
            'Stats_of_Opponents_they_have_lost_to':'R_Stats_of_Opponents_they_have_lost_to'}).set_index('Index')

        red_attributes.drop(['Blue_or_Red','Fighters'], inplace=True,axis=1)

        blue_attributes = add_variable_to_split[add_variable_to_split.Blue_or_Red == 'Blue'].rename(columns = {
            'Stats_of_Opponents_they_have_beaten' :'B_Stats_of_Opponents_they_have_beaten',
            'Stats_of_Opponents_they_have_lost_to':'B_Stats_of_Opponents_they_have_lost_to'}).set_index('Index')

        blue_attributes.drop(['Blue_or_Red','Fighters'], inplace=True,axis=1)

        self.Elos_and_features = self.Elos_and_features.join(red_attributes)
        self.Elos_and_features = self.Elos_and_features.join(blue_attributes)



    def shift_features(self):
        '''
        Shift features as they need to be an accumaltion of stats before fight
        '''
        self.shifted_elos_and_features = Shift_all_features(self.Elos_and_features)


    @staticmethod
    def check_if_fighter_has_beaten_opponent_and_who_beat_their_current_opponent(row):
        
        R_beaten = set(row['R_Beaten_Names'])
        R_lost   = set(row['R_Lost_to_names'])

        B_beaten = set(row['B_Beaten_Names'])
        B_lost   = set(row['B_Lost_to_names'])

        if (len(R_beaten) > 0) and (len(B_lost) > 0):
            Red_beat = len(list(R_beaten & B_lost))
        else:
            Red_beat = 0

        if (len(B_beaten) > 0) and (len(R_lost) > 0):
            Blue_beat = len(list(B_beaten & R_lost))
        else:
            Blue_beat = 0

        return Red_beat, Blue_beat
        

    @staticmethod
    def Average_distance_of_oppent_to_wins_and_loses(row):

        blue_fighter = [row['blue_Fighter_Odds'], row['B_Takedown Accuracy'],
                row['B_age'], row['B_RingRust'],
                row['B_Striking Defense'], row['B_Takedown_Defense'],
                row['blue_skill'],  row['striking_blue_skill'],
                row['wrestling_blue_skill'],  row['B_Power_Rating'],
                row['g_and_p_blue_skill'], row['jiujitsu_blue_skill'],
                row['B_Strikes_Absorbed_per_Minute'], row['B_AVG_fight_time']]

        red_fighter = [row['red_Fighter_Odds'], row['R_Takedown Accuracy'],
                row['R_age'],   row['R_RingRust'],
                row['R_Striking Defense'], row['R_Takedown_Defense'],
                row['red_skill'],  row['striking_red_skill'],
                row['wrestling_red_skill'],  row['R_Power_Rating'],
                row['g_and_p_red_skill'], row['jiujitsu_red_skill'],
                row['R_Strikes_Absorbed_per_Minute'], row['R_AVG_fight_time']]


        if len(row['R_Stats_of_Opponents_they_have_beaten']) > 0:
            distances = []
            for fighter in row['R_Stats_of_Opponents_they_have_beaten']:
                distances.append(distance.euclidean(blue_fighter, fighter))
            
            distance_red_beaten = EWMA(distances, 2)
        else:
            distance_red_beaten = 9999


        if len(row['R_Stats_of_Opponents_they_have_lost_to']) > 0:
            distances = []
            for fighter in row['R_Stats_of_Opponents_they_have_lost_to']:
                distances.append(distance.euclidean(blue_fighter, fighter))
            
            distance_red_lost = mean(distances)
        else:
            distance_red_lost = 9999


        if len(row['B_Stats_of_Opponents_they_have_beaten']) > 0:
            distances = []
            for fighter in row['B_Stats_of_Opponents_they_have_beaten']:
                distances.append(distance.euclidean(red_fighter, fighter))
            
            distance_blue_beaten = EWMA(distances, 2)
        else:
            distance_blue_beaten = 9999

        if len(row['B_Stats_of_Opponents_they_have_lost_to']) > 0:
            distances = []
            for fighter in row['B_Stats_of_Opponents_they_have_lost_to']:
                distances.append(distance.euclidean(red_fighter, fighter))
            
            distance_blue_lost = mean(distances)
        else:
            distance_blue_lost = 9999

        return distance_red_beaten, distance_red_lost, distance_blue_beaten, distance_blue_lost


    def calculate_average_distance_of_opponent_to_previous_wins_loses(self):

        temp  = Normalize_Features(self.Elos_and_features)
        
        (temp['R_distance_beaten'], 
         temp['R_distance_lost'], 
         temp['B_distance_beaten'],
         temp['B_distance_lost']) \
        =  zip(*temp.apply(lambda x: self.Average_distance_of_oppent_to_wins_and_loses(x), axis=1))
        
        temp = self.create_a_merge_column(temp, 'R_fighter', 'B_fighter', 'date')

        temp = temp[['R_distance_beaten','R_distance_lost','B_distance_beaten','B_distance_lost',
                    'merge']].copy()

        self.Elos_and_features = self.create_a_merge_column(self.Elos_and_features, 'R_fighter', 'B_fighter', 'date')
        self.Elos_and_features = self.Elos_and_features.merge(temp, on = 'merge')



    def check_if_fighter_beat_anyone_who_opponent_has_lost_to(self):

        (self.Elos_and_features['R_Beaten_Similar'], 
        self.Elos_and_features['B_Beaten_Similar']) \
        = zip(*self.Elos_and_features.apply(lambda x: self.check_if_fighter_has_beaten_opponent_and_who_beat_their_current_opponent(x), axis=1))


    def subset_features(self):

        self.subset = self.shifted_elos_and_features[['R_fighter','B_fighter','Average_Odds_f1', 'Average_Odds_f2','date','title_bout','win_by','weight_class',
                            'red_fighters_elo','blue_fighters_elo','red_Fighter_Odds','blue_Fighter_Odds','Winner', 'R_distance_beaten', 'R_distance_lost',
                            'R_Fight_Number','R_Stance', 'R_Height_cms', 'R_Reach_cms', 'R_age', 'R_WinLossRatio','R_Beaten_Names', 'R_Lost_to_names',
                            'R_RingRust','R_Winning_Streak','R_Losing_Streak','R_AVG_fight_time','R_total_title_bouts','R_Beaten_Similar',
                            'R_Takedown_Defense', 'R_Takedown Accuracy','R_Strikes_Per_Minute', 'R_Log_Striking_Ratio' , 'R_Striking Accuracy',
                            'R_Strikes_Absorbed_per_Minute','R_Striking Defense','R_knockdows_per_minute','R_Submission Attempts',
                            'R_Average_Num_Takedowns','R_win_by_Decision_Majority','R_win_by_Decision_Split','R_win_by_Decision_Unanimous',
                            'R_win_by_KO/TKO', 'R_win_by_Submission', 'R_win_by_TKO_Doctor_Stoppage','R_Power_Rating','red_skill',
                            'wrestling_red_skill','striking_red_skill','g_and_p_red_skill', 'jiujitsu_red_skill', 'grappling_red_skill',
                            'R_Stats_of_Opponents_they_have_beaten', 'R_Stats_of_Opponents_they_have_lost_to',
                            'B_Fight_Number',
                            'B_Stance','B_Height_cms','B_Reach_cms', 'B_age','B_WinLossRatio','B_RingRust','B_Winning_Streak', 'B_Beaten_Similar', 
                            'B_Losing_Streak','B_AVG_fight_time', 'B_total_title_bouts','B_Takedown_Defense', 'B_Takedown Accuracy', 'B_distance_beaten', 'B_distance_lost',
                            'B_Strikes_Per_Minute','B_Striking Accuracy','B_Log_Striking_Ratio','B_Strikes_Absorbed_per_Minute','B_Striking Defense',
                            'B_knockdows_per_minute','B_Submission Attempts','B_Average_Num_Takedowns','B_win_by_Decision_Majority',
                            'B_win_by_Decision_Split','B_win_by_Decision_Unanimous','B_win_by_KO/TKO','B_win_by_Submission',
                            'B_win_by_TKO_Doctor_Stoppage','B_Power_Rating','blue_skill', 'wrestling_blue_skill', 'striking_blue_skill',
                            'g_and_p_blue_skill', 'jiujitsu_blue_skill', 'grappling_blue_skill','B_Beaten_Names', 'B_Lost_to_names',
                            'B_Stats_of_Opponents_they_have_beaten', 'B_Stats_of_Opponents_they_have_lost_to']]


    def Normalize_different_wins(self):
        
        self.final = self.subset.copy()
        red_columns = ['R_win_by_Decision_Majority','R_win_by_Decision_Split','R_win_by_Decision_Unanimous',
                       'R_win_by_KO/TKO', 'R_win_by_Submission', 'R_win_by_TKO_Doctor_Stoppage']
                       
        blue_columns = ['B_win_by_Decision_Majority','B_win_by_Decision_Split','B_win_by_Decision_Unanimous',
                        'B_win_by_KO/TKO', 'B_win_by_Submission', 'B_win_by_TKO_Doctor_Stoppage']

        for red, blue in zip(red_columns, blue_columns):
            
            self.final[red]  = self.final[red]/self.final['R_Fight_Number']
            self.final[blue] = self.final[blue]/self.final['B_Fight_Number']



    def save_file(self, filename):
        self.final.to_csv(self.BASE_PATH/filename, index=False)




