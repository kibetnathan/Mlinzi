import pandas

from repeated import detect_repeated_withdrawals


test_transactions = [
    {
        "transaction_id": "TXN001",
        "customer_id": "CUST_TEST",
        "timestamp": pandas.Timestamp("2026-01-07 10:00:00"),
        "amount_kes": 3100,
        "transaction_type": "Withdrawal",
    },
    {
        "transaction_id": "TXN002",
        "customer_id": "CUST_TEST",
        "timestamp": pandas.Timestamp("2026-01-07 10:15:00"),
        "amount_kes": 3500,
        "transaction_type": "Withdrawal",
    },
    {
        "transaction_id": "TXN003",
        "customer_id": "CUST_TEST",
        "timestamp": pandas.Timestamp("2026-01-07 10:30:00"),
        "amount_kes": 3900,
        "transaction_type": "Withdrawal",
    },
    {
        "transaction_id": "TXN004",
        "customer_id": "CUST_TEST",
        "timestamp": pandas.Timestamp("2026-01-07 10:45:00"),
        "amount_kes": 3200,
        "transaction_type": "Withdrawal",
    },
    {
        "transaction_id": "TXN005",
        "customer_id": "CUST_TEST",
        "timestamp": pandas.Timestamp("2026-01-07 11:00:00"),
        "amount_kes": 3800,
        "transaction_type": "Withdrawal",
    },
]


flagged = detect_repeated_withdrawals(test_transactions)

print("Number of flagged transactions:", len(flagged))

for transaction in flagged:
    print(transaction)