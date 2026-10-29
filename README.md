# Wind Forecast Accuracy Dashboard

Live Application: [https://wind-forecast-xyz123.vercel.app/](url)

## Overview
This full-stack application helps energy utility procurement teams evaluate day-ahead wholesale market purchasing decisions. By comparing actual wind generation against the specific day-ahead forecasts available at the time of procurement, the dashboard allows the team to quantitatively assess forecast accuracy and minimize risk.

## Problem Statement & Solution
Purchasing electricity in the day-ahead market requires committing to volumes before actual renewable generation is known. Forecasts are critical, but they update continuously. 

**The core challenge:** We cannot evaluate accuracy using a forecast published after the procurement decision was made (look-ahead bias). 

**The solution:** This application reconstructs the exact knowledge available to the team at decision time. It enforces a strict D-1 11:00 AM local time cutoff, filtering out any forecasts published after this deadline before merging the remaining data with actual generation for January 2026.

## Technology Stack
- **Frontend:** React, Vite, Tailwind CSS (v4), Recharts, Lucide Icons.
- **Backend:** Python, FastAPI, Pandas, NumPy, HTTPX.
- **Infrastructure:** Vercel (Serverless Backend & Frontend), Docker (Local).

## Files & Directories Structure
- `/api/` - Contains `index.py`, the Vercel Serverless entrypoint that bridges the cloud infrastructure to the Python backend.
- `/backend/` - Contains the Python FastAPI application, Elexon BMRS API HTTPX clients, and Pandas data processing/vectorization logic.
- `/frontend/` - Contains the React single-page application, Vite build configuration, and Recharts visualization components.
- `vercel.json` - Configuration file defining Vercel build commands and routing rules.
- `docker-compose.yml` & `backend/Dockerfile` - Configurations for running the backend locally via Docker.

## Architecture & Data Flow
1. **API Client Layer:** The backend asynchronously fetches FUELHH (actuals) and WINDFOR (forecasts) data from Elexon BMRS.
2. **Data Normalization:** Timestamps are converted to strict UTC for chronological alignment.
3. **Cutoff Enforcement:** The backend calculates the D-1 11:00 AM cutoff for every delivery interval and drops any forecasts published after this time.
4. **Metric Calculation:** Pandas vectorizes the calculation of Mean Absolute Error (MAE), Root Mean Square Error (RMSE), Bias, and Weighted Absolute Percentage Error (WAPE).
5. **Client Presentation:** The React frontend consumes the REST API and renders interactive KPIs, time-series charts, and data tables in the user's local timezone.

## Setup Instructions

### Backend (Python/FastAPI)
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `.\venv\Scripts\Activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Set environment variables (create a `.env` file or export them):
   - `ELEXON_API_BASE_URL="https://data.elexon.co.uk/bmrs/api/v1"`
   - `DECISION_CUTOFF_TIME="11:00"`
6. Run the server: `uvicorn app.main:app --reload --port 8000`

### Frontend (React/Vite)
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run the development server: `npm run dev`

### Docker Support
To run the backend locally via Docker:
```bash
docker-compose up --build
