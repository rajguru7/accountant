"""
Tests for GenericCSVImporter driver
Following Test-Driven Development approach
"""
import pytest
import tempfile
import os
from datetime import date
from decimal import Decimal
from ingestion.drivers.csv_importer import GenericCSVImporter


class TestGenericCSVImporter:
    """Test suite for GenericCSVImporter"""

    def test_initialization_with_valid_config(self):
        """Test that GenericCSVImporter can be initialized with valid config"""
        config = {
            "institution": "TestBank",
            "driver": "csv",
            "file_pattern": "test-*.csv",
            "skip_header_lines": 1,
            "columns": {
                "date": "transaction_date",
                "narration": "description",
                "amount": "amount"
            }
        }
        importer = GenericCSVImporter(config)
        assert importer.institution == "TestBank"
        assert importer.file_pattern == "test-*.csv"

    def test_parse_simple_csv_file(self):
        """Test parsing a simple CSV file with basic columns"""
        config = {
            "institution": "Chase",
            "driver": "csv",
            "file_pattern": "chase-*.csv",
            "skip_header_lines": 0,  # First line is the header
            "columns": {
                "date": "Date",
                "narration": "Description",
                "amount": "Amount"
            }
        }
        
        # Create temporary CSV file
        csv_content = """Date,Description,Amount
2024-01-15,Grocery Store,-45.23
2024-01-16,Salary Deposit,2500.00
2024-01-17,Gas Station,-35.50"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            importer = GenericCSVImporter(config)
            transactions = importer.parse(temp_file)
            
            assert len(transactions) == 3
            assert transactions[0]['date'] == date(2024, 1, 15)
            assert transactions[0]['narration'] == 'Grocery Store'
            assert transactions[0]['amount'] == Decimal('-45.23')
            
            assert transactions[1]['date'] == date(2024, 1, 16)
            assert transactions[1]['amount'] == Decimal('2500.00')
        finally:
            os.unlink(temp_file)

    def test_parse_csv_with_metadata_columns(self):
        """Test parsing CSV with additional metadata columns"""
        config = {
            "institution": "Zerodha",
            "driver": "csv",
            "file_pattern": "tradebook-*.csv",
            "skip_header_lines": 0,  # First line is the header
            "columns": {
                "date": "trade_date",
                "narration": "symbol",
                "amount": "net_amount",
                "meta": ["order_id", "trade_type"]
            }
        }
        
        csv_content = """trade_date,symbol,net_amount,order_id,trade_type
2024-01-10,RELIANCE,-15000.50,ORD123,BUY
2024-01-11,TCS,8500.00,ORD124,SELL"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            importer = GenericCSVImporter(config)
            transactions = importer.parse(temp_file)
            
            assert len(transactions) == 2
            assert transactions[0]['narration'] == 'RELIANCE'
            assert transactions[0]['meta']['order_id'] == 'ORD123'
            assert transactions[0]['meta']['trade_type'] == 'BUY'
        finally:
            os.unlink(temp_file)

    def test_parse_csv_with_skip_header(self):
        """Test that skip_header_lines configuration works"""
        config = {
            "institution": "TestBank",
            "driver": "csv",
            "file_pattern": "test-*.csv",
            "skip_header_lines": 2,  # Skip 2 header lines
            "columns": {
                "date": "Date",
                "narration": "Description",
                "amount": "Amount"
            }
        }
        
        csv_content = """Account Statement
Report Date: 2024-01-31
Date,Description,Amount
2024-01-15,Test Transaction,100.00"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            importer = GenericCSVImporter(config)
            transactions = importer.parse(temp_file)
            
            assert len(transactions) == 1
            assert transactions[0]['narration'] == 'Test Transaction'
        finally:
            os.unlink(temp_file)

    def test_parse_empty_csv_file(self):
        """Test handling of empty CSV file"""
        config = {
            "institution": "TestBank",
            "driver": "csv",
            "file_pattern": "test-*.csv",
            "skip_header_lines": 0,  # First line is the header
            "columns": {
                "date": "Date",
                "narration": "Description",
                "amount": "Amount"
            }
        }
        
        csv_content = """Date,Description,Amount"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            importer = GenericCSVImporter(config)
            transactions = importer.parse(temp_file)
            
            assert len(transactions) == 0
        finally:
            os.unlink(temp_file)

    def test_invalid_config_missing_required_fields(self):
        """Test that invalid config raises appropriate error"""
        config = {
            "institution": "TestBank",
            # Missing required fields
        }
        
        with pytest.raises(ValueError):
            GenericCSVImporter(config)

    def test_convert_to_beancount_format(self):
        """Test conversion of parsed transactions to Beancount format"""
        config = {
            "institution": "Chase",
            "driver": "csv",
            "file_pattern": "chase-*.csv",
            "skip_header_lines": 0,  # First line is the header
            "account": "Assets:US:Chase:Checking",
            "columns": {
                "date": "Date",
                "narration": "Description",
                "amount": "Amount"
            }
        }
        
        csv_content = """Date,Description,Amount
2024-01-15,Grocery Store,-45.23"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            importer = GenericCSVImporter(config)
            transactions = importer.parse(temp_file)
            beancount_entries = importer.to_beancount(transactions)
            
            assert len(beancount_entries) > 0
            # Beancount entry should contain date, narration, and postings
        finally:
            os.unlink(temp_file)
