import numpy as np
import pandas as pd

def convert_negative_american_odds(odds):
    odds = abs(odds)
    return((odds/(odds+100)))

def convert_positve_american_odds(odds):
    return((100/(odds+100)))

def check_if_number_pos_or_neg(number):
  if(number > 0):
    return(True)
  else:
    return(False)

def convert_american_odds_to_perecentage(odds):
  if check_if_number_pos_or_neg(odds) == True:
    return(convert_positve_american_odds(odds))
  else:
    return(convert_negative_american_odds(odds))
