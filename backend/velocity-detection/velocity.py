"""
Velocity detection 
Reads a transaction csv file, flags transactions that are part of a define 
high number of transactions made by the same customer within a short time window.

DuckDB is used to query the csv file directly,enabling fast analytical queries without needing a separate data-loading step.
  
"""

import duckdb
from pathlib import Path 
from collections import defaultdict
from datetime import timedelta

N_THRESHOLD = 5 # more than the transactions
X_HOURS = 2 # within this hours triggers a flag 



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
           CAST(timestamp AS TIMESTAMP) AS timestamp
        FROM read_csv(?, header=True)
        """,
        [str(DATA_FILE)],
    )
    return rows_as_dicts(conn)

def detect_velocity(transactions: list[dict]) -> list[dict]:
  """
   Detect customers who exceed the velocity threshold .

   A customer is flagged when the have more than n_threshold transaction 
   within the x_hours window. 
  """
  customers = defaultdict(list)
  for transaction in transactions:
     customer_id = transaction["customer_id"]
     customers[customer_id]. append(transaction)
  window_size_limit = timedelta(hours=X_HOURS)
  flagged_transactions = []

  flagged_transaction_ids = set()

  for customer_id, customer_transaction in customers.items():
     sorted_transactions = sorted(
        customer_transaction, key=lambda transaction: transaction["timestamp"]
     )
     window_start_index = 0
     for window_end_index in range(len(sorted_transactions)):
        current_transaction = sorted_transactions[window_end_index]

        while(
            current_transaction["timestamp"]
            - sorted_transactions[window_start_index]["timestamp"]
            > window_size_limit
        ):
           window_start_index += 1
        transactions_in_window = window_end_index - window_start_index + 1
        
        if transactions_in_window > N_THRESHOLD:
                   
            for flagged_transaction in sorted_transactions[
                window_start_index : window_end_index + 1
            ]:
                transaction_id = flagged_transaction["transaction_id"]
                if transaction_id in flagged_transaction_ids:
                    continue  

                flagged_transaction_ids.add(transaction_id)
                flagged_transaction["reason"] = (
                    f"High transaction frequency: {transactions_in_window} "
                    f"transactions in {X_HOURS} hours"
                )
                flagged_transactions.append(flagged_transaction)
        
  return flagged_transactions

if __name__ == "__main__":
   conn = duckdb.connect()

   transactions = load_transactions(conn)
   flagged = detect_velocity(transactions)
 
   print(type(flagged))
   print(len(flagged))

   for transaction in flagged:
    print(transaction)