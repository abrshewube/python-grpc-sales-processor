import unittest
import io
import os
import sys
import tempfile
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)

from utils.csv_processor import aggregate_sales_from_stream, write_output_csv


class TestCSVProcessor(unittest.TestCase):
    
    def test_aggregate_sales_basic(self):
        """Test basic aggregation summing sales numbers."""
        csv_data = [
            "Department Name,Date,Number of Sales\n",
            "Electronics,2023-08-01,100\n",
            "Clothing,2023-08-01,200\n",
            "Electronics,2023-08-02,150\n"
        ]
        
        result = aggregate_sales_from_stream(iter(csv_data))
        
        # Should sum sales: Electronics = 100 + 150 = 250
        self.assertEqual(result['Electronics'], 250)
        # Clothing = 200
        self.assertEqual(result['Clothing'], 200)
    
    def test_aggregate_sales_empty(self):
        """Test empty CSV."""
        csv_data = ["Department Name,Date,Number of Sales\n"]
        result = aggregate_sales_from_stream(iter(csv_data))
        self.assertEqual(len(result), 0)
    
    def test_aggregate_sales_malformed_rows(self):
        """Test handling of malformed rows."""
        csv_data = [
            "Department Name,Date,Number of Sales\n",
            "Electronics,2023-08-01,100\n",
            "incomplete row\n",  # malformed - insufficient columns
            "Clothing,2023-08-01,200\n"
        ]
        
        result = aggregate_sales_from_stream(iter(csv_data))
        
        # Should still process valid rows
        self.assertEqual(result['Electronics'], 100)
        self.assertEqual(result['Clothing'], 200)
    
    def test_aggregate_sales_invalid_date(self):
        """Test handling of invalid date format."""
        csv_data = [
            "Department Name,Date,Number of Sales\n",
            "Electronics,2023-08-01,100\n",
            "Clothing,08/01/2023,200\n",  # Invalid date format
            "Books,2023-08-01,50\n"
        ]
        
        result = aggregate_sales_from_stream(iter(csv_data))
        
        # Should skip row with invalid date
        self.assertEqual(result['Electronics'], 100)
        self.assertEqual(result['Books'], 50)
        self.assertNotIn('Clothing', result)
    
    def test_aggregate_sales_negative_values(self):
        """Test handling of negative sales values."""
        csv_data = [
            "Department Name,Date,Number of Sales\n",
            "Electronics,2023-08-01,100\n",
            "Clothing,2023-08-01,-50\n",  # Negative value
            "Books,2023-08-01,50\n"
        ]
        
        result = aggregate_sales_from_stream(iter(csv_data))
        
        # Should skip row with negative value
        self.assertEqual(result['Electronics'], 100)
        self.assertEqual(result['Books'], 50)
        self.assertNotIn('Clothing', result)
    
    def test_aggregate_sales_invalid_sales_number(self):
        """Test handling of invalid sales number (non-integer)."""
        csv_data = [
            "Department Name,Date,Number of Sales\n",
            "Electronics,2023-08-01,100\n",
            "Clothing,2023-08-01,abc\n",  # Invalid number
            "Books,2023-08-01,50\n"
        ]
        
        result = aggregate_sales_from_stream(iter(csv_data))
        
        # Should skip row with invalid sales number
        self.assertEqual(result['Electronics'], 100)
        self.assertEqual(result['Books'], 50)
        self.assertNotIn('Clothing', result)
    
    def test_aggregate_sales_empty_department(self):
        """Test handling of empty department name."""
        csv_data = [
            "Department Name,Date,Number of Sales\n",
            "Electronics,2023-08-01,100\n",
            ",2023-08-01,200\n",  # Empty department name
            "Books,2023-08-01,50\n"
        ]
        
        result = aggregate_sales_from_stream(iter(csv_data))
        
        # Should skip row with empty department name
        self.assertEqual(result['Electronics'], 100)
        self.assertEqual(result['Books'], 50)
    
    def test_write_output_csv(self):
        """Test output CSV writing."""
        dept_counts = {
            'Electronics': 500,
            'Clothing': 300,
            'Books': 200
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            output_path = f.name
        
        try:
            write_output_csv(dept_counts, output_path)
            
            # Verify file exists and has correct content
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r') as f:
                lines = f.readlines()
                self.assertEqual(len(lines), 4)  # header + 3 departments
                self.assertIn('Department Name', lines[0])
                self.assertIn('Total Number of Sales', lines[0])
                # Check sorted order
                self.assertIn('Books', lines[1])
                self.assertIn('Clothing', lines[2])
                self.assertIn('Electronics', lines[3])
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


if __name__ == '__main__':
    unittest.main()

