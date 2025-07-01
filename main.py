from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fitbit_router import router as fitbit_router

app = FastAPI(
    title="Fitbit API",
    description="API for accessing Fitbit",
    version="1.0.0"
)

app.include_router(fitbit_router, prefix="/fitbit", tags=["Fitbit"])
@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <h1>Fitbit LLM Integration</h1>
    <a href='/fitbit/auth/fitbit/start'>Connect to Fitbit</a>
    """
