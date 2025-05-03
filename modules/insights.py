import pandas as pd
import numpy as np
from typing import Dict, List, Any

def generate_insights(df: pd.DataFrame, forecast: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates comprehensive insights from the enhanced dataset and forecast data.
    
    Parameters:
    df (DataFrame): Enhanced dataset with derived features
    forecast (DataFrame): Forecast data for future predictions
    
    Returns:
    Dict: Dictionary containing categorized insights
    """
    insights = {}
    
    # Basic Sales Metrics
    insights['sales_and_product_trends'] = {}
    product_trends = insights['sales_and_product_trends']
    
    # 1. Top selling categories by total revenue
    if 'category' in df.columns and 'total_revenue' in df.columns:
        category_sales = df.groupby('category')['total_revenue'].sum().sort_values(ascending=False)
        product_trends['top_categories'] = category_sales.head(5).to_dict()
    
    # 2. Products generating most revenue
    if 'item_purchased' in df.columns and 'total_revenue' in df.columns:
        product_revenue = df.groupby('item_purchased')['total_revenue'].sum().sort_values(ascending=False)
        product_trends['top_revenue_products'] = product_revenue.head(5).to_dict()
    
    # 3. Monthly sales analysis
    if 'month' in df.columns and 'total_revenue' in df.columns:
        monthly_sales = df.groupby('month')['total_revenue'].sum()
        product_trends['monthly_sales'] = monthly_sales.to_dict()
    
    # 4. Daily sales patterns
    if 'day_of_week' in df.columns and 'total_revenue' in df.columns:
        daily_sales = df.groupby('day_of_week')['total_revenue'].sum()
        product_trends['daily_sales'] = daily_sales.to_dict()
    
    # 5. Popular products analysis
    if 'item_purchased' in df.columns and 'popularity_score' in df.columns:
        popular_items = df.groupby('item_purchased')['popularity_score'].mean().sort_values(ascending=False)
        product_trends['popular_products'] = popular_items.head(5).to_dict()
    
    # 6. Seasonal revenue analysis
    if 'season' in df.columns and 'total_revenue' in df.columns:
        seasonal_revenue = df.groupby('season')['total_revenue'].sum()
        product_trends['seasonal_revenue'] = seasonal_revenue.to_dict()
    
    # 7. Trending items
    if 'item_purchased' in df.columns and 'trend_flag' in df.columns:
        trending_items = df[df['trend_flag'] == 1]['item_purchased'].unique()
        product_trends['trending_items'] = trending_items[:5].tolist()
    
    # 8. Product size analysis
    if 'product_size' in df.columns and 'total_revenue' in df.columns:
        size_revenue = df.groupby('product_size')['total_revenue'].sum()
        product_trends['size_revenue'] = size_revenue.to_dict()
    
    # 9. Product color analysis
    if 'product_color' in df.columns and 'total_revenue' in df.columns:
        color_revenue = df.groupby('product_color')['total_revenue'].sum()
        product_trends['color_revenue'] = color_revenue.to_dict()
    
    # 10. Regional seasonal analysis
    if all(col in df.columns for col in ['region', 'season', 'total_revenue']):
        regional_seasonal = df.groupby(['region', 'season'])['total_revenue'].sum().unstack()
        product_trends['regional_seasonal_revenue'] = regional_seasonal.to_dict()
    
    # Customer Behavior Insights
    insights['customer_behavior'] = {}
    customer_behavior = insights['customer_behavior']
    
    # 1. Purchase frequency analysis
    if 'customer_id' in df.columns and 'purchase_frequency' in df.columns:
        avg_purchase_freq = df.groupby('customer_id')['purchase_frequency'].mean()
        customer_behavior['average_purchase_frequency'] = avg_purchase_freq.to_dict()
    
    # 2. Category loyalty analysis
    if all(col in df.columns for col in ['customer_id', 'category']):
        category_purchases = df.groupby(['customer_id', 'category']).size().reset_index(name='frequency')
        category_return = category_purchases.groupby('category')['frequency'].mean()
        customer_behavior['category_return_frequency'] = category_return.to_dict()
    
    # 3. Customer lifetime value
    if 'customer_lifetime_value' in df.columns:
        customer_behavior['lifetime_value_analysis'] = {
            'average_clv': df['customer_lifetime_value'].mean(),
            'top_customers': df.nlargest(5, 'customer_lifetime_value')['customer_id'].tolist()
        }
    
    # 4. Promo code effectiveness
    if all(col in df.columns for col in ['promo_code_used', 'total_revenue']):
        promo_analysis = {
            'avg_with_promo': df[df['promo_code_used'] == 1]['total_revenue'].mean(),
            'avg_without_promo': df[df['promo_code_used'] == 0]['total_revenue'].mean()
        }
        customer_behavior['promo_analysis'] = promo_analysis
    
    # 5. Reviews impact
    if all(col in df.columns for col in ['review_rating', 'purchase_frequency']):
        review_correlation = df['review_rating'].corr(df['purchase_frequency'])
        customer_behavior['rating_purchase_correlation'] = review_correlation
    
    # 6. Weekend vs weekday behavior
    if 'is_weekend' in df.columns and 'total_revenue' in df.columns:
        weekend_analysis = df.groupby('is_weekend')['total_revenue'].agg(['mean', 'sum'])
        customer_behavior['weekend_behavior'] = weekend_analysis.to_dict()
    
    # 7. Shipping preferences
    if all(col in df.columns for col in ['shipping_type', 'age', 'gender']):
        shipping_preferences = df.groupby('shipping_type').size()
        customer_behavior['shipping_demographics'] = shipping_preferences.to_dict()
    
    # Operational Insights
    insights['operational_insights'] = {}
    operational_insights = insights['operational_insights']
    
    # 1. Stock recommendations
    if all(col in df.columns for col in ['trend_flag', 'popularity_score', 'item_purchased']):
        trending = df[df['trend_flag'] == 1]['item_purchased'].unique()
        operational_insights['stocking_recommendations'] = trending.tolist()
    
    # 2. Seasonal demand
    if 'season' in df.columns and 'quantity' in df.columns:
        season_demand = df.groupby('season')['quantity'].sum()
        operational_insights['seasonal_demand'] = season_demand.to_dict()
    
    # 3. Shipping analysis
    if all(col in df.columns for col in ['shipping_type', 'total_revenue']):
        shipping_stats = df.groupby('shipping_type').agg({
            'total_revenue': 'sum',
            'quantity': 'count'
        })
        operational_insights['shipping_analysis'] = shipping_stats.to_dict()
    
    # 4. Underperforming categories
    if 'category' in df.columns and 'total_revenue' in df.columns:
        low_performers = df.groupby('category')['total_revenue'].sum()
        operational_insights['underperforming_categories'] = low_performers.nsmallest(3).to_dict()
    
    # 5. Payment methods
    if 'payment_method' in df.columns:
        payment_stats = df.groupby('payment_method').agg({
            'total_revenue': 'sum',
            'quantity': 'count'
        })
        operational_insights['payment_analysis'] = payment_stats.to_dict()
    
    # Advanced Insights
    insights['advanced_insights'] = {}
    advanced_insights = insights['advanced_insights']
    
    # 1. Size purchase patterns
    if 'product_size' in df.columns and 'purchase_frequency' in df.columns:
        size_frequency = df.groupby('product_size')['purchase_frequency'].mean()
        advanced_insights['size_purchase_frequency'] = size_frequency.to_dict()
    
    # 2. Review analysis
    if all(col in df.columns for col in ['review_rating', 'total_revenue']):
        rating_revenue = df.groupby('review_rating')['total_revenue'].mean()
        advanced_insights['rating_analysis'] = rating_revenue.to_dict()
    
    # 3. Promotional impact
    if all(col in df.columns for col in ['promo_code_used', 'purchase_date']):
        promo_usage = df.groupby('purchase_date')['promo_code_used'].mean()
        advanced_insights['promo_trends'] = promo_usage.to_dict()
    
    # 4. Age-based analysis
    if 'age' in df.columns and 'total_revenue' in df.columns:
        age_spending = df.groupby('age')['total_revenue'].mean()
        advanced_insights['age_trend_correlation'] = age_spending.to_dict()
    
    # Comparative Insights
    insights['comparative_insights'] = {}
    comparative_insights = insights['comparative_insights']
    
    # 1. Regional patterns
    if 'region' in df.columns and 'purchase_frequency' in df.columns:
        region_frequency = df.groupby('region')['purchase_frequency'].mean()
        comparative_insights['regional_frequency'] = region_frequency.to_dict()
    
    # 2. Subscription impact
    if 'is_subscribed' in df.columns and 'total_revenue' in df.columns:
        sub_revenue = df.groupby('is_subscribed')['total_revenue'].mean()
        comparative_insights['subscription_spending'] = sub_revenue.to_dict()
    
    # 3. Gender patterns
    if 'gender' in df.columns and 'total_revenue' in df.columns:
        gender_spending = df.groupby('gender')['total_revenue'].mean()
        comparative_insights['gender_trends'] = gender_spending.to_dict()
    
    # 4. Urban vs Rural
    if 'region' in df.columns and 'total_revenue' in df.columns:
        regional_metrics = df.groupby('region').agg({
            'total_revenue': 'mean',
            'quantity': 'sum'
        })
        comparative_insights['regional_comparison'] = regional_metrics.to_dict()
    
    # Forecast Insights
    if forecast is not None:
        forecast_preview = forecast[['ds', 'yhat']].tail(30).to_dict(orient='records')
        forecast_insights = {
            'forecast_next_30_days': forecast_preview,
            'average_forecasted_sales': forecast['yhat'].tail(30).mean(),
            'max_forecasted_day': forecast.loc[forecast['yhat'].tail(30).idxmax(), 'ds'].strftime("%Y-%m-%d"),
            'min_forecasted_day': forecast.loc[forecast['yhat'].tail(30).idxmin(), 'ds'].strftime("%Y-%m-%d")
        }
        insights['forecast_insights'] = forecast_insights
    
    return insights
