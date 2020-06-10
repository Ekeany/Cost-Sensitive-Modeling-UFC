import numpy as np
import pandas as pd
from tqdm import tqdm


def stats_of_previous_fighters_who_they_beat(df, fighter):

    blue_cols = [df['blue_Fighter_Odds'], df['B_Takedown Accuracy'],
                df['B_age'],   df['B_RingRust'],
                df['B_Striking Defense'], df['B_Takedown_Defense'],
                df['blue_skill'],  df['striking_blue_skill'],
                df['wrestling_blue_skill'],  df['B_Power_Rating'],
                df['g_and_p_blue_skill'], df['jiujitsu_blue_skill'],
                df['B_Strikes_Absorbed_per_Minute'], df['B_AVG_fight_time']]

    red_cols  = [df['red_Fighter_Odds'], df['R_Takedown Accuracy'],
                df['R_age'],   df['R_RingRust'],
                df['R_Striking Defense'], df['R_Takedown_Defense'],
                df['red_skill'],  df['striking_red_skill'],
                df['wrestling_red_skill'],  df['R_Power_Rating'],
                df['g_and_p_red_skill'], df['jiujitsu_red_skill'],
                df['R_Strikes_Absorbed_per_Minute'], df['R_AVG_fight_time']]

    if df.R_fighter == fighter and df.Winner == 'Red':
        won, lost = blue_cols , ''
    
    elif df.B_fighter == fighter and df.Winner == 'Blue':
        won, lost = red_cols , ''
        
    elif df.Winner == 'Draw' or df.win_by == 'DQ':
        won, lost = '',''
    
    elif df.B_fighter == fighter and df.Winner == 'Red':
        won, lost = '', red_cols

    elif df.R_fighter == fighter and df.Winner == 'Blue':
        won, lost = '', blue_cols
    
    return(won, lost)