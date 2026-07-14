"""
Velocity detection 
Reads a transaction csv file, flags transactions that are part of a define 
high number of transactions made by the same customer within a short time window.

DuckDB is used to query the csv file directly,enabling fast analytical queries without needing a separate data-loading step.
  
"""

import duckdb
import pandas as pd
from pathlib import path 

N_THRESHOLD = 5 # more than the transactions
X_HOURS = 2 # within this hours triggers a flag 

RULE_NAME = 'velocity'

BASE_DIR = path(__file__).resolve().parent
DATA_FILE = BASE_DIR.parent /"data"/ "transactions.csv"
