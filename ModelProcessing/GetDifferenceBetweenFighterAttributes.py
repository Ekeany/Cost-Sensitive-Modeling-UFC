import numpy as np
import pandas as pd


class GetTheDifferenceBetweenFighterAttributes:

    def __init__(self, df):
      self.df = df


    @staticmethod
    def find_pairing_column_name(col_name):
      if 'R_' in col_name:
        return col_name.replace('R_','B_')
      else:
        return col_name.replace('red_','blue_')


    @staticmethod
    def find_red_columns(all_columns):

      red_columns = []
      for col in all_columns:
        if('R_' in col) | ('red_' in col):
          red_columns.append(col)
        else:
          pass
      
      return red_columns


    @staticmethod
    def new_column_name(col_name):
      if 'R_' in col_name:
        return col_name.replace('R_','difference_')
      else:
        return col_name.replace('red_','difference_')


    def get_difference_between_fighters_stats(self, cols_to_keep_whole):
  
      self.my_copy = self.df.copy()
      self.my_copy.drop(cols_to_keep_whole, axis=1, inplace=True)
      
      red_columns = self.find_red_columns(self.my_copy.columns)
      for red_col in red_columns:

        blue_col = self.find_pairing_column_name(red_col)
        new_col_name = self.new_column_name(red_col)

        self.df[new_col_name] = self.my_copy[red_col] - self.my_copy[blue_col]



    def drop_solo_columns(self):
        self.df.drop(self.my_copy.columns.to_list(), axis=1, inplace=True)
        return self.df
