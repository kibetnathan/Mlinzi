from fastapi import FastAPI

# from ..routes.routes import router as router
from ..routes.transactions import router as transactions_router


def create_app() -> FastAPI:
    """
    Application factory function.
    Instantiates and configures the FastAPI app instance
    """

    app = FastAPI(title="Mlinzi Fraud Detection")

    # app.include_router(router)
    app.include_router(transactions_router)
    return app
