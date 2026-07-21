from fastapi import FastAPI
from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))


from velocity_detection import velocity
from repeated_withdrawal import repeated

app = FastAPI(
    title="Mlinzi Fraud Detection API",
    version="1.0.0",
)

@app.get("/")
def home():
    return {
        "message": "Mlinzi Fraud Detection API"
    }

@app.get("/velocity")
def velocity_detection():
    transactions = velocity.load_transactions()
    flagged = velocity.detect_velocity(transactions)
    return flagged

@app.get("/repeated_withdrawals")
def repeated_withdrawals_detection():
    transactions = repeated.load_transactions()
    flagged = repeated.detect_repeated_withdrawals(transactions)
    return flagged