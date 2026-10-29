from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.elexon_client import ElexonClient
from app.processing import process_forecast_accuracy
from app.config import settings

app = FastAPI(title="Wind Forecast Dashboard API")

# Allow React frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "wind-forecast-backend"}

@app.get("/api/analysis/january-2026")
async def get_january_analysis():
    client = ElexonClient()
    
    try:
        # 1. Fetch Actuals for January 2026 (Format required by FUELHH: yyyy-MM-dd)
        actuals = await client.get_actual_wind_generation(
            start_date="2026-01-01",
            end_date="2026-01-31"
        )
        
        # 2. Fetch Forecasts with buffer (Format required by WINDFOR: ISO datetime)
        # Fetching from Dec 25, 2025 to catch day-ahead forecasts for early Jan 2026
        forecasts = await client.get_forecast_wind_generation(
            publish_start="2025-12-25T00:00:00Z",
            publish_end="2026-01-31T23:59:59Z"
        )
        
        # 3. Process Data and compute metrics
        result = process_forecast_accuracy(
            actuals=actuals,
            forecasts=forecasts,
            cutoff_time_str=settings.decision_cutoff_time
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()