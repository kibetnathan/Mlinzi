import sys
from pathlib import Path
import pandas
from collections import defaultdict

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

DATA_FILE = BACKEND_DIR.parent / "data" / "mlinzi_sample_transactions.csv"

from sorting.sorter import Adapter


# Detection configuration
MINIMUM_ROUND_AMOUNT = 10_000
ROUND_NUMBER_FREQUENCY_THRESHOLD = 2


def load_transactions() -> list[dict]:
    adapter = Adapter(
        path=str(DATA_FILE),
        sort_by="customer_id",
        amount_col="amount_kes",
        min_value=0
    )

    df = adapter.get_all()

    df["timestamp"] = pandas.to_datetime(df["timestamp"])

    df["amount_kes"] = pandas.to_numeric(
        df["amount_kes"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    return df.to_dict("records")


def is_round_number(
    amount: float,
    minimum_amount: float
) -> bool:
    """
    Determine whether a transaction amount is a suspicious
    round number above the configured minimum amount.
    """

    if amount < minimum_amount:
        return False

    return amount % 1000 == 0


def detect_round_number_anomalies(
    transactions: list[dict]
) -> list[dict]:

    customers = defaultdict(list)

    # Group transactions by customer
    for transaction in transactions:
        customer_id = transaction["customer_id"]
        customers[customer_id].append(transaction)

    flagged_transactions = []
    flagged_transaction_ids = set()

    # Analyze each customer's transactions
    for customer_id, customer_transactions in customers.items():

        round_number_transactions = []

        # Find qualifying round-number transactions
        for transaction in customer_transactions:

            amount = transaction["amount_kes"]

            if is_round_number(
                amount=amount,
                minimum_amount=MINIMUM_ROUND_AMOUNT
            ):
                round_number_transactions.append(transaction)

        # Check whether the customer's frequency
        # exceeds the configured baseline
        if len(round_number_transactions) >= ROUND_NUMBER_FREQUENCY_THRESHOLD:

            for transaction in round_number_transactions:

                transaction_id = transaction["transaction_id"]

                # Prevent duplicate flags
                if transaction_id in flagged_transaction_ids:
                    continue

                flagged_transaction_ids.add(transaction_id)

                transaction["reason"] = (
                    f"Round-number transaction: "
                    f"{transaction['amount_kes']}"
                )

                flagged_transactions.append(transaction)

    return flagged_transactions


if __name__ == "__main__":

    transactions = load_transactions()

    flagged_transactions = detect_round_number_anomalies(
        transactions
    )

    print("\nFLAGGED TRANSACTIONS:")

    for transaction in flagged_transactions:
        print(transaction)