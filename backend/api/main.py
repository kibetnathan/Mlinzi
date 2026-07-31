from backend.api.app.routes import users
from velocity_detection.velocity import load_transactions, detect_velocity
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys
from api.app.routes import transactions ,users


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from velocity_detection.velocity import detect_velocity, load_transactions

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))


CORS_ALLOWED_ORIGINS = [
    "https://mlinzi-theta.vercel.app",
    "https://mlinzi-tau.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # React default if applicable
    "http://127.0.0.1:3000",
]

from repeated_withdrawal import repeated
from round_number_anomaly import round_number_anomaly

app = FastAPI(
    title="Mlinzi Fraud Detection API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(transactions.router)
app.include_router(users.router)



@app.get("/")
def home():
    return {"message": "Mlinzi Fraud Detection API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

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

@app.get("/round_number_anomalies")
def round_number_anomalies_detection():
    """Detect accounts with suspicious clusters of round-number transactions."""
    transactions = round_number_anomaly.load_transactions()
    flagged = round_number_anomaly.detect_round_number_anomalies(transactions)
    return flagged

