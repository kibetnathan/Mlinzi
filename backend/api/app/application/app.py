from fastapi import FastAPI
# from ..routes.routes import router as router


def create_app() -> FastAPI:
    """
    Application factory function.
    Instantiates and configures the FastAPI app instance
    """

    app = FastAPI(title="Mlinzi Fraud Detection")

    # app.include_router(router)
    return app
