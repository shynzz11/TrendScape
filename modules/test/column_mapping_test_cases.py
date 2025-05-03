import unittest
import pandas as pd
import numpy as np
from modules.column_mapping import map_columns

class TestColumnMapping(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Define standard column mapping dictionary for tests
        self.standard_columns = {
            "customer_id": ["customer_id", "cust_id", "customer", "client_id", "user_id"],
            "price": ["price", "cost", "amount", "unit_price", "sale_price"],
            "purchase_date": ["purchase_date", "order_date", "date", "transaction_date"],
            "product_id": ["product_id", "prod_id", "item_id", "sku"],
            "quantity": ["quantity", "qty", "count", "units"],
            "customer_name": ["customer_name", "client_name", "buyer_name", "name"],
            "email": ["email", "email_address", "contact_email", "customer_email"]
        }

    def test_exact_matches(self):
        """Test exact column name matches"""
        input_columns = ["customer_id", "price", "purchase_date"]
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        self.assertEqual(mapping["customer_id"], "customer_id")
        self.assertEqual(mapping["price"], "price")
        self.assertEqual(mapping["purchase_date"], "purchase_date")
        self.assertEqual(len(unmapped), 0)

    def test_synonym_matches(self):
        """Test matching of column synonyms"""
        input_columns = ["cust_id", "unit_price", "order_date"]
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        self.assertEqual(mapping["cust_id"], "customer_id")
        self.assertEqual(mapping["unit_price"], "price")
        self.assertEqual(mapping["order_date"], "purchase_date")
        self.assertEqual(len(unmapped), 0)

    def test_case_insensitive_matches(self):
        """Test case-insensitive matching"""
        input_columns = ["CUSTOMER_ID", "Price", "Purchase_Date"]
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        self.assertEqual(mapping["CUSTOMER_ID"], "customer_id")
        self.assertEqual(mapping["Price"], "price")
        self.assertEqual(mapping["Purchase_Date"], "purchase_date")
        self.assertEqual(len(unmapped), 0)

    def test_partial_matches(self):
        """Test partial and fuzzy matches"""
        input_columns = ["customer_number", "price_amount", "transaction_time"]
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        self.assertEqual(mapping["customer_number"], "customer_id")
        self.assertEqual(mapping["price_amount"], "price")
        self.assertEqual(mapping["transaction_time"], "purchase_date")

    def test_unmapped_columns(self):
        """Test handling of unmapped columns"""
        input_columns = ["unknown_column", "random_field", "customer_id"]
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        self.assertEqual(mapping["customer_id"], "customer_id")
        self.assertIn("unknown_column", unmapped)
        self.assertIn("random_field", unmapped)
        self.assertEqual(len(unmapped), 2)

    def test_empty_input(self):
        """Test handling of empty input"""
        input_columns = []
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        self.assertEqual(len(mapping), 0)
        self.assertEqual(len(unmapped), 0)

    def test_similar_columns(self):
        """Test handling of similar column names"""
        input_columns = ["customer_id", "customer_id_2", "customer_number"]
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        self.assertEqual(mapping["customer_id"], "customer_id")
        self.assertIn("customer_id_2", unmapped)  # Should not map duplicate-like columns
        self.assertEqual(mapping["customer_number"], "customer_id")

    def test_special_characters(self):
        """Test handling of special characters in column names"""
        input_columns = ["customer-id", "price_$", "date#purchase"]
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        self.assertEqual(mapping["customer-id"], "customer_id")
        self.assertEqual(mapping["price_$"], "price")
        self.assertEqual(mapping["date#purchase"], "purchase_date")

    def test_whitespace_handling(self):
        """Test handling of whitespace in column names"""
        input_columns = ["customer id", "  price  ", "purchase date"]
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        self.assertEqual(mapping["customer id"], "customer_id")
        self.assertEqual(mapping["  price  "], "price")
        self.assertEqual(mapping["purchase date"], "purchase_date")

    def test_multiple_possible_matches(self):
        """Test handling of columns that could match multiple standard columns"""
        input_columns = ["customer_price", "id_number", "date_amount"]
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        # These should map to the closest match or be unmapped if below threshold
        self.assertIn("customer_price", mapping)
        self.assertIn("id_number", mapping)
        self.assertIn("date_amount", mapping)

    def test_threshold_boundary(self):
        """Test matching behavior near the threshold boundary"""
        input_columns = ["cust", "prc", "dt"]  # Very short abbreviations
        mapping, unmapped = map_columns(input_columns, self.standard_columns)
        
        # These should be unmapped due to being too short/ambiguous
        self.assertIn("cust", unmapped)
        self.assertIn("prc", unmapped)
        self.assertIn("dt", unmapped)

if __name__ == '__main__':
    unittest.main()