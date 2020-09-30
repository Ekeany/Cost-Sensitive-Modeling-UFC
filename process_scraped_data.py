from PreProcessing.Preprocessing import Preprocessing
from PreProcessing.Odds_processing import process_odds

print('Started Preprocessing')
Preprocessing()

print('processing odds')
process_odds(path_to_files='C:/Users/egnke/PythonCode/UFC/Cost-Sensitive-Modeling-UFC/data/odds_data/',
            output_file='C:/Users/egnke/PythonCode/UFC/Cost-Sensitive-Modeling-UFC/data/best_fight_odds.csv')
