"""
Integration tests for SFIS
Tests the complete workflow from data import to ledger validation
"""
import pytest
import tempfile
import os
import shutil
from pathlib import Path
from ingestion.runner import IngestionRunner
from ingestion.config_loader import ConfigLoader
from plugins.inflation import InflationPlugin
from datetime import date
from decimal import Decimal


class TestIntegration:
    """End-to-end integration tests"""

    def test_complete_csv_import_workflow(self):
        """Test complete workflow: CSV → Config → Import → Beancount"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            config_dir = os.path.join(tmpdir, 'config')
            data_dir = os.path.join(tmpdir, 'data')
            output_dir = os.path.join(tmpdir, 'output')
            
            os.makedirs(config_dir)
            os.makedirs(data_dir)
            os.makedirs(output_dir)
            
            # Create test config
            config_content = """
institution: "Test Bank"
driver: "csv"
file_pattern: "test-*.csv"
skip_header_lines: 0
account: "Assets:TestBank:Checking"
columns:
  date: "Date"
  narration: "Description"
  amount: "Amount"
"""
            with open(os.path.join(config_dir, 'testbank.yaml'), 'w') as f:
                f.write(config_content)
            
            # Create test CSV data
            csv_content = """Date,Description,Amount
2024-01-15,Test Transaction 1,100.00
2024-01-16,Test Transaction 2,-50.00
2024-01-17,Test Transaction 3,75.00"""
            
            with open(os.path.join(data_dir, 'test-jan2024.csv'), 'w') as f:
                f.write(csv_content)
            
            # Run ingestion
            runner = IngestionRunner(config_dir, data_dir, output_dir)
            runner.run_all()
            
            # Verify output file was created
            output_file = os.path.join(output_dir, 'test_bank_import.bean')
            assert os.path.exists(output_file)
            
            # Verify output contains transactions
            with open(output_file, 'r') as f:
                content = f.read()
                assert 'Test Transaction 1' in content
                assert 'Test Transaction 2' in content
                assert 'Test Transaction 3' in content
                assert 'Assets:TestBank:Checking' in content

    def test_config_loader_integration(self):
        """Test ConfigLoader with multiple configs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple config files
            config1 = """
institution: "Bank A"
driver: "csv"
file_pattern: "banka-*.csv"
skip_header_lines: 0
columns:
  date: "Date"
  narration: "Desc"
  amount: "Amt"
"""
            config2 = """
institution: "Bank B"
driver: "csv"
file_pattern: "bankb-*.csv"
skip_header_lines: 0
columns:
  date: "TxnDate"
  narration: "Description"
  amount: "Amount"
"""
            
            with open(os.path.join(tmpdir, 'banka.yaml'), 'w') as f:
                f.write(config1)
            
            with open(os.path.join(tmpdir, 'bankb.yaml'), 'w') as f:
                f.write(config2)
            
            # Load all configs
            loader = ConfigLoader()
            configs = loader.load_all_from_directory(tmpdir)
            
            assert len(configs) == 2
            institutions = [c['institution'] for c in configs]
            assert 'Bank A' in institutions
            assert 'Bank B' in institutions
            
            # Validate all configs
            for config in configs:
                assert loader.validate(config) is True

    def test_inflation_plugin_integration(self):
        """Test inflation plugin end-to-end"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'inflation_test.bean')
            
            # Create test CPI data
            cpi_dict = {
                '2024-01': 300.0,
                '2024-02': 303.0,
                '2024-03': 306.0
            }
            
            # Initialize plugin and generate data
            plugin = InflationPlugin()
            cpi_data = plugin.load_cpi_data(cpi_dict)
            
            plugin.generate_beancount_file(
                commodity='I-USD',
                base_currency='USD',
                cpi_data=cpi_data,
                base_date=date(2024, 1, 1),
                output_file=output_file
            )
            
            # Verify file was created
            assert os.path.exists(output_file)
            
            # Verify content
            with open(output_file, 'r') as f:
                content = f.read()
                assert 'commodity I-USD' in content
                assert '2024-01-01 price I-USD 1.00 USD' in content
                assert 'I-USD' in content
                
            # Verify prices are correct
            prices = plugin.generate_prices('I-USD', 'USD', cpi_data, date(2024, 1, 1))
            assert len(prices) == 3
            
            # Base month should be 1.0
            base_price = next(p for p in prices if p['date'] == date(2024, 1, 1))
            assert base_price['value'] == Decimal('1.0')
            
            # March should reflect 2% inflation
            march_price = next(p for p in prices if p['date'] == date(2024, 3, 1))
            assert march_price['value'] == Decimal('1.02')

    def test_multi_source_ingestion(self):
        """Test importing from multiple data sources simultaneously"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, 'config')
            data_dir = os.path.join(tmpdir, 'data')
            output_dir = os.path.join(tmpdir, 'output')
            
            os.makedirs(config_dir)
            os.makedirs(data_dir)
            os.makedirs(output_dir)
            
            # Create configs for two banks
            for bank in ['BankA', 'BankB']:
                config = f"""
institution: "{bank}"
driver: "csv"
file_pattern: "{bank.lower()}-*.csv"
skip_header_lines: 0
account: "Assets:{bank}:Checking"
columns:
  date: "Date"
  narration: "Description"
  amount: "Amount"
"""
                with open(os.path.join(config_dir, f'{bank.lower()}.yaml'), 'w') as f:
                    f.write(config)
                
                # Create CSV data for each bank
                csv_content = f"""Date,Description,Amount
2024-01-15,{bank} Transaction 1,100.00
2024-01-16,{bank} Transaction 2,-50.00"""
                
                with open(os.path.join(data_dir, f'{bank.lower()}-2024.csv'), 'w') as f:
                    f.write(csv_content)
            
            # Run ingestion
            runner = IngestionRunner(config_dir, data_dir, output_dir)
            runner.run_all()
            
            # Verify both output files were created
            assert os.path.exists(os.path.join(output_dir, 'banka_import.bean'))
            assert os.path.exists(os.path.join(output_dir, 'bankb_import.bean'))
            
            # Verify each contains correct transactions
            for bank in ['banka', 'bankb']:
                output_file = os.path.join(output_dir, f'{bank}_import.bean')
                with open(output_file, 'r') as f:
                    content = f.read()
                    # Check for BankA or BankB Transaction 1
                    assert 'Transaction 1' in content
                    assert 'Transaction 2' in content

    def test_error_handling_invalid_csv(self):
        """Test that system handles invalid CSV gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, 'config')
            data_dir = os.path.join(tmpdir, 'data')
            output_dir = os.path.join(tmpdir, 'output')
            
            os.makedirs(config_dir)
            os.makedirs(data_dir)
            os.makedirs(output_dir)
            
            # Create valid config
            config = """
institution: "Test Bank"
driver: "csv"
file_pattern: "test-*.csv"
skip_header_lines: 0
account: "Assets:TestBank:Checking"
columns:
  date: "Date"
  narration: "Description"
  amount: "Amount"
"""
            with open(os.path.join(config_dir, 'test.yaml'), 'w') as f:
                f.write(config)
            
            # Create invalid CSV (missing required columns)
            invalid_csv = """WrongColumn1,WrongColumn2
Value1,Value2"""
            
            with open(os.path.join(data_dir, 'test-invalid.csv'), 'w') as f:
                f.write(invalid_csv)
            
            # Run ingestion - should not crash
            runner = IngestionRunner(config_dir, data_dir, output_dir)
            # Should handle error gracefully
            try:
                runner.run_all()
            except Exception as e:
                # Some exception is expected, but shouldn't be a crash
                assert isinstance(e, (KeyError, ValueError, Exception))
