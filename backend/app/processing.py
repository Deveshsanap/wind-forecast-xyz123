import pandas as pd
import numpy as np
from typing import Dict, Any, List

def process_forecast_accuracy(actuals: List[Dict], forecasts: List[Dict], cutoff_time_str: str) -> Dict[str, Any]:
    if not actuals or not forecasts:
        return {"error": "Insufficient data"}

    df_act = pd.DataFrame(actuals)
    df_fcst = pd.DataFrame(forecasts)

    # Standardize column names and types
    df_act['startTime'] = pd.to_datetime(df_act['startTime'], utc=True)
    df_fcst['startTime'] = pd.to_datetime(df_fcst['startTime'], utc=True)
    df_fcst['publishTime'] = pd.to_datetime(df_fcst['publishTime'], utc=True)

    # Ensure actuals are only WIND (safeguard)
    if 'fuelType' in df_act.columns:
        df_act = df_act[df_act['fuelType'].str.upper() == 'WIND']

    # 1. Look-ahead bias prevention: Calculate exact cutoff per delivery interval
    # January is GMT (UTC+0), so local time is identical to UTC. 
    cutoff_hour, cutoff_minute = map(int, cutoff_time_str.split(':'))
    
    # Delivery date is the calendar date of the startTime
    df_fcst['delivery_date'] = df_fcst['startTime'].dt.floor('D')
    
    # Decision cutoff is D-1 at the configured time
    df_fcst['decision_cutoff'] = df_fcst['delivery_date'] - pd.Timedelta(days=1) + pd.Timedelta(hours=cutoff_hour, minutes=cutoff_minute)

    # 2. Filter: Keep only forecasts published before or exactly at the cutoff
    valid_forecasts = df_fcst[df_fcst['publishTime'] <= df_fcst['decision_cutoff']]

    if valid_forecasts.empty:
        return {"error": "No forecasts eligible before the decision cutoff."}

    # 3. Select latest eligible forecast for each delivery interval (startTime)
    # Sort by publish time ascending, then group by start time and take the last row
    best_forecasts = valid_forecasts.sort_values('publishTime').groupby('startTime').last().reset_index()

    # 4. Merge Actuals and Forecasts
    merged = pd.merge(
        df_act[['startTime', 'generation']],
        best_forecasts[['startTime', 'generation', 'publishTime']],
        on='startTime',
        suffixes=('_actual', '_forecast')
    ).dropna()

    if merged.empty:
        return {"error": "No overlapping intervals between actuals and valid forecasts."}

    # 5. Calculate Metrics
    merged['error'] = merged['generation_forecast'] - merged['generation_actual']
    merged['abs_error'] = merged['error'].abs()
    merged['squared_error'] = merged['error'] ** 2

    # Vectorized statistical aggregations
    mae = merged['abs_error'].mean()
    rmse = np.sqrt(merged['squared_error'].mean())
    bias = merged['error'].mean()
    
    sum_actual = merged['generation_actual'].sum()
    sum_abs_error = merged['abs_error'].sum()
    
    # Safe WAPE calculation
    wape = (sum_abs_error / sum_actual * 100) if sum_actual > 0 else None

    # Format time series data for frontend
    merged['startTime'] = merged['startTime'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    merged['publishTime'] = merged['publishTime'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Sort chronologically
    merged = merged.sort_values('startTime')
    
    records = merged.rename(columns={
        'generation_actual': 'actual',
        'generation_forecast': 'forecast'
    }).to_dict(orient='records')

    return {
        "summary": {
            "total_intervals": len(records),
            "cutoff_time": cutoff_time_str,
            "metrics": {
                "mae": round(mae, 2),
                "rmse": round(rmse, 2),
                "bias": round(bias, 2),
                "wape": round(wape, 2) if wape is not None else None
            }
        },
        "timeseries": records
    }