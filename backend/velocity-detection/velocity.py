"""
Velocity detection 
Reads a transaction csv file, flags transactions that are part of a define 
high number of transactions made by the same customer within a short time window.

DuckDB is used to query the csv file directly,enabling fast analytical queries without needing a separate data-loading step.
  
"""

import duckdb
from pathlib import Path 

N_THRESHOLD = 5 # more than the transactions
X_HOURS = 2 # within this hours triggers a flag 

RULE_NAME = 'velocity'

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR.parent.parent /"data"/ "mlinzi_sample_transactions.csv"

def rows_as_dicts(conn: duckdb.DuckDBPyConnection) -> list[dict]:
    """Convert DuckDB query results into a list of dictionaries."""
    columns = [column[0] for column in conn.description]
    return [dict(zip(columns, row)) for row in conn.fetchall()]

def load_transactions(conn: duckdb.DuckDBPyConnection) -> list[dict]:
    """
    Read the transaction csv file using DuckDB and execute the sql query.
    """
    conn.execute(
        """
         SELECT 
           customer_id,
           transaction_id,
           timestamp
        FROM read_csv(?, header=True)
        """,
        [str(DATA_FILE)],
    )
    return rows_as_dicts(conn)
    