from prophet import Prophet
import pandas as pd

def forecast_sales(df):
    """
    Aggregates daily sales and forecasts future sales using Prophet.
    
    Expects the DataFrame to have 'purchase_date' and 'price' columns.
    Returns:
      - forecast: DataFrame with forecasted values.
      - model: The fitted Prophet model.
    """
    # Aggregate sales by day
    daily_sales = df.groupby('purchase_date')['price'].sum().reset_index()
    daily_sales = daily_sales.rename(columns={'purchase_date': 'ds', 'price': 'y'})
    
    # Initialize and fit the Prophet model
    model = Prophet()
    model.fit(daily_sales)
    
    # Create future dates for forecasting (e.g., next 30 days)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    return forecast, model
