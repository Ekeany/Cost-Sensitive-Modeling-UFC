import numpy as np
import pandas as pd
import re


class GetTheDifferenceBetweenFighterAttributes:

    def __init__(self, df):
      self.df = df
      

    @staticmethod
    def lreplace(pattern, sub, string):
      """
      Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
      """
      return re.sub('^%s' % pattern, sub, string)


    def find_pairing_column_name(self, col_name):
      if 'R_' in col_name:
        return self.lreplace('R_', 'B_', col_name)
      else:
        return col_name.replace('red_','blue_')


    @staticmethod
    def find_red_columns(df, columns_we_want):

      red_columns = []
      dtypes = columns_we_want.select_dtypes([np.int, np.float]).dtypes
      for col in dtypes.index:
        if('R_' in col) | ('red_' in col):
          red_columns.append(col)
        else:
          pass
      
      return red_columns


    
    def new_column_name(self, col_name):
      if 'R_' in col_name:
        return self.lreplace('R_', 'difference_', col_name)
      else:
        return col_name.replace('red_','difference_')



    def get_difference_between_fighters_stats(self, cols_to_keep_whole):
  
      self.my_copy = self.df.copy()
      self.my_copy.drop(cols_to_keep_whole, axis=1, inplace=True)
      
      red_columns = self.find_red_columns(self.df, self.my_copy)
      for red_col in red_columns:

        blue_col = self.find_pairing_column_name(red_col)
        new_col_name = self.new_column_name(red_col)

        self.df[new_col_name] = self.my_copy[red_col] - self.my_copy[blue_col]



    def drop_solo_columns(self):
      self.df.drop(self.my_copy.columns.to_list(), axis=1, inplace=True)


    def get_data(self):
      return self.df 