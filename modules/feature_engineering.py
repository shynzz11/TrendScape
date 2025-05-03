import pandas as pd
import numpy as np

def generate_features(data):
    """
    Generates derived features from cleaned data to enhance analysis
    
    Parameters:
    data (DataFrame): Cleaned data from data_cleaning module
    
    Returns:
    DataFrame: Enhanced dataset with derived features
    """
    # Make a copy to avoid modifying the original
    df = data.copy()
    
    try:
        # Ensure purchase_date is datetime
        if 'purchase_date' in df.columns and not pd.api.types.is_datetime64_dtype(df['purchase_date']):
            df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
        
        # Time-Based Features
        if 'purchase_date' in df.columns:
            # Extracts month name from the purchase date
            df['month'] = df['purchase_date'].dt.month_name()
            # Extracts day of the week from the purchase date
            df['day_of_week'] = df['purchase_date'].dt.day_name()
            # Determines the season based on the month (1: Winter, 2: Spring, 3: Summer, 4: Fall)
            df['season'] = df['purchase_date'].dt.month % 12 // 3 + 1
            # Identifies if the purchase day is a weekend (Saturday or Sunday)
            df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday']).astype(int)
        
        # Basic derived metrics
        if all(col in df.columns for col in ['price', 'quantity']):
            # Calculates total revenue by multiplying price and quantity
            df['total_revenue'] = df['price'] * df['quantity']
        
        # Category features
        if all(col in df.columns for col in ['category', 'total_revenue']):
            # Calculates total sales per category
            category_sales = df.groupby('category')['total_revenue'].sum().reset_index()
            category_sales.rename(columns={'total_revenue': 'category_sales'}, inplace=True)
            df = df.merge(category_sales, on='category', how='left')
        
        # Customer metrics
        if all(col in df.columns for col in ['customer_id', 'total_revenue']):
            # Customer Lifetime Value: Total spending per customer
            customer_lifetime_value = df.groupby('customer_id')['total_revenue'].sum().reset_index()
            customer_lifetime_value.rename(columns={'total_revenue': 'customer_lifetime_value'}, inplace=True)
            df = df.merge(customer_lifetime_value, on='customer_id', how='left')
            
            # Purchase Frequency: Number of purchases per customer
            if 'purchase_id' in df.columns:
                purchase_frequency = df.groupby('customer_id')['purchase_id'].count().reset_index()
                purchase_frequency.rename(columns={'purchase_id': 'purchase_frequency'}, inplace=True)
                df = df.merge(purchase_frequency, on='customer_id', how='left')
            
            # Average spending: Average spending per customer
            average_spending = df.groupby('customer_id')['total_revenue'].mean().reset_index()
            average_spending.rename(columns={'total_revenue': 'average_spending'}, inplace=True)
            df = df.merge(average_spending, on='customer_id', how='left')
        
        # Product popularity metrics
        if all(col in df.columns for col in ['item_purchased', 'quantity', 'total_revenue']):
            popularity_cols = ['quantity', 'total_revenue']
            agg_dict = {
                'quantity': 'sum',
                'total_revenue': 'sum'
            }
            
            # Add review rating if available
            if 'review_rating' in df.columns:
                popularity_cols.append('review_rating')
                agg_dict['review_rating'] = 'mean'
            
            # Aggregate quantity, total revenue, and review rating (if available) per item
            popularity_score = df.groupby('item_purchased')[popularity_cols].agg(agg_dict).reset_index()
            
            # Rename columns for clarity
            popularity_score.rename(columns={
                'quantity': 'total_purchases',
                'review_rating': 'average_review_rating'
            }, inplace=True)
            
            # Calculate weighted popularity score
            if 'average_review_rating' in popularity_score.columns:
                popularity_score['popularity_score'] = (
                    popularity_score['total_purchases'] * 0.5 + 
                    popularity_score['total_revenue'] * 0.3 + 
                    popularity_score['average_review_rating'] * 0.2
                )
            else:
                popularity_score['popularity_score'] = (
                    popularity_score['total_purchases'] * 0.6 + 
                    popularity_score['total_revenue'] * 0.4
                )
            
            df = df.merge(popularity_score[['item_purchased', 'popularity_score']], 
                          on='item_purchased', how='left')
            
            # Trend flag: Identifies if an item is trending based on its popularity score
            threshold = df['popularity_score'].quantile(0.8)
            df['trend_flag'] = (df['popularity_score'] >= threshold).astype(int)
        
        # Additional metrics as data permits
        if all(col in df.columns for col in ['category', 'review_rating']):
            # Calculates average rating per category
            average_rating_per_category = df.groupby('category')['review_rating'].mean().reset_index()
            average_rating_per_category.rename(columns={'review_rating': 'average_rating_per_category'}, inplace=True)
            df = df.merge(average_rating_per_category, on='category', how='left')
        
        # Discount effectiveness if promo code data exists
        if all(col in df.columns for col in ['promo_code_used', 'item_purchased', 'total_revenue']):
            if df['promo_code_used'].nunique() > 1:  # Only if we have both promo and non-promo sales
                # Get data with and without promos
                promo_data = df[df['promo_code_used'] == 1]
                non_promo_data = df[df['promo_code_used'] == 0]
                
                # Only proceed if we have both types of data
                if not promo_data.empty and not non_promo_data.empty:
                    total_revenue_with_promo = promo_data.groupby('item_purchased')['total_revenue'].sum().reset_index()
                    total_revenue_without_promo = non_promo_data.groupby('item_purchased')['total_revenue'].sum().reset_index()
                    
                    # Only include products that appear in both datasets
                    common_products = set(total_revenue_with_promo['item_purchased']) & set(total_revenue_without_promo['item_purchased'])
                    
                    if common_products:  # Only if we have common products
                        total_revenue_with_promo = total_revenue_with_promo[total_revenue_with_promo['item_purchased'].isin(common_products)]
                        total_revenue_without_promo = total_revenue_without_promo[total_revenue_without_promo['item_purchased'].isin(common_products)]
                        
                        discount_effectiveness = total_revenue_with_promo.merge(
                            total_revenue_without_promo, 
                            on='item_purchased',
                            suffixes=('_with', '_without')
                        )
                        
                        discount_effectiveness['discount_effectiveness'] = (
                            discount_effectiveness['total_revenue_with'] - discount_effectiveness['total_revenue_without']
                        )
                        
                        df = df.merge(
                            discount_effectiveness[['item_purchased', 'discount_effectiveness']], 
                            on='item_purchased', 
                            how='left'
                        )
        
        # Demographic correlations if age and gender data exists
        if all(col in df.columns for col in ['age', 'category']) and df['age'].notna().any():
            try:
                # Calculates the most purchased category for each age
                age_category_preference = df.groupby(['age', 'category']).size().reset_index(name='count')
                age_category_preference = age_category_preference.loc[age_category_preference.groupby('age')['count'].idxmax()]
                age_category_preference.rename(columns={'category': 'most_purchased_category_by_age'}, inplace=True)
                df = df.merge(age_category_preference[['age', 'most_purchased_category_by_age']], on='age', how='left')
            except:
                pass  # Skip if this fails
                
        if all(col in df.columns for col in ['gender', 'category']) and df['gender'].notna().any():
            try:
                # Calculates the most purchased category for each gender
                gender_category_preference = df.groupby(['gender', 'category']).size().reset_index(name='count')
                gender_category_preference = gender_category_preference.loc[gender_category_preference.groupby('gender')['count'].idxmax()]
                gender_category_preference.rename(columns={'category': 'most_purchased_category_by_gender'}, inplace=True)
                df = df.merge(gender_category_preference[['gender', 'most_purchased_category_by_gender']], on='gender', how='left')
            except:
                pass  # Skip if this fails
        
        return df
    
    except Exception as e:
        print(f"Error generating features: {str(e)}")
        # Return original data if feature engineering fails
        return data
