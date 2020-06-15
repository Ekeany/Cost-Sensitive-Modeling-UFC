import numpy as np
import pandas as pd

class Subset:

  def __init__(self, df):
    self.df = df


  def subset_on_number_of_fights(self, number_of_fights):
    print('Original Shape with all fights: ' + str(self.df.shape))
    self.df = self.df[(self.df.R_Fight_Number > number_of_fights) &
              (self.df.B_Fight_Number > number_of_fights)]
    print('New Shape with fighters over ' + str(number_of_fights) + ' fights ' + str(self.df.shape))
 
  @property
  def subset_on_draws(self):
    print('Original Shape including Draws: ' + str(self.df.shape))
    self.df = self.df[self.df.Winner != 'Draw'].copy()
    print('New Shape with excluding draws' + str(self.df.shape))