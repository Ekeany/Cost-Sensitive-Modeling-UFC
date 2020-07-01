import numpy as np
import pandas as pd
from tqdm import tqdm

def expected(A, B):
    return 1 / (1 + 10 ** ((B - A) / 400))

def elo(exp, score, k):
    return(k * (score - exp))

def initalise_elos(df):

  Red_fighters  = list(df['R_fighter'].values)
  Blue_fighters = list(df['B_fighter'].values)
  All_fighters  = Red_fighters + Blue_fighters

  unique_fighters = list(set(All_fighters))
  constant_elo    = [1000]*len(unique_fighters)

  return(dict(zip(unique_fighters, constant_elo)))


def compute_updates(red_fighter, blue_fighter, winner , elos, red_k, blue_k):

  expectation_red  = expected(elos[red_fighter], elos[blue_fighter])
  expectation_blue = 1 - expectation_red

  if winner == 'Red':
    red_win_lose  = 1
    blue_win_lose = 0
  elif winner == 'Blue':
    red_win_lose  = 0
    blue_win_lose = 1
  else:
    red_win_lose  = 0.5
    blue_win_lose = 0.5

  # update values
  return(elo(expectation_red, red_win_lose, red_k),
         elo(expectation_blue, blue_win_lose, blue_k))


def calculate_elos(df):

  df = df.sort_values(by='date')

  red_fighters_elo = []; blue_fighters_elo =[]
  elos = initalise_elos(df)
  for index, row in df.iterrows():

    red_fighter = row['R_fighter']; blue_fighter = row['B_fighter']; winner = row['Winner']
    red_fight_num = row['R_Fight_Number']; blue_fight_num = row['B_Fight_Number']

    if red_fight_num <= 3:
      red_k = 275
    else:
      red_k = 155

    if blue_fight_num <= 3:
      blue_k = 275
    else:
      blue_k = 155

    red_fighter_update, blue_fighter_update = compute_updates(red_fighter, blue_fighter, winner , elos, red_k, blue_k)
    
    # Multiplier for the severity of the way in which the fighter won the bout
    if row['win_by'] == 'Decision - Split':
      
      if winner == 'red':
        elos[red_fighter]  += 0.67*red_fighter_update
        elos[blue_fighter] += 0.33*blue_fighter_update
      
      else:
        elos[red_fighter]  += 0.33*red_fighter_update
        elos[blue_fighter] += 0.67*blue_fighter_update

    elif row['win_by'] == 'Decision - Majority':

      if winner == 'red':
        elos[red_fighter]  += 0.83*red_fighter_update
        elos[blue_fighter] += 0.167*blue_fighter_update
      
      else:
        elos[red_fighter]  += 0.167*red_fighter_update
        elos[blue_fighter] += 0.83*blue_fighter_update

    else:
      elos[red_fighter]  += red_fighter_update
      elos[blue_fighter] += blue_fighter_update


    red_fighters_elo.append(elos[red_fighter])
    blue_fighters_elo.append(elos[blue_fighter])

  df['red_fighters_elo']  = red_fighters_elo
  df['blue_fighters_elo'] = blue_fighters_elo
  
  return(df)




def calculate_expected(row):
    red = row['red_fighters_elo']
    blue = row['blue_fighters_elo']

    red_expected =  1 / (1 + 10 ** ((blue - red) / 400))
    blue_expected = 1 - red_expected
    return red_expected, blue_expected