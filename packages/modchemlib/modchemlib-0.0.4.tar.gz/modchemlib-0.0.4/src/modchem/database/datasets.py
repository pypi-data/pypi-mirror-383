import pandas as pd
import os

def periodic_table():
   df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'redox_periodictable.csv'))
   return df
        
    