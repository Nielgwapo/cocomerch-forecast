"""
Simplified Sales Forecasting for CocoMerch (Render API)
Author: AI Assistant
Date: 2025-11-03
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from statistics import mean

class SimpleForecastController:
    def __init__(self):
        pass

    def generate_forecast_from_data(self, sales_data, months=3):
        """
        sales_data: a list of dicts like:
        [
            {"product_id": 1, "product_name": "Coconut Lumber", "sales": 120},
            {"product_id": 2, "product_name": "Coco Husk", "sales": 150}
        ]
        """

        if not sales_data or len(sales_data) < 2:
            return {"error": "Not enough data for forecasting"}

        df = pd.DataFrame(sales_data)

        # Validate that 'sales' column exists
        if "sales" not in df.columns:
            return {"error": "Missing 'sales' key in data"}

        # Prepare basic forecasting model
        df["month_index"] = np.arange(1, len(df) + 1)
        X = df[["month_index"]]
        y = df["sales"]

        model = LinearRegression()
        model.fit(X, y)

        # Predict next few months
        future_months = np.arange(len(df) + 1, len(df) + months + 1).reshape(-1, 1)
        forecast = model.predict(future_months)

        # Confidence estimate based on data variance
        variance = np.var(y)
        confidence = round(max(0.4, min(0.95, 1 - variance / (mean(y) ** 2 + 1e-6))), 2)

        results = []
        for i, f in enumerate(forecast, 1):
            results.append({
                "month_offset": i,
                "forecast_sales": round(float(f), 2)
            })

        return {
            "success": True,
            "forecasts": results,
            "confidence": confidence,
            "message": f"Generated {len(results)}-month forecast successfully."
        }
