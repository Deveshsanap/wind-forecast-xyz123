import sys
import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Force path resolution to the absolute root
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

app = FastAPI(title="Wind Forecast Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attempt to load the backend modules and trap the exact error if it fails
try:
    from backend.app.elexon_client import ElexonClient
    from backend.app.processing import process_forecast_accuracy
    from backend.app.config import settings
    LOAD_ERROR = None
except Exception as e:
    LOAD_ERROR = traceback.format_exc()

@app.get("/api/health")
def health_check():
    if LOAD_ERROR:
        return {"status": "CRASH", "error": LOAD_ERROR, "path": sys.path}
    return {"status": "healthy", "service": "vercel-serverless-backend"}

@app.get("/api/analysis/january-2026")
async def get_january_analysis():
    if LOAD_ERROR:
        raise HTTPException(status_code=500, detail="Backend failed to load. Check /api/health for error trace.")
    
    client = ElexonClient()
    try:
        actuals = await client.get_actual_wind_generation("2026-01-01", "2026-01-31")
        forecasts = await client.get_forecast_wind_generation("2025-12-25T00:00:00Z", "2026-01-31T23:59:59Z")
        result = process_forecast_accuracy(actuals, forecasts, settings.decision_cutoff_time)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()