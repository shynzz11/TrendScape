# TrendScape Dashboard

A comprehensive sales analytics dashboard built with Python and Streamlit that provides insights into sales trends, customer behavior, and product performance.

## Features

- Sales and Product Trend Analysis
- Customer Behavior Insights
- Operational Analytics
- Advanced Data Visualization
- Achievement Badges Generation
- Secure User Authentication

## Installation

1. Clone this repository
```bash
git clone <your-repository-url>
```

2. Install required packages
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Main application file
- `modules/`: Core functionality modules
  - `data_ingestion.py`: Data loading and processing
  - `data_cleaning.py`: Data cleaning utilities
  - `feature_engineering.py`: Feature generation and enhancement
  - `insights.py`: Business insights generation
  - `trend_analysis.py`: Trend analysis and forecasting
  - `badge.py`: Achievement badge generation
  - `user_auth.py`: User authentication system
- `assets/`: Image assets and templates
- `docs/`: Project documentation

## Required Data Format

The dashboard accepts CSV, Excel, or JSON files with the following columns:
- customer_id
- age
- gender
- region
- product_id
- category
- item_purchased
- price
- quantity
- product_size
- product_color
- purchase_id
- purchase_date
- payment_method
- promo_code_used
- shipping_type
- review_rating
- is_subscribed
- previous_purchases
