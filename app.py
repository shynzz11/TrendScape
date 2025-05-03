import streamlit as st
import logging
import os
logging.getLogger("streamlit.runtime").setLevel(logging.ERROR)

import pandas as pd
from modules.data_ingestion import load_data
from modules.column_mapping import map_columns
from modules.data_cleaning import clean_data
from modules.trend_analysis import forecast_sales
from modules.insights import generate_insights
from modules.badge import generate_badge
from modules.user_auth import init_auth_db, login_page, signup_page, logout, delete_user
from modules.feature_engineering import generate_features

# Initialize the authentication database
init_auth_db()

# Initialize session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'redirect_signup' not in st.session_state:
    st.session_state.redirect_signup = False

# Set up the app
st.set_page_config(page_title="TrendLens Dashboard", layout="wide")

# Handle redirect to signup page first
if st.session_state.redirect_signup:
    st.title("🔒 Create Your Account")
    signup_page()
    st.session_state.redirect_signup = False
    st.rerun()  # Use st.rerun() instead of experimental_rerun for newer Streamlit versions
    st.stop()

# If user is not logged in, show login/signup pages
if not st.session_state.logged_in:
    st.title("🔒 Welcome to TrendScape Dashboard")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        login_page()
    with tab2:
        signup_page()
    st.stop()

# Show dashboard for logged-in users
st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")
logout()

# Add self account deletion for logged-in users using an expander confirmation
if st.sidebar.button("Delete My Account", key="delete_my_account_button"):
    with st.sidebar.expander("Confirm Account Deletion", expanded=True):
        st.write("Are you sure you want to delete your account? This action cannot be undone.")
        col_yes, col_no = st.columns(2)
        if col_yes.button("Yes, Delete My Account", key="confirm_yes"):
            success, message = delete_user(st.session_state.username)
            if success:
                st.success("Account deleted successfully.")
                # Clear ALL session state variables
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                # Set only the required flags for redirection
                st.session_state.redirect_signup = True
                st.session_state.logged_in = False
                st.session_state.username = None
                time.sleep(1)  # Brief pause to ensure state updates
                st.rerun()
            else:
                st.error(f"Failed to delete account: {message}")
        if col_no.button("Cancel", key="confirm_no"):
            st.info("Account deletion cancelled.")

# ====== SIDEBAR NAVIGATION ======
menu = st.sidebar.radio(
    "📌 Navigate",
    ["🏠 Overview", "📂 Column Mapping", "🧹 Data Cleaning", "🔍 Feature Engineering", 
     "📈 Trend Analysis", "💡 Insights", "🏆 Badge" ] #"📋 Raw Data"
)

# ====== ADMIN PANEL (Visible only for admin) ======
if st.session_state.username.lower() == "admin":
    st.sidebar.markdown("### Admin Panel")
    with st.sidebar.expander("Delete User", expanded=False):
        delete_username = st.text_input("Username to Delete", key="delete_username")
        if st.button("Delete User", key="delete_user_button"):
            if delete_username.lower() == "admin":
                st.error("Cannot delete admin account")
            else:
                success, message = delete_user(delete_username)
                if success:
                    st.success(f"User '{delete_username}' deleted successfully")
                    # If the deleted user is currently logged in, force them to logout
                    if delete_username == st.session_state.get('username'):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.session_state.redirect_signup = True
                        st.rerun()
                else:
                    st.error(message)

# ====== FILE UPLOAD SECTION ======
st.sidebar.subheader("📁 Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload your sales data (CSV, Excel, JSON)", type=['csv', 'xlsx', 'xls', 'json']
)

