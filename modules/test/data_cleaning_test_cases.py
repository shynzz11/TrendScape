import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from modules.data_cleaning import clean_data

class TestDataCleaning(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a sample DataFrame with various test cases
        self.today = datetime.now().date()
        self.sample_data = {
            'customer_id': ['C001', 'C002', 'C003', None, 'C005', 'C006', 'C007', 'C008', 'C009', 'C010'],
            'price': [100, -50, 1000000, 200, None, '50.00', '$100', '1,000', 0, 300],
            'purchase_date': [
                self.today,
                self.today + timedelta(days=1),  # future date
                '2023-01-01',
                None,
                '2023-13-13',  # invalid date
                'Jan 1, 2023',
                '01/01/2023',
                '2023-01-01 10:00:00',
                'invalid_date',
                '2023-01-01'
            ],
            'quantity': [1, 2000, None, 0, -1, '5', 'ten', 1.5, 1, 1],
            'payment_method': ['CREDIT', 'Visa', 'PayPal', 'Unknown', 'GPAY', 'Cash on Delivery', None, 'mastercard', 'amex', 'debit'],
            'review_rating': [5, 8, None, 0, 11, 3, 'good', 4.5, -1, 4],
            'is_subscribed': ['yes', 'true', 'no', '0', '1', 'subscribed', None, 'FALSE', 'Y', 'N'],
            'age': [25, 150, -1, None, 0, '35', 'twenty', 40.5, 12, 80],
            'product_color': ['  Red  ', 'BLUE', 'green', '', None, '  ', 'N/A', 'Unknown', 'RED', 'Blue'],
            'category': ['Electronics', None, '', '  ', 'BOOKS', 'Games ', None, 'electronics', 'ELECTRONICS', 'Books']
        }
        self.df = pd.DataFrame(self.sample_data)

    def test_missing_values(self):
        """Test handling of missing values"""
        cleaned_df = clean_data(self.df)
        
        # Check if essential columns don't have any null values
        self.assertTrue(cleaned_df['customer_id'].notna().all())
        self.assertTrue(cleaned_df['price'].notna().all())
        self.assertTrue(cleaned_df['purchase_date'].notna().all())
        
        # Check if quantity defaults to 1 when missing
        self.assertTrue((cleaned_df['quantity'] >= 1).all())
        
        # Check if review_rating has been filled with median
        self.assertTrue(cleaned_df['review_rating'].notna().all())

    def test_data_type_conversions(self):
        """Test data type conversions"""
        cleaned_df = clean_data(self.df)
        
        # Test date conversion
        self.assertEqual(cleaned_df['purchase_date'].dtype, 'datetime64[ns]')
        
        # Test price conversion to numeric
        self.assertEqual(cleaned_df['price'].dtype, 'float64')
        
        # Test quantity conversion to int
        self.assertEqual(cleaned_df['quantity'].dtype, 'int64')
        
        # Test review_rating conversion to numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_df['review_rating']))
        
        # Test age conversion to numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_df['age']))

    def test_value_validation(self):
        """Test validation of value ranges and formats"""
        cleaned_df = clean_data(self.df)
        
        # Test price is positive
        self.assertTrue((cleaned_df['price'] > 0).all())
        
        # Test purchase date is not in future
        self.assertTrue((cleaned_df['purchase_date'] <= pd.Timestamp(self.today)).all())
        
        # Test quantity is reasonable
        self.assertTrue((cleaned_df['quantity'] >= 1).all())
        self.assertTrue((cleaned_df['quantity'] <= 1000).all())
        
        # Test age is within reasonable range
        if 'age' in cleaned_df.columns:
            self.assertTrue((cleaned_df['age'] >= 13).all())
            self.assertTrue((cleaned_df['age'] <= 120).all())
        
        # Test review rating is within valid range
        self.assertTrue((cleaned_df['review_rating'] >= 1).all())
        self.assertTrue((cleaned_df['review_rating'] <= 5).all())

    def test_outlier_handling(self):
        """Test outlier detection and handling"""
        cleaned_df = clean_data(self.df)
        
        # Create a separate extreme outlier df to test IQR method
        outlier_df = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
            'price': [100, 200, 150, 9999999, 175],
            'purchase_date': [self.today] * 5
        })
        
        cleaned_outlier_df = clean_data(outlier_df)
        
        # Verify extreme outlier was removed
        self.assertTrue(len(cleaned_outlier_df) < len(outlier_df))
        self.assertTrue(cleaned_outlier_df['price'].max() < 9999999)

    def test_text_standardization(self):
        """Test standardization of text fields"""
        cleaned_df = clean_data(self.df)
        
        # Test product_color standardization
        if 'product_color' in cleaned_df.columns:
            # Should be title case
            for color in cleaned_df['product_color'].dropna():
                self.assertTrue(color == color.title())
        
        # Test category standardization
        if 'category' in cleaned_df.columns:
            # Should be title case and no leading/trailing spaces
            for category in cleaned_df['category'].dropna():
                self.assertTrue(category == category.strip().title())

    def test_category_normalization(self):
        """Test normalization of categorical values"""
        cleaned_df = clean_data(self.df)
        
        # Test payment method normalization
        payment_methods = cleaned_df['payment_method'].dropna().unique()
        
        # Should match our standardized values from payment_mapping
        standard_methods = {'Credit Card', 'PayPal', 'Google Pay', 'Cash', 'Debit Card', 'Apple Pay'}
        
        # All payment methods should be one of our standard values or unchanged
        for method in payment_methods:
            if method not in standard_methods and method not in self.df['payment_method'].values:
                self.fail(f"Payment method '{method}' not properly standardized")

    def test_boolean_conversion(self):
        """Test conversion of various boolean representations"""
        cleaned_df = clean_data(self.df)
        
        # Test is_subscribed conversion
        if 'is_subscribed' in cleaned_df.columns:
            # Should be boolean
            self.assertEqual(cleaned_df['is_subscribed'].dtype, 'bool')
            
            # Verify expected transformations
            orig_values = ['yes', 'true', 'no', '0', '1', 'subscribed', None, 'FALSE', 'Y', 'N']
            expected = [True, True, False, False, True, True, False, False, True, False]
            
            # Sample a few key conversions
            for i, expected_val in enumerate([True, True, False, False, True]):
                if i < len(cleaned_df) and orig_values[i] in self.df['is_subscribed'].values:
                    idx = self.df[self.df['is_subscribed'] == orig_values[i]].index[0]
                    if idx in cleaned_df.index:
                        self.assertEqual(cleaned_df.loc[idx, 'is_subscribed'], expected_val)

    def test_duplicate_removal(self):
        """Test duplicate transaction removal"""
        # Create data with duplicates
        dup_data = pd.DataFrame({
            'customer_id': ['C001', 'C001', 'C002'],
            'product_id': ['P001', 'P001', 'P002'],
            'purchase_date': ['2023-01-01', '2023-01-01', '2023-01-02'],
            'price': [100, 100, 200]
        })
        
        cleaned_dup_df = clean_data(dup_data)
        
        # Should have removed 1 duplicate
        self.assertEqual(len(cleaned_dup_df), 2)

    def test_empty_dataframe(self):
        """Test handling of empty DataFrames"""
        empty_df = pd.DataFrame()
        cleaned_empty = clean_data(empty_df)
        
        self.assertTrue(cleaned_empty.empty)

    def test_data_consistency(self):
        """Test that data cleaning maintains internal consistency"""
        cleaned_df = clean_data(self.df)
        
        # Check that cleaned data has reasonable size
        self.assertGreater(len(cleaned_df), 0)
        
        # Test that essential columns are preserved
        for col in ['customer_id', 'price', 'purchase_date']:
            self.assertIn(col, cleaned_df.columns)
        
        # Verify no NaN in essential columns
        for col in ['customer_id', 'price', 'purchase_date']:
            self.assertEqual(cleaned_df[col].isna().sum(), 0)

    def test_invalid_dataframe_input(self):
        """Test handling of invalid DataFrame inputs"""
        # Test with None input
        result_none = clean_data(None)
        self.assertTrue(isinstance(result_none, pd.DataFrame))
        self.assertTrue(result_none.empty)
        
        # Test with invalid type (not a DataFrame)
        with self.assertRaises(Exception):
            clean_data("not a dataframe")
        
        # Test with DataFrame of wrong structure (missing essential columns)
        invalid_df = pd.DataFrame({'random_column': [1, 2, 3]})
        result_invalid = clean_data(invalid_df)
        self.assertTrue(isinstance(result_invalid, pd.DataFrame))
        # Should return empty DataFrame or handle gracefully

    def test_corrupted_data(self):
        """Test handling of severely corrupted data"""
        # Create DataFrame with corrupted data (all wrong types)
        corrupted_df = pd.DataFrame({
            'customer_id': [None, None, None],
            'price': [None, None, None],
            'purchase_date': [None, None, None],
            'quantity': [None, None, None]
        })
        
        result = clean_data(corrupted_df)
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertTrue(result.empty)  # Should return empty DataFrame
        
    def test_malicious_input(self):
        """Test handling of potentially problematic inputs"""
        # Test with extremely large values
        large_df = pd.DataFrame({
            'customer_id': ['C001'],
            'price': [float('inf')],  # Infinity
            'purchase_date': [self.today],
            'quantity': [10**10]  # Extremely large quantity
        })
        
        result_large = clean_data(large_df)
        self.assertTrue(isinstance(result_large, pd.DataFrame))

if __name__ == '__main__':
    unittest.main()