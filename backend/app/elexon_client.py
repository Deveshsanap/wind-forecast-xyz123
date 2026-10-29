import httpx
from app.config import settings
from typing import List, Dict, Any

class ElexonClient:
    def __init__(self):
        self.base_url = settings.elexon_api_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_actual_wind_generation(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        # FUELHH requires format yyyy-MM-dd
        url = f"{self.base_url}/datasets/FUELHH/stream"
        params = {
            "settlementDateFrom": start_date,
            "settlementDateTo": end_date,
            "fuelType": "WIND"
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        # Elexon Insights API usually wraps arrays in a list directly or under a 'data' key
        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data

    async def get_forecast_wind_generation(self, publish_start: str, publish_end: str) -> List[Dict[str, Any]]:
        # WINDFOR uses publishDateTime parameters
        url = f"{self.base_url}/datasets/WINDFOR/stream"
        params = {
            "publishDateTimeFrom": publish_start,
            "publishDateTimeTo": publish_end
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data

    async def close(self):
        await self.client.aclose()