import pandas
from pathlib import Path
import sys
from collections import defaultdict
from datetime import timedelta


BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

DATA_FILE = BACKEND_DIR.parent / "data" / "mlinzi_sample_transactions.csv"

from sorting.sorter import Adapter


WITHDRAWAL_COUNT_THRESHOLD = 5
TIME_WINDOW_HOURS = 2


def load_transactions() -> list[dict]:
    adapter = Adapter(
        path=str(DATA_FILE),
        sort_by="customer_id",
        amount_col="amount_kes",
        min_value=0,
    )

    df = adapter.get_all()

    df["timestamp"] = pandas.to_datetime(df["timestamp"])

    withdrawals = df[
        df["transaction_type"] == "Withdrawal"
    ]

    return withdrawals.to_dict("records")


def calculate_tolerance(
    amount: float,
    tolerance_type: str,
    tolerance_value: float,
) -> float:
    """
    Calculate the allowed amount difference based on
    the tolerance configuration selected by the analyst.

    fixed:
        tolerance_value represents a fixed KES amount.

        Example:
            amount = 50,000
            tolerance_value = 1,000

            Allowed range:
            49,000 to 51,000

    percentage:
        tolerance_value represents a percentage.

        Example:
            amount = 50,000
            tolerance_value = 5

            Allowed range:
            47,500 to 52,500
    """

    if tolerance_type == "fixed":
        return tolerance_value

    if tolerance_type == "percentage":
        return amount * (tolerance_value / 100)

    raise ValueError(
        "tolerance_type must be either 'fixed' or 'percentage'"
    )


def amounts_are_similar(
    first_amount: float,
    second_amount: float,
    tolerance_type: str,
    tolerance_value: float,
) -> bool:
    """
    Determine whether two withdrawal amounts are similar
    according to the analyst's selected tolerance.
    """

    tolerance = calculate_tolerance(
        amount=first_amount,
        tolerance_type=tolerance_type,
        tolerance_value=tolerance_value,
    )

    lower_bound = first_amount - tolerance
    upper_bound = first_amount + tolerance

    return lower_bound <= second_amount <= upper_bound


def detect_repeated_withdrawals(
    transactions: list[dict],
    tolerance_type: str,
    tolerance_value: float,
) -> list[dict]:
    """
    Detect repeated withdrawals made by the same customer.

    A transaction is flagged when at least
    WITHDRAWAL_COUNT_THRESHOLD transactions have:

    1. The same customer.
    2. Occurred within TIME_WINDOW_HOURS.
    3. Similar withdrawal amounts according to the
       analyst-selected tolerance.
    """

    if tolerance_type not in {"fixed", "percentage"}:
        raise ValueError(
            "tolerance_type must be either 'fixed' or 'percentage'"
        )

    if tolerance_value <= 0:
        raise ValueError(
            "tolerance_value must be greater than 0"
        )

    if tolerance_type == "percentage" and tolerance_value > 100:
        raise ValueError(
            "percentage tolerance cannot be greater than 100"
        )

    customers = defaultdict(list)

    # Group transactions by customer.
    for transaction in transactions:
        customer_id = transaction["customer_id"]
        customers[customer_id].append(transaction)

    window_size_limit = timedelta(
        hours=TIME_WINDOW_HOURS
    )

    flagged_transactions = []
    flagged_transaction_ids = set()

    # Analyze each customer independently.
    for customer_id, customer_transactions in customers.items():

        sorted_transactions = sorted(
            customer_transactions,
            key=lambda transaction: transaction["timestamp"],
        )

        window_start_index = 0

        # Move through the customer's transactions.
        for window_end_index in range(
            len(sorted_transactions)
        ):
            current_transaction = sorted_transactions[
                window_end_index
            ]

            # Move the start of the window forward until
            # all transactions are within the configured
            # time window.
            while (
                current_transaction["timestamp"]
                - sorted_transactions[
                    window_start_index
                ]["timestamp"]
                > window_size_limit
            ):
                window_start_index += 1

            current_window = sorted_transactions[
                window_start_index : window_end_index + 1
            ]

            similar_transactions = []

            # Compare the current transaction against
            # transactions inside the current time window.
            for transaction in current_window:

                if amounts_are_similar(
                    first_amount=current_transaction[
                        "amount_kes"
                    ],
                    second_amount=transaction[
                        "amount_kes"
                    ],
                    tolerance_type=tolerance_type,
                    tolerance_value=tolerance_value,
                ):
                    similar_transactions.append(
                        transaction
                    )

            # Flag the group if enough similar withdrawals
            # exist within the time window.
            if (
                len(similar_transactions)
                >= WITHDRAWAL_COUNT_THRESHOLD
            ):

                for transaction in similar_transactions:

                    transaction_id = transaction[
                        "transaction_id"
                    ]

                    # Prevent the same transaction from
                    # being returned multiple times.
                    if (
                        transaction_id
                        in flagged_transaction_ids
                    ):
                        continue

                    flagged_transaction_ids.add(
                        transaction_id
                    )

                    transaction["reason"] = (
                        f"Repeated withdrawals: "
                        f"{len(similar_transactions)} "
                        f"withdrawals of similar amount "
                        f"within {TIME_WINDOW_HOURS} hours "
                        f"using {tolerance_type} tolerance "
                        f"of {tolerance_value}"
                    )

                    flagged_transactions.append(
                        transaction
                    )

    return flagged_transactions


if __name__ == "__main__":

    transactions = load_transactions()

    # Analyst chooses a fixed KES tolerance.
    flagged = detect_repeated_withdrawals(
        transactions=transactions,
        tolerance_type="fixed",
        tolerance_value=1000,
    )

    print("\nFLAGGED TRANSACTIONS:")

    for transaction in flagged:
        print(transaction)