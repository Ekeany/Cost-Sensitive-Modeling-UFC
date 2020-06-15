import numpy as np
import pandas as pd

class Encoder:

  def __init__(self, df):
    self.df = df

  @property
  def encode_weight_class(self):
    weight_class_mapping = {"Women's Strawweight":115, "Women's Flyweight":125, "Women's Bantamweight":135,
                            "Strawweight":115, "Flyweight":125, "Bantamweight":135,
                            "Featherweight":145, "Lightweight":155, "Welterweight":170,
                            "Middleweight":185, "Light Heavyweight":205, "Heavyweight":265,
                            "Catch Weight":265}
                          
    self.df['weight_class'] = self.df['weight_class'].map(weight_class_mapping)

  @property
  def encode_title_bout(self):
    title_bout_mapping = {True:1, False:0}
    self.df['title_bout_encoded'] = self.df['title_bout'].map(title_bout_mapping)

  @property
  def encode_winner(self):
    winner_mapping = {'Red':1, 'Blue':0}
    self.df['Winner_encoded'] = self.df['Winner'].map(winner_mapping)
  
  @property
  def Difference_in_stances(self):

    different_stance_mapping = {True:1, False:0}
    red_stance  = self.df['R_Stance'].values
    blue_stance = self.df['B_Stance'].values

    self.df['Difference_in_stance'] = np.equal(red_stance, blue_stance)
    self.df['Difference_in_stance'] = self.df['Difference_in_stance'].map(different_stance_mapping)

    self.df.drop(['R_Stance','B_Stance'],axis=1,inplace=True)