if uploaded_file is not None:
    try:
        # ====== DATA INGESTION ======
        if 'df' not in st.session_state:
            st.session_state.df = load_data(uploaded_file)

        df = st.session_state.df

        # Check if df is empty (error occurred during loading)
        if df.empty:
            st.error("Failed to process the uploaded file. Please ensure it contains the required columns 'price' and 'customer_id'.")
            st.session_state.df = None
        else:
            # ====== METRICS ======
            total_sales = df['price'].sum()
            total_customers = df['customer_id'].nunique()
            avg_order_value = total_sales / total_customers if total_customers > 0 else 0

            # Display metrics at the top of the page
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="💰 Total Sales", value=f"${total_sales:,.2f}")
            with col2:
                st.metric(label="👥 Total Customers", value=f"{total_customers}")
            with col3:
                st.metric(label="📦 Average Order Value", value=f"${avg_order_value:.2f}")

            # ====== NAVIGATION LOGIC ======
            if menu == "🏠 Overview":
                st.title(f"📊 TrendScape Dashboard Overview - Welcome {st.session_state.username}!")
                st.write("Welcome to the TrendScape Dashboard! Upload your data and explore insights.")

            # ====== COLUMN MAPPING ======
            if menu == "📂 Column Mapping":
                st.title("🗺️ Column Mapping")
                st.write("Map your input columns to the standardized format.")

                input_columns = list(df.columns)
                standard_columns = {
                    "customer_id": ["customer_id", "cust_id", "customer"],
                    "age": ["age", "customer_age", "years"],
                    "gender": ["gender", "sex"],
                    "region": ["region", "area", "location"],
                    "product_id": ["product_id", "prod_id", "item_id"],
                    "category": ["category", "type", "segment"],
                    "item_purchased": ["item_purchased", "product_name", "item", "product"],
                    "price": ["price", "cost", "amount", "unit_price"],
                    "quantity": ["quantity", "qty", "count", "number"],
                    "product_size": ["product_size", "size"],
                    "product_color": ["product_color", "color"],
                    "purchase_id": ["purchase_id", "order_id", "transaction_id"],
                    "purchase_date": ["purchase_date", "order_date", "date", "transaction_date"],
                    "payment_method": ["payment_method", "payment_type", "payment"],
                    "promo_code_used": ["promo_code_used", "promo", "discount_code"],
                    "shipping_type": ["shipping_type", "delivery_method"],
                    "review_rating": ["review_rating", "rating", "score"],
                    "is_subscribed": ["is_subscribed", "subscription", "subscribed"],
                    "previous_purchases": ["previous_purchases", "past_orders", "purchase_history"]
                }

                mapping, unmapped = map_columns(input_columns, standard_columns)
                st.write("### Mapping Results:")
                st.json(mapping)

                if unmapped:
                    st.warning("Unmapped columns: " + ", ".join(unmapped))

            # ====== DATA CLEANING ======
            if menu == "🧹 Data Cleaning":
                st.title("🧹 Data Cleaning")
                if 'df' in st.session_state:
                    with st.expander("🔍 Clean Data Preview"):
                        try:
                            if 'df_clean' not in st.session_state or st.session_state.df_clean is None:
                                st.session_state.df_clean = clean_data(st.session_state.df)
                                st.write("✅ Data cleaning completed!")
                            
                            df_clean = st.session_state.df_clean
                            
                            if df_clean is not None and not df_clean.empty:
                                st.write("### Cleaned Data Preview:")
                                st.dataframe(df_clean.head())
                            else:
                                st.warning("⚠️ Cleaning returned an empty DataFrame. Check data integrity.")
                        except Exception as e:
                            st.error(f"❌ Data Cleaning Error: {str(e)}")
                else:
                    st.warning("⚠️ Please upload and map your data first.")

            # ====== FEATURE ENGINEERING ======
            if menu == "🔍 Feature Engineering":
                st.title("🔍 Feature Engineering")
                if 'df_clean' in st.session_state and st.session_state.df_clean is not None:
                    with st.expander("✨ Enhanced Features"):
                        try:
                            if 'df_features' not in st.session_state or st.button("Regenerate Features"):
                                with st.spinner("Generating advanced features..."):
                                    st.session_state.df_features = generate_features(st.session_state.df_clean)
                                st.success("✅ Feature engineering completed!")
                            
                            df_features = st.session_state.df_features
                            
                            if df_features is not None and not df_features.empty:
                                # Show new derived features
                                original_cols = set(st.session_state.df_clean.columns)
                                new_cols = set(df_features.columns)
                                derived_features = list(new_cols - original_cols)
                                
                                if derived_features:
                                    st.write("### 🆕 Newly Derived Features:")
                                    for feature in sorted(derived_features):
                                        st.write(f"- `{feature}`")
                                
                                st.write("### Enhanced Data Preview:")
                                st.dataframe(df_features.head())
                                
                                # Add save button
                                if st.download_button(
                                    label="💾 Save Enhanced Dataset",
                                    data=df_features.to_csv(index=False),
                                    file_name="enhanced_features.csv",
                                    mime="text/csv"
                                ):
                                    st.success("✅ Enhanced dataset saved successfully!")
                        except Exception as e:
                            st.error(f"❌ Feature Engineering Error: {str(e)}")
                else:
                    st.warning("⚠️ Please clean your data first.")

            # ====== TREND ANALYSIS ======
            if menu == "📈 Trend Analysis":
                st.title("📈 Trend Analysis")
                if 'df_features' in st.session_state and st.session_state.df_features is not None:
                    analysis_data = st.session_state.df_features
                    data_source = "feature-enhanced"
                elif 'df_clean' in st.session_state and st.session_state.df_clean is not None:
                    analysis_data = st.session_state.df_clean
                    data_source = "cleaned"
                else:
                    analysis_data = None
                    data_source = None
                
                if analysis_data is not None:
                    try:
                        st.info(f"Using {data_source} data for trend analysis.")
                        with st.expander("🔮 Forecast Data (Last 30 Days)"):
                            if 'forecast' not in st.session_state or st.session_state.forecast is None or st.button("Regenerate Forecast"):
                                forecast, model = forecast_sales(analysis_data)
                                st.session_state.forecast = forecast
                                st.session_state.model = model
                            st.dataframe(st.session_state.forecast[['ds', 'yhat']].tail(30))
                    except Exception as e:
                        st.error(f"❌ Forecasting Error: {str(e)}")
                else:
                    st.warning("⚠️ Please clean your data first.")

            # ====== INSIGHTS ======
            if menu == "💡 Insights":
                st.title("💡 Personalized Insights")
                if 'df_features' in st.session_state and st.session_state.df_features is not None:
                    analysis_data = st.session_state.df_features
                    data_source = "feature-enhanced"
                elif 'df_clean' in st.session_state and st.session_state.df_clean is not None:
                    analysis_data = st.session_state.df_clean
                    data_source = "cleaned"
                else:
                    analysis_data = None
                    data_source = None
                
                if analysis_data is not None:
                    try:
                        st.info(f"Using {data_source} data for insights.")
                        
                        # Generate insights
                        if 'forecast' in st.session_state and st.session_state.forecast is not None:
                            if 'insights' not in st.session_state or st.button("Refresh Insights"):
                                st.session_state.insights = generate_insights(analysis_data, st.session_state.forecast)
                            
                            if st.session_state.insights:
                                # Category selection
                                categories = {
                                    "Sales and Product Trends": {
                                        "top_categories": "Top-selling categories",
                                        "top_revenue_products": "Products generating most revenue",
                                        "monthly_sales": "Sales variation across months",
                                        "daily_sales": "Sales by day of week",
                                        "popular_products": "Most popular products",
                                        "seasonal_revenue": "Seasonal revenue analysis",
                                        "trending_items": "Currently trending items",
                                        "size_revenue": "Sales by product size",
                                        "color_revenue": "Sales by product color",
                                        "regional_seasonal_revenue": "Regional seasonal trends"
                                    },
                                    "Customer Behavior": {
                                        "average_purchase_frequency": "Average purchase frequency",
                                        "category_return_frequency": "Category return frequency",
                                        "lifetime_value_analysis": "Customer lifetime value",
                                        "promo_analysis": "Promo code effectiveness",
                                        "rating_purchase_correlation": "Rating vs purchase correlation",
                                        "weekend_behavior": "Weekend vs weekday behavior",
                                        "shipping_demographics": "Shipping preferences by demographics"
                                    },
                                    "Operational Insights": {
                                        "stocking_recommendations": "Stocking recommendations",
                                        "seasonal_demand": "Seasonal demand patterns",
                                        "shipping_analysis": "Shipping analysis",
                                        "underperforming_categories": "Underperforming categories",
                                        "payment_analysis": "Payment method analysis",
                                        "multi_category_customers": "Multi-category customers"
                                    },
                                    "Advanced Insights": {
                                        "size_purchase_frequency": "Size vs purchase frequency",
                                        "rating_analysis": "Review and discount analysis",
                                        "promo_trends": "Promo code trends",
                                        "age_trend_correlation": "Age and trendy items correlation",
                                        "regional_shipping": "Regional shipping analysis",
                                        "seasonal_category_performance": "Seasonal category performance"
                                    },
                                    "Comparative Insights": {
                                        "regional_frequency": "Regional purchase frequency",
                                        "subscription_categories": "Subscription analysis",
                                        "gender_ratings": "Gender-based reviews",
                                        "subscription_spending": "Subscription spending patterns",
                                        "regional_categories": "Urban vs rural preferences"
                                    }
                                }
                                
                                # Create tabs for different visualization options
                                tab1, tab2 = st.tabs(["📊 Visual Insights", "📑 Raw Data"])
                                
                                with tab1:
                                    # Category dropdown
                                    selected_category = st.selectbox(
                                        "Select Category",
                                        list(categories.keys()),
                                        key="category_selector"
                                    )
                                    
                                    # Display subcategories for selected category
                                    if selected_category:
                                        st.subheader(f"{selected_category} Analysis")
                                        
                                        # Create columns for better layout
                                        col1, col2 = st.columns([2, 3])
                                        
                                        with col1:
                                            # Subcategory selection
                                            selected_subcategory = st.radio(
                                                "Select Analysis",
                                                list(categories[selected_category].values()),
                                                key="subcategory_selector"
                                            )
                                        
                                        with col2:
                                            # Find the key for selected subcategory
                                            selected_key = [k for k, v in categories[selected_category].items() 
                                                          if v == selected_subcategory][0]
                                            
                                            # Display the selected insight
                                            st.write("### Analysis Results")
                                            
                                            # Get the data for the selected category
                                            category_data = st.session_state.insights.get(selected_category.lower().replace(" ", "_"), {})
                                            if selected_key in category_data:
                                                data = category_data[selected_key]
                                                
                                                # Different display methods based on data type
                                                if isinstance(data, dict):
                                                    # Create a DataFrame for better visualization
                                                    df_display = pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
                                                    st.dataframe(df_display)
                                                    
                                                    # Add visualization if applicable
                                                    if len(data) > 0:
                                                        st.bar_chart(df_display)
                                                elif isinstance(data, (int, float)):
                                                    st.metric("Value", f"{data:,.2f}")
                                                elif isinstance(data, list):
                                                    for item in data:
                                                        st.write(f"- {item}")
                                                else:
                                                    st.write(data)
                                            else:
                                                st.info("No data available for this analysis")
                                
                                with tab2:
                                    st.json(st.session_state.insights)
                            else:
                                st.info("⚠️ No insights generated.")
                        else:
                            st.warning("⚠️ Please generate the forecast first.")
                    except Exception as e:
                        st.error(f"❌ Insight Generation Error: {str(e)}")
                else:
                    st.warning("⚠️ Please clean your data first.")

            # ====== BADGE GENERATION ======
            if menu == "🏆 Badge":
                st.title("🏆 Badge Generation")
                if 'df_features' in st.session_state and st.session_state.df_features is not None:
                    analysis_data = st.session_state.df_features
                elif 'df_clean' in st.session_state and st.session_state.df_clean is not None:
                    analysis_data = st.session_state.df_clean
                else:
                    analysis_data = None
                
                if analysis_data is not None:
                    try:
                        # Get all categories and their top products
                        all_badges = generate_badge(analysis_data)
                        
                        if all_badges:
                            # Create category dropdown
                            categories = list(all_badges.keys())
                            selected_category = st.selectbox(
                                "Select Product Category",
                                categories,
                                key="badge_category_selector"
                            )
                            
                            if selected_category:
                                badge_data = all_badges[selected_category]
                                
                                # Display badge information
                                st.write("### Top Product in Category")
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.markdown(f"""
                                    **Category:** {badge_data['category']}  
                                    **Product:** {badge_data['product']}  
                                    **Units Sold:** {badge_data['quantity']}
                                    """)
                                
                                with col2:
                                    if st.button("Generate Badge", key="generate_badge_btn"):
                                        # Display the generated badge image
                                        if os.path.exists(badge_data['badge_path']):  # Use os.path.exists to check if the file exists
                                            st.success("Badge Generated!")
                                            st.image(badge_data['badge_path'], caption="Your TrendScape Badge")
                                            
                                            # Read the image file for download
                                            with open(badge_data['badge_path'], 'rb') as f:
                                                badge_bytes = f.read()
                                            
                                            # Add download button for the badge image
                                            st.download_button(
                                                label="Download Badge",
                                                data=badge_bytes,
                                                file_name=f"trendlens_badge_{selected_category.lower().replace(' ', '_')}.png",
                                                mime="image/png",
                                                key="download_badge_btn"
                                            )
                                        else:
                                            st.error("Failed to generate badge image. Please try again.")
                        else:
                            st.warning("No product categories found in the data.")
                    except Exception as e:
                        st.error(f"❌ Badge Generation Error: {str(e)}")
                else:
                    st.warning("⚠️ Please clean your data first.")

            # ====== RAW DATA ======
            if menu == "📊 Raw Data":
                st.title("📊 Raw Data Preview")
                if 'df' in st.session_state:
                    with st.expander("📂 Raw Data Overview"):
                        st.write("### Raw Data:")
                        st.dataframe(st.session_state.df.head())
                else:
                    st.warning("⚠️ Please upload data first.")

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.session_state.df = None

else:
    st.info("📥 Please upload a file to get started.")