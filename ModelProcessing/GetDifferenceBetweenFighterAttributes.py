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


    @property
    def get_difference_between_fighters_stats(self):
  
      my_copy = self.df.copy()
      my_copy.drop(['R_fighter','B_fighter','date',
                    'Average_Odds_f1', 'Average_Odds_f2',
                    'win_by','weight_class','Winner',
                    'R_win_by_Decision_Majority',
                    'R_win_by_Decision_Split', 'R_win_by_Decision_Unanimous',
                    'R_win_by_KO/TKO', 'R_win_by_Submission',
                    'R_win_by_TKO_Doctor_Stoppage','B_win_by_Decision_Majority',
                    'B_win_by_Decision_Split', 'B_win_by_Decision_Unanimous',
                    'B_win_by_KO/TKO', 'B_win_by_Submission',
                    'B_win_by_TKO_Doctor_Stoppage'], axis=1, inplace=True)
      
      red_columns = self.find_red_columns(my_copy.columns)
      for red_col in red_columns:

        blue_col = self.find_pairing_column_name(red_col)
        new_col_name = self.new_column_name(red_col)

        self.df[new_col_name] = my_copy[red_col] - my_copy[blue_col]

      return self.df