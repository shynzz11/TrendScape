import pandas as pd
import numpy as np
from datetime import datetime

def clean_data(df):
    """
    Comprehensive data cleaning function that handles various anomalies:
    - Drops rows with missing essential data
    - Converts data types (dates, numeric values)
    - Handles outliers
    - Standardizes text columns
    - Validates data ranges
    - Removes duplicates
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Make a copy to avoid modifying the original DataFrame
    df_clean = df.copy()
    
    # ===== HANDLING MISSING VALUES =====
    # Define essential columns – adjust these based on your mapping
    essential_cols = ["customer_id", "price", "purchase_date"]
    df_clean = df_clean.dropna(subset=essential_cols)
    
    # Fill non-essential missing values with appropriate defaults
    if 'quantity' in df_clean.columns:
        df_clean['quantity'] = df_clean['quantity'].fillna(1)
    
    if 'review_rating' in df_clean.columns:
        df_clean['review_rating'] = df_clean['review_rating'].fillna(df_clean['review_rating'].median())
    
    # ===== DATA TYPE CONVERSIONS =====
    # Convert purchase_date column to datetime with better error handling
    if 'purchase_date' in df_clean.columns:
        # First try standard format, then attempt various common formats
        df_clean['purchase_date'] = pd.to_datetime(df_clean['purchase_date'], errors='coerce')
        
        # Remove rows with invalid dates
        df_clean = df_clean.dropna(subset=['purchase_date'])
        
        # Ensure dates are not in the future
        today = pd.Timestamp(datetime.now().date())
        df_clean = df_clean[df_clean['purchase_date'] <= today]
    
    # Convert price column to numeric with better handling
    if 'price' in df_clean.columns:
        # Handle currency symbols and commas in price
        if df_clean['price'].dtype == 'object':
            df_clean['price'] = df_clean['price'].astype(str).str.replace('[$,]', '', regex=True)
        
        df_clean['price'] = pd.to_numeric(df_clean['price'], errors='coerce')
        
        # Remove rows with negative or zero prices (likely errors)
        df_clean = df_clean[df_clean['price'] > 0]
    
    # Convert quantity to integers
    if 'quantity' in df_clean.columns:
        df_clean['quantity'] = pd.to_numeric(df_clean['quantity'], errors='coerce').fillna(1).astype(int)
        # Remove unrealistic quantities (e.g., orders of 1000+ items might be errors)
        df_clean = df_clean[df_clean['quantity'] <= 1000]
    
    # ===== OUTLIER DETECTION AND HANDLING =====
    # Handle price outliers using IQR method
    if 'price' in df_clean.columns:
        Q1 = df_clean['price'].quantile(0.25)
        Q3 = df_clean['price'].quantile(0.75)
        IQR = Q3 - Q1
        
        # Define bounds for outliers (adjust multiplier as needed)
        lower_bound = max(0, Q1 - 1.5 * IQR)  # Ensure non-negative
        upper_bound = Q3 + 3 * IQR  # More lenient upper bound
        
        # Filter out extreme price outliers
        df_clean = df_clean[(df_clean['price'] >= lower_bound) & 
                            (df_clean['price'] <= upper_bound)]
    
    # ===== TEXT STANDARDIZATION =====
    # Standardize text fields for consistency
    text_columns = ['item_purchased', 'category', 'product_color', 'payment_method', 'shipping_type']
    for col in text_columns:
        if col in df_clean.columns:
            # Convert to string, strip whitespace, and title case
            df_clean[col] = df_clean[col].astype(str).str.strip().str.title()
            
            # Replace empty strings with NaN
            df_clean[col] = df_clean[col].replace('', np.nan).replace('Nan', np.nan)
    
    # ===== CATEGORY NORMALIZATION =====
    # Normalize payment method categories
    if 'payment_method' in df_clean.columns:
        # Map similar payment methods to standard names
        payment_mapping = {
            'Credit': 'Credit Card',
            'Credit Card': 'Credit Card',
            'Visa': 'Credit Card',
            'Mastercard': 'Credit Card',
            'Amex': 'Credit Card',
            'Debit': 'Debit Card',
            'Debit Card': 'Debit Card',
            'Paypal': 'PayPal',
            'Pay Pal': 'PayPal',
            'Apple Pay': 'Apple Pay',
            'Google Pay': 'Google Pay',
            'Android Pay': 'Google Pay',
            'Gpay': 'Google Pay',
            'Cash': 'Cash',
            'Cod': 'Cash',
            'Cash On Delivery': 'Cash'
        }
        df_clean['payment_method'] = df_clean['payment_method'].map(lambda x: 
            next((v for k, v in payment_mapping.items() if k.lower() in str(x).lower()), x))
    
    # ===== BOOLEAN CONVERSIONS =====
    # Convert string boolean values to actual booleans
    bool_columns = ['is_subscribed', 'promo_code_used']
    for col in bool_columns:
        if col in df_clean.columns:
            # Map various representations to boolean
            true_values = ['yes', 'true', 't', 'y', '1', 'used', 'subscribed']
            df_clean[col] = df_clean[col].astype(str).str.lower().isin(true_values)
    
    # ===== REMOVE DUPLICATES =====
    # Remove duplicate transactions (same customer, product, date, price)
    if all(col in df_clean.columns for col in ['customer_id', 'product_id', 'purchase_date', 'price']):
        df_clean = df_clean.drop_duplicates(subset=['customer_id', 'product_id', 'purchase_date', 'price'])
    
    # ===== VALIDATION =====
    # Validate age is reasonable (if present)
    if 'age' in df_clean.columns:
        df_clean['age'] = pd.to_numeric(df_clean['age'], errors='coerce')
        df_clean = df_clean[(df_clean['age'] >= 13) & (df_clean['age'] <= 120)]
    
    # Validate review ratings (if present)
    if 'review_rating' in df_clean.columns:
        df_clean['review_rating'] = pd.to_numeric(df_clean['review_rating'], errors='coerce')
        # Normalize ratings to 1-5 scale if they're on another scale (like 0-10)
        if df_clean['review_rating'].max() > 5:
            df_clean['review_rating'] = df_clean['review_rating'] / 2
        
        # Ensure ratings are within the valid range
        df_clean['review_rating'] = df_clean['review_rating'].clip(1, 5)
    
    # Reset index for clean DataFrame
    df_clean = df_clean.reset_index(drop=True)
    
    return df_clean
