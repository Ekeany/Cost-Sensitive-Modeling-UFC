import pandas as pd
import numpy as np
from tqdm import tqdm


def extract_stats(row, fighter, red_column, blue_column):
  
  if row.R_fighter == fighter:
    return(row[red_column], 1)

  elif row.B_fighter == fighter:
    return(row[blue_column], 0)


def list_fighters_attribute(df, fighter, red_column, blue_column):
  values = df.apply(lambda x : extract_stats(x, fighter, red_column, blue_column), axis = 1)
  return pd.DataFrame(values.tolist(), columns=['Fighter_Value','Red_or_Blue'], index=values.index)


def replace_shifted_values_back(subset, original_df, fighter, red_column, blue_column):

  values = list_fighters_attribute(subset, fighter, red_column, blue_column)

  # shift values but keep red or blue constant
  values.Fighter_Value = values.Fighter_Value.shift()
  for index, row in values.iterrows():

    if row['Red_or_Blue'] == 1:
      original_df.loc[index, red_column] = row['Fighter_Value']

    else:
      original_df.loc[index, blue_column] = row['Fighter_Value']
    
  return original_df


def Shift_all_features(df):

  Red_fighters  = list(df['R_fighter'].values)
  Blue_fighters = list(df['B_fighter'].values)
  All_fighters  = Red_fighters + Blue_fighters

  unique_fighters = list(set(All_fighters))

  cols_to_shift_red = ['red_fighters_elo','R_WinLossRatio', 'R_Log_Striking_Defense',
                 'R_Winning_Streak','R_Losing_Streak','R_AVG_fight_time',
                 'R_total_title_bouts','R_Takedown_Defense','R_Takedown Accuracy',
                 'R_Strikes_Per_Minute','R_Striking Accuracy','R_Strikes_Absorbed_per_Minute',
                 'R_Striking Defense','R_knockdows_per_minute','R_Submission Attempts',
                 'R_Average_Num_Takedowns','R_Power_Rating','red_skill','wrestling_red_skill',
                 'striking_red_skill', 'g_and_p_red_skill','jiujitsu_red_skill','R_Log_Striking_Ratio',
                 'grappling_red_skill', 'log_striking_red_skill', 'log_defense_red_skill',
                 'R_opponents_avg_strikes_or_grapple', 'R_opp_log_striking_ratio',
                 'R_opp_log_of_striking_defense','R_average_strikes_or_grapple', 'R_Total_Takedown_Percentage']
                 
                 
  cols_to_shift_blue  = ['blue_fighters_elo', 'B_WinLossRatio', 'B_Log_Striking_Defense',
                 'B_Winning_Streak','B_Losing_Streak','B_AVG_fight_time', 'B_Log_Striking_Ratio',
                 'B_total_title_bouts','B_Takedown_Defense','B_Takedown Accuracy',
                 'B_Strikes_Per_Minute','B_Striking Accuracy','B_Strikes_Absorbed_per_Minute',
                 'B_Striking Defense','B_knockdows_per_minute','B_Submission Attempts',
                 'B_Average_Num_Takedowns','B_Power_Rating','blue_skill','wrestling_blue_skill',
                 'striking_blue_skill', 'g_and_p_blue_skill','jiujitsu_blue_skill', 'B_average_strikes_or_grapple',
                 'grappling_blue_skill', 'log_striking_blue_skill','log_defense_blue_skill', 'B_Total_Takedown_Percentage',
                 'B_opponents_avg_strikes_or_grapple', 'B_opp_log_striking_ratio', 'B_opp_log_of_striking_defense']
                 

  df = df.sort_values(by='date', ascending=True)

  for fighter in tqdm(unique_fighters):

      fights = df[(df.R_fighter == fighter) | (df.B_fighter == fighter)]

      for red, blue in zip(cols_to_shift_red, cols_to_shift_blue):
        replace_shifted_values_back(subset=fights, 
                                       original_df=df, 
                                       fighter=fighter, 
                                       red_column=red,
                                       blue_column=blue)

  return df