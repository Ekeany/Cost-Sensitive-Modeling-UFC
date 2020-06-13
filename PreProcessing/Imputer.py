import pandas as pd
import numpy as np
from tqdm import tqdm

class Imputer:

  def __init__(self, df):
    self.df = df


  def impute(self, fill_type):
    '''
    back fill and forward fill any missing values as the missing values 
    are for takedowns etc or attributes they may not happen in the fight.
    '''
    
    Red_fighters  = list(self.df['R_fighter'].values)
    Blue_fighters = list(self.df['B_fighter'].values)
    All_fighters  = Red_fighters + Blue_fighters

    unique_fighters = list(set(All_fighters))
    self.df = self.df.sort_values(by='date')
    for fighter in tqdm(unique_fighters):

      try:
        self.df[(self.df.R_fighter == fighter)|(self.df.B_fighter == fighter)] = self.df[(self.df.R_fighter == fighter)|(self.df.B_fighter == fighter)].fillna(method=fill_type)
      
      except:
        pass

    return self.df


  def impute_missing_values(self):

    na_cols = self.find_columns_with_missing_values()
    if len(na_cols) != 0:
      print('These Columns have Missing Values' + str(na_cols))
      for col in na_cols:
        self.impute_using_group(col, impute_type = 'median')

    else:
      pass

    return self.df


  def find_columns_with_missing_values(self):
    return self.df.columns[self.df.isnull().any()].tolist()

  
  def impute_using_group(self, col, impute_type = 'median'):
    '''
    mainly for takedowns as some
    fighters never engage in wrestling
    '''
    self.df[col] = self.df[col].fillna(self.df.groupby('weight_class')[col].transform(impute_type))