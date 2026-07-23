
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

CORS_ALLOWED_ORIGINS = [
    "https://mlinzi-theta.vercel.app",
    "https://mlinzi-tau.vercel.app",
    "http://localhost:5173",
]

from velocity_detection import velocity
from repeated_withdrawal import repeated

app = FastAPI(
    title="Mlinzi Fraud Detection API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Mlinzi Fraud Detection API"}


@app.get("/velocity")
def velocity_detection():
    transactions = velocity.load_transactions()
    flagged = velocity.detect_velocity(transactions)
    return flagged

@app.get("/repeated_withdrawals")
def repeated_withdrawals_detection(
    tolerance_type: str = "fixed",
    tolerance_value: float = 1000,
):
    transactions = repeated.load_transactions()

    flagged = repeated.detect_repeated_withdrawals(
        transactions=transactions,
        tolerance_type=tolerance_type,
        tolerance_value=tolerance_value,
    )

    return flagged

