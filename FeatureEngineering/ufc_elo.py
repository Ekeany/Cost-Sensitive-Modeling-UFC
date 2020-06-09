import numpy as np
import pandas as pd

def expected(A, B):
    return 1 / (1 + 10 ** ((B - A) / 400))

def elo(exp, score, k):
    return(k * (score - exp))

def initalise_elos(df):

  Red_fighters  = list(df['R_fighter'].values)
  Blue_fighters = list(df['B_fighter'].values)
  All_fighters  = Red_fighters + Blue_fighters

  unique_fighters = list(set(All_fighters))
  constant_elo    = [1200]*len(unique_fighters)

  return(dict(zip(unique_fighters, constant_elo)))

def compute_updates(red_fighter, blue_fighter, winner , elos, k):

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
  return(elo(expectation_red, red_win_lose, k),
         elo(expectation_blue, blue_win_lose, k))

def calculate_elos(df, k):

  df = df.sort_values(by='date')

  red_fighters_elo = []; blue_fighters_elo =[]
  elos = initalise_elos(df)
  for index, row in df.iterrows():

    red_fighter = row['R_fighter']; blue_fighter = row['B_fighter']; winner = row['Winner']
    red_fighter_update, blue_fighter_update = compute_updates(red_fighter, blue_fighter, winner , elos, k)
    
    # Multiplier for the severity of the way in which the fighter won the bout
    if((row['win_by'] == 'Decision - Unanimous') |
       (row['win_by'] == 'KO/TKO') | 
       (row['win_by'] == 'Submission')):
      
      elos[red_fighter]  += 2.9*red_fighter_update
      elos[blue_fighter] += 2.9*blue_fighter_update
    else:

      elos[red_fighter]  += red_fighter_update
      elos[blue_fighter] += blue_fighter_update

    red_fighters_elo.append(elos[red_fighter])
    blue_fighters_elo.append(elos[blue_fighter])

  df['red_fighters_elo']  = red_fighters_elo
  df['blue_fighters_elo'] = blue_fighters_elo
  
  return(df)

def compute_least_squares(epxred,obsred,epxblue,obsblue):
  return ((epxred - obsred)**2) + ((epxblue - obsblue)**2)


def calculate_optimal_k_value(df):

  df = df.sort_values(by='date')
  all_errors = []
  for bonus in tqdm(range(10,40)):
    totalerror = []
    for k in range(100):
      red_fighters_elo = []; blue_fighters_elo =[]
      elos = initalise_elos(df); error = []
      for index, row in df.iterrows():

        red_fighter = row['R_fighter']; blue_fighter = row['B_fighter']; winner = row['Winner']
        red_fighter_update, blue_fighter_update = compute_updates(red_fighter, blue_fighter, winner , elos, k)

        if winner == 'Red':
          red_win_lose  = 1
          blue_win_lose = 0
        elif winner == 'Blue':
          red_win_lose  = 0
          blue_win_lose = 1
        else:
          red_win_lose  = 0.5
          blue_win_lose = 0.5

        expectation_red  = expected(elos[red_fighter], elos[blue_fighter])
        expectation_blue = 1 - expectation_red

        error_ = compute_least_squares(expectation_red,red_win_lose,expectation_blue,blue_win_lose)
        error.append(error_)

        # Multiplier for the severity of the way in which the fighter won the bout
        if((row['win_by'] == 'Decision - Unanimous') |
          (row['win_by'] == 'KO/TKO') | 
          (row['win_by'] == 'Submission')):
      
          elos[red_fighter]  += (bonus/10)*red_fighter_update
          elos[blue_fighter] += (bonus/10)*blue_fighter_update
        else:

          elos[red_fighter]  += red_fighter_update
          elos[blue_fighter] += blue_fighter_update
    
      totalerror.append(sum(error))
    all_errors.append(totalerror)
  #return(totalerror, list(range(0, 100)))
  return(all_errors)

def generalised_calculate_elos(df, k, win_column, red_column_name, blue_column_name, optimize = False):

  df = df.sort_values(by='date')

  red_fighters_elo = []; blue_fighters_elo =[]
  elos = initalise_elos(df); error = []
  for index, row in df.iterrows():

    red_fighter = row['R_fighter']; blue_fighter = row['B_fighter']; winner = row[win_column]
    red_fighter_update, blue_fighter_update = compute_updates(red_fighter, blue_fighter, winner , elos, k)
    
    elos[red_fighter]  += red_fighter_update
    elos[blue_fighter] += blue_fighter_update

    if winner == 'Red':
      red_win_lose  = 1
      blue_win_lose = 0
    elif winner == 'Blue':
      red_win_lose  = 0
      blue_win_lose = 1
    else:
      red_win_lose  = 0.5
      blue_win_lose = 0.5

    expectation_red  = expected(elos[red_fighter], elos[blue_fighter])
    expectation_blue = 1 - expectation_red

    error_ = compute_least_squares(expectation_red,red_win_lose,expectation_blue,blue_win_lose)
    error.append(error_)

    red_fighters_elo.append(elos[red_fighter])
    blue_fighters_elo.append(elos[blue_fighter])

  if optimize:
    return(sum(error))
  else:
    df[red_column_name]  = red_fighters_elo
    df[blue_column_name] = blue_fighters_elo
    return(df)

def optimize(df, win_column):

  error = []
  for k in tqdm(range(200)):
    error_ = generalised_calculate_elos(df, k, win_column, optimize = True)
    error.append(error_)

  print(error)
  print(np.argmin(np.array(error)))
