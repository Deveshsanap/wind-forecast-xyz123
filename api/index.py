import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Force Python to recognize the root directory so it can find the 'backend' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now these imports will work in the cloud
from backend.app.elexon_client import ElexonClient
from backend.app.processing import process_forecast_accuracy
from backend.app.config import settings

app = FastAPI(title="Wind Forecast Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "vercel-serverless-backend"}

@app.get("/api/analysis/january-2026")
async def get_january_analysis():
    client = ElexonClient()
    try:
        actuals = await client.get_actual_wind_generation("2026-01-01", "2026-01-31")
        forecasts = await client.get_forecast_wind_generation("2025-12-25T00:00:00Z", "2026-01-31T23:59:59Z")
        
        result = process_forecast_accuracy(actuals, forecasts, settings.decision_cutoff_time)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()