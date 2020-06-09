from trueskill import Rating, rate_1vs1
import pandas as pd
import numpy as np

def initalise_ratings(df):

  Red_fighters  = list(df['R_fighter'].values)
  Blue_fighters = list(df['B_fighter'].values)
  All_fighters  = Red_fighters + Blue_fighters

  unique_fighters = list(set(All_fighters))
  inital_rating   = [Rating()]*len(unique_fighters)

  return(dict(zip(unique_fighters, inital_rating)))


def compute_update(Red_fighter, Blue_fighter, winner, ratings):

  if winner == 'Red':
    ratings[Red_fighter], ratings[Blue_fighter] = rate_1vs1(ratings[Red_fighter], 
                                                            ratings[Blue_fighter])
  elif winner == 'Blue':
    ratings[Blue_fighter], ratings[Red_fighter] = rate_1vs1(ratings[Blue_fighter], 
                                                            ratings[Red_fighter])
  elif winner == 'Draw':
    ratings[Blue_fighter], ratings[Red_fighter] = rate_1vs1(ratings[Blue_fighter], 
                                                            ratings[Red_fighter],
                                                            drawn=True)
  else:
    pass

  return ratings


def calculate_skill(df, winner_column, red_skill, blue_skill):

  df = df.sort_values(by='date')
  ratings = initalise_ratings(df)
  red_fighters_ratings = []; blue_fighters_ratings =[]

  for index, row in df.iterrows():

    red_fighter = row['R_fighter']; blue_fighter = row['B_fighter']; winner = row[winner_column]
    ratings = compute_update(red_fighter, blue_fighter, winner, ratings)

    red_fighters_ratings.append(ratings[red_fighter].mu)
    blue_fighters_ratings.append(ratings[blue_fighter].mu)

  df[red_skill]  = red_fighters_ratings
  df[blue_skill] = blue_fighters_ratings

  return(df)