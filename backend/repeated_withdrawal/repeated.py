
import pandas
from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))
DATA_FILE = BACKEND_DIR.parent / "data" / "mlinzi_sample_transactions.csv"
from sorting.sorter import Adapter

def load_transactions() -> list[dict]:
    adapter = Adapter(
        path = str(DATA_FILE),
        sort_by= 'customer_id',
        amount_col= 'amount_kes',
        min_value=0
    )

    df = adapter.get_all()

    df['timestamp'] = pandas.to_datetime(df['timestamp'])

    withdrawals = df[df['transaction_type'] == 'Withdrawal']

    return withdrawals.to_dict('records')

transactions = load_transactions()

for transaction in transactions:
    print(transaction)

