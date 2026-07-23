from sorting.sorter import Adapter
import pandas
from pathlib import Path
import sys
from collections import defaultdict
from datetime import timedelta


BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))
DATA_FILE = BACKEND_DIR.parent / "data" / "mlinzi_sample_transactions.csv"

WITHDRAWAL_COUNT_THRESHOLD = 5
TIME_WINDOW_HOURS = 2
AMOUNT_TOLERANCE = 1000


def load_transactions() -> list[dict]:
    adapter = Adapter(
        path=str(DATA_FILE), sort_by="customer_id", amount_col="amount_kes", min_value=0
    )

    df = adapter.get_all()

    df["timestamp"] = pandas.to_datetime(df["timestamp"])

    withdrawals = df[df["transaction_type"] == "Withdrawal"]

    return withdrawals.to_dict("records")


def detect_repeated_withdrawals(transactions: list[dict]) -> list[dict]:

    customers = defaultdict(list)

    for transaction in transactions:
        customer_id = transaction["customer_id"]
        customers[customer_id].append(transaction)
    window_size_limit = timedelta(hours=TIME_WINDOW_HOURS)
    flagged_transactions = []

    flagged_transaction_ids = set()

    for customer_id, customer_transactions in customers.items():
        sorted_transactions = sorted(
            customer_transactions, key=lambda transaction: transaction["timestamp"]
        )
        window_start_index = 0

        for window_end_index in range(len(sorted_transactions)):
            current_transaction = sorted_transactions[window_end_index]

            while (
                current_transaction["timestamp"]
                - sorted_transactions[window_start_index]["timestamp"]
                > window_size_limit
            ):
                window_start_index += 1
            current_window = sorted_transactions[
                window_start_index : window_end_index + 1
            ]

            amount_buckets = defaultdict(list)

            for transaction in current_window:
                amount = transaction["amount_kes"]

                amount_bucket = amount // AMOUNT_TOLERANCE

                amount_buckets[amount_bucket].append(transaction)

            for amount_bucket, bucket_transaction in amount_buckets.items():
                if len(bucket_transaction) >= WITHDRAWAL_COUNT_THRESHOLD:
                    for flagged_transaction in bucket_transaction:
                        transaction_id = flagged_transaction["transaction_id"]

                        if transaction_id in flagged_transaction_ids:
                            continue

                        flagged_transaction_ids.add(transaction_id)

                        flagged_transaction["anomalyType"] = "Repeated Withdrawals"
                        flagged_transaction["severity"] = (
                            "HIGH" if len(bucket_transaction) < 8 else "CRITICAL"
                        )
                        flagged_transaction["status"] = "Flagged"
                        flagged_transaction["reason"] = (
                            f"Repeated withdrawal: KES {
                                bucket_transaction[0]['amount_kes']:,} × "
                            f"{len(bucket_transaction)} in {TIME_WINDOW_HOURS}h"
                        )
                    flagged_transaction["flag"] = "repeated"
                    flagged_transaction["date_flagged"] = pandas.Timestamp.now(
                        tz="UTC"
                    ).isoformat()

                    flagged_transactions.append(flagged_transaction)
        return flagged_transactions


if __name__ == "__main__":
    transactions = load_transactions()

    flagged = detect_repeated_withdrawals(transactions)

    print(flagged)
