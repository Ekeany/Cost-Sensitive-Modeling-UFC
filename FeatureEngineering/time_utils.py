import numpy as np
import pandas as pd

def Time_difference_days(d1,d2):
    return abs((d2 - d1)/np.timedelta64(1, 'D'))

def Time_difference_between_consectuive_dates_in_column(df, column):
  diff = Time_difference_days(df[column],df[column].shift()).fillna(0)
  return(diff)
