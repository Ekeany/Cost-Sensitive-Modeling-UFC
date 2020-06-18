import numpy as np
import pandas as pd

'''
Grappling:

2 points for takedown
1 point takedown defense
2 points sweep
3 points pasing guard
1 point submision attempt
2 points to more strikes landed

winner most points or if person gets submission

if its within one point classify as dra
'''

'''
Striking

Greater number of significant stikes landed if absoulte
difference in strikes landed is ten.

A knock down contributes 10% to the number of significant strikes

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

def calculate_relative_different(num1,num2):
  absoulute_diff = abs(num1-num2)
  minimum = min(num1,num2)
  if minimum > 0:
    return(absoulute_diff/minimum)
  else:
    return absoulute_diff/1

def check_ground_strikes(red,blue):
  if(red >= blue*1.25) and (red > 10):
    return('red')
  elif(blue >= red*1.25) and blue > 10:
    return('blue')
  else:
    return('draw')

def check_who_had_more_points(red, blue):
  if red > blue:
    return('Red')
  elif blue > red:
    return('Blue')
  else:
    return('Draw')


def ground_and_pound(row):

  red_ground_strikes, _ = split_of_from_stat(row.R_GROUND)
  blue_ground_strikes, _ = split_of_from_stat(row.B_GROUND)

  if((red_ground_strikes < 7) & (blue_ground_strikes < 7)):
      return('No Contest') 

  elif calculate_relative_different(red_ground_strikes, blue_ground_strikes) > 0.2:
      output = check_who_had_more_points(red_ground_strikes, blue_ground_strikes)
      return(output)

  else:
    return('Draw')


def wrestling(row):
  
  # takedowns
  red_takedowns_success, n_red_takedowns_attempts = split_of_from_stat(row.R_TD)
  blue_takedowns_success, n_blue_takedowns_attempts = split_of_from_stat(row.B_TD)

  # Takedown Defense
  red_takedowns_defenses = n_blue_takedowns_attempts - blue_takedowns_success
  blue_takedowns_defenses = n_red_takedowns_attempts - red_takedowns_success

  # Takedown Accuracy
  red_takedown_accuracy  = Calculate_Percentage(red_takedowns_success, n_red_takedowns_attempts)
  blue_takedown_accuracy = Calculate_Percentage(blue_takedowns_success, n_blue_takedowns_attempts)

  red_points = (3*red_takedowns_success)+(1*red_takedowns_defenses)
  blue_points = (3*blue_takedowns_success)+(1*blue_takedowns_defenses)

  if abs(blue_points-red_points) > 1:
    output = check_who_had_more_points(red_points, blue_points)
    return(output)

  elif((n_red_takedowns_attempts < 2) & (n_blue_takedowns_attempts < 2)):
    return('No Contest')

  elif((red_takedown_accuracy > 0.3) | (blue_takedown_accuracy > 0.3)):
    output = check_who_had_more_points(red_points, blue_points)
    return(output)

  else:
    return('Draw')


def JiuJitsu(row):
  
  if row.win_by == 'Submission':
    return(row.Winner)

  else:

    # reversals
    red_reversals  = row.R_REV
    blue_reversals = row.B_REV

    # Guard Passes
    blue_passes  = row.B_PASS
    red_passes = row.R_PASS

    # Submission Attempts
    red_sub_attempts =  row.R_SUB_ATT
    blue_sub_attempts = row.B_SUB_ATT

    # Total Moves made
    red_total_moves = red_reversals + red_passes + red_sub_attempts
    blue_total_moves = blue_reversals + blue_passes + blue_sub_attempts

    red_points = (2*red_reversals)+(3*red_passes)+(2*red_sub_attempts)

    blue_points = (2*blue_reversals)+(3*blue_passes)+(2*blue_sub_attempts)

    if abs(blue_points-red_points) > 1:
      output = check_who_had_more_points(red_points, blue_points)
      return(output)

    elif((red_total_moves < 2) & (blue_total_moves < 2)):
      return('No Contest')

    else:
      return('Draw')


def grappling(row):

  if row.win_by == 'Submission':
    return(row.Winner)

  else:

    # takedowns
    red_takedowns_success, n_red_takedowns_attempts = split_of_from_stat(row.R_TD)
    blue_takedowns_success, n_blue_takedowns_attempts = split_of_from_stat(row.B_TD)

    # Takedown Defense
    red_takedowns_defenses = n_blue_takedowns_attempts - blue_takedowns_success
    blue_takedowns_defenses = n_red_takedowns_attempts - red_takedowns_success

    # reversals
    red_reversals  = row.R_REV
    blue_reversals = row.B_REV

    # Guard Passes
    blue_passes  = row.B_PASS
    red_passes = row.R_PASS

    # Submission Attempts
    red_sub_attempts =  row.R_SUB_ATT
    blue_sub_attempts = row.B_SUB_ATT

    # Ground Stikes
    red_ground_strikes, _ = split_of_from_stat(row.R_GROUND)
    blue_ground_strikes, _ = split_of_from_stat(row.B_GROUND)


    flag = check_ground_strikes(red_ground_strikes, blue_ground_strikes)

    if flag == 'red':
      red_strikes = 2
      blue_strikes = 0
    elif flag == 'blue':
      red_strikes = 0
      blue_strikes = 2
    else:
      red_strikes = 0
      blue_strikes = 0

    red_points = ((2*red_takedowns_success)+(1*red_takedowns_defenses)+
                (2*red_reversals)+(3*red_passes)+(2*red_sub_attempts)) + red_strikes

    blue_points = ((2*blue_takedowns_success)+(1*blue_takedowns_defenses)+
                (2*blue_reversals)+(3*blue_passes)+(2*blue_sub_attempts)) + blue_strikes

    if abs(blue_points-red_points) > 1:
      output = check_who_had_more_points(red_points, blue_points)
      return(output)
    else:
      return('Draw')


def striking(row):

  if row.win_by == 'KO/TKO':
    return(row.Winner)

  else:

    red_significant_strikes_landed,  red_total_sig_strikes_thrown = split_of_from_stat(row['R_SIG_STR.'])
    blue_significant_strikes_landed, blue_total_sig_strikes_thrown = split_of_from_stat(row['B_SIG_STR.'])

    red_knock_downs  = row.R_KD
    blue_knock_downs = row.B_KD

    red_strikes_dodged = (blue_total_sig_strikes_thrown - blue_significant_strikes_landed)
    blue_strikes_dodged = (red_total_sig_strikes_thrown - red_significant_strikes_landed)

    # Striking Accuarcy
    red_accuracy = Calculate_Percentage(red_significant_strikes_landed, red_total_sig_strikes_thrown)
    blue_accuracy = Calculate_Percentage(blue_significant_strikes_landed,blue_total_sig_strikes_thrown)

    red_points = ((red_significant_strikes_landed)+
                  (red_significant_strikes_landed*0.1)*(red_knock_downs))

    blue_points = ((blue_significant_strikes_landed)+
                   (blue_significant_strikes_landed*0.1)*(blue_knock_downs))
    

    scaled_points_blue = blue_accuracy*blue_points
    scaled_points_red  = red_accuracy*red_points

    if((red_points < 10) & (blue_points < 10)):
      return('No Contest')
    
    elif calculate_relative_different(red_points,blue_points) > 0.2:
      output = check_who_had_more_points(scaled_points_red, scaled_points_blue)
      return(output)

    else:
      return('Draw')