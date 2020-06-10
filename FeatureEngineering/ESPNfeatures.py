import numpy as np
import pandas as pd

'''
ESPN features

strikes per minute
striking accuracy
takedowns per minute
takedown accuarcy %
takedown defense %
strikes absorbed per minute
striking defense number of missed punches by oppenent
submission attempts
number of unanimos decsions/wins by ko/wins by submission

'''

def split_of_from_stat(one_of_two):
  split_sentence = one_of_two.split()
  success   = int(split_sentence[0])
  attempts = int(split_sentence[-1])
  return(success,attempts)

def Calculate_Percentage(success,attempts):
  if attempts > 0:
    return(success/attempts)
  else:
    return(0)

def ESPN_features(row):

  # strikes per minute
  red_total_strikes_landed, red_total_strikes  = split_of_from_stat(row['R_SIG_STR.'])
  blue_total_strikes_landed, blue_total_strikes  = split_of_from_stat(row['B_SIG_STR.'])

  red_strikes_per_minute = red_total_strikes/row['total_fight_time']
  blue_strikes_per_minute = blue_total_strikes_landed/row['total_fight_time']


  # striking ratio
  red_total_striking_ratio = Calculate_Percentage(red_total_strikes_landed, blue_total_strikes_landed)
  blue_total_striking_ratio = Calculate_Percentage(blue_total_strikes_landed, red_total_strikes_landed)

  # striking accuarcy
  red_striking_accuracy  = Calculate_Percentage(red_total_strikes_landed, red_total_strikes)
  blue_striking_accuracy = Calculate_Percentage(blue_total_strikes_landed, blue_total_strikes)
  
  # Power Rating
  if red_total_strikes_landed != 0:
      red_power  = (row['R_KD'] + row['R_win_by_KO/TKO'])/red_total_strikes_landed
  else:
      red_power = 0

  if blue_total_strikes_landed != 0:
      blue_power = (row['B_KD'] + row['B_win_by_KO/TKO'])/blue_total_strikes_landed
  else:
      blue_power = 0 

  # Takedowns per minute
  red_successful_td,  red_total_td    = split_of_from_stat(row['R_TD'])
  blue_successful_td, blue_total_td  =  split_of_from_stat(row['B_TD'])

  red_td_per_minute = red_successful_td/row['total_fight_time']
  blue_td_per_minute = blue_successful_td/row['total_fight_time']

  red_avg_takedowns = red_td_per_minute*15
  blue_avg_takedowns = blue_td_per_minute*15

  if blue_total_td > 0:
    blue_td_accuracy = Calculate_Percentage(blue_successful_td, blue_total_td)

  else:
    blue_td_accuracy = np.NaN

  if red_total_td > 0:
    red_td_accuracy  = Calculate_Percentage(red_successful_td, red_total_td)

  else:
    red_td_accuracy  = np.NaN


  # Takedown Defense %  Takedown Accuarcy %
  red_nr_takedowns_defended  = blue_total_td - blue_successful_td
  blue_nr_takedowns_defended = red_total_td - red_successful_td

  if blue_total_td > 0:
    red_td_defense  = Calculate_Percentage(red_nr_takedowns_defended, blue_total_td)

  else:
    red_td_defense = np.NaN

  if red_total_td > 0:
    blue_td_defense = Calculate_Percentage(blue_nr_takedowns_defended,red_total_td)

  else:
    blue_td_defense  = np.NaN

  # Kncokdowns per minute
  red_knockdowns  = row['R_KD']/row['total_fight_time']
  blue_knockdowns = row['B_KD']/row['total_fight_time']

  # strikes absorbed per minute
  red_strikes_absorbed_per_minute = blue_total_strikes_landed/row['total_fight_time']
  blue_strikes_absorbed_per_minute = red_total_strikes_landed/row['total_fight_time']

  # striking defense %
  red_strikes_avoided = (blue_total_strikes - blue_total_strikes_landed)
  blue_strikes_avoided = (red_total_strikes - red_total_strikes_landed)

  red_striking_defense  = Calculate_Percentage(red_strikes_avoided,  blue_total_strikes)
  blue_striking_defense = Calculate_Percentage(blue_strikes_avoided, red_total_strikes)

  # submission attempts per minute
  red_sub_attempts =  row.R_SUB_ATT
  blue_sub_attempts = row.B_SUB_ATT

  red_sub_per_minute =  red_sub_attempts/row['total_fight_time']
  blue_sub_per_minute = blue_sub_attempts/row['total_fight_time']

  red_avg_submissions = red_sub_per_minute*15
  blue_avg_submissions = blue_sub_per_minute*15

  return(red_strikes_per_minute, blue_strikes_per_minute,
        red_striking_accuracy, blue_striking_accuracy,
        red_avg_takedowns, blue_avg_takedowns,
        red_td_accuracy, blue_td_accuracy,
        red_td_defense, blue_td_defense,
        red_strikes_absorbed_per_minute, blue_strikes_absorbed_per_minute,
        red_striking_defense, blue_striking_defense,
        red_avg_submissions, blue_avg_submissions,
        red_knockdowns, blue_knockdowns,
        red_power, blue_power,
        red_total_striking_ratio , blue_total_striking_ratio)
