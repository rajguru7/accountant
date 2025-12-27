"""
Tests for YAML configuration parser and loader
"""
import pytest
import tempfile
import os
import yaml
from ingestion.config_loader import ConfigLoader


class TestConfigLoader:
    """Test suite for ConfigLoader"""

    def test_load_valid_csv_config(self):
        """Test loading a valid CSV configuration from YAML"""
        yaml_content = """
institution: "Chase Bank"
driver: "csv"
file_pattern: "chase-*.csv"
skip_header_lines: 0
account: "Assets:US:Chase:Checking"
columns:
  date: "Date"
  narration: "Description"
  amount: "Amount"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            loader = ConfigLoader()
            config = loader.load(temp_file)
            
            assert config['institution'] == 'Chase Bank'
            assert config['driver'] == 'csv'
            assert config['file_pattern'] == 'chase-*.csv'
            assert config['columns']['date'] == 'Date'
        finally:
            os.unlink(temp_file)

    def test_load_config_with_metadata(self):
        """Test loading configuration with metadata columns"""
        yaml_content = """
institution: "Zerodha"
driver: "csv"
file_pattern: "tradebook-*.csv"
skip_header_lines: 0
columns:
  date: "trade_date"
  narration: "symbol"
  amount: "net_amount"
  meta:
    - "order_id"
    - "trade_type"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            loader = ConfigLoader()
            config = loader.load(temp_file)
            
            assert 'meta' in config['columns']
            assert 'order_id' in config['columns']['meta']
        finally:
            os.unlink(temp_file)

    def test_load_invalid_yaml_file(self):
        """Test handling of invalid YAML file"""
        yaml_content = """
institution: "Test"
driver: csv
  invalid: indentation
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            loader = ConfigLoader()
            with pytest.raises(yaml.YAMLError):
                loader.load(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_nonexistent_file(self):
        """Test handling of non-existent configuration file"""
        loader = ConfigLoader()
        with pytest.raises(FileNotFoundError):
            loader.load('/nonexistent/path/config.yaml')

    def test_load_all_configs_from_directory(self):
        """Test loading all configuration files from a directory"""
        # Create temporary directory with multiple config files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config 1
            config1 = """
institution: "Bank A"
driver: "csv"
file_pattern: "banka-*.csv"
skip_header_lines: 0
columns:
  date: "Date"
  narration: "Description"
  amount: "Amount"
"""
            with open(os.path.join(tmpdir, 'banka.yaml'), 'w') as f:
                f.write(config1)
            
            # Create config 2
            config2 = """
institution: "Bank B"
driver: "csv"
file_pattern: "bankb-*.csv"
skip_header_lines: 0
columns:
  date: "Date"
  narration: "Desc"
  amount: "Amt"
"""
            with open(os.path.join(tmpdir, 'bankb.yaml'), 'w') as f:
                f.write(config2)
            
            loader = ConfigLoader()
            configs = loader.load_all_from_directory(tmpdir)
            
            assert len(configs) == 2
            institutions = [c['institution'] for c in configs]
            assert 'Bank A' in institutions
            assert 'Bank B' in institutions

    def test_validate_config_schema(self):
        """Test configuration validation"""
        loader = ConfigLoader()
        
        # Valid config
        valid_config = {
            'institution': 'Test',
            'driver': 'csv',
            'file_pattern': '*.csv',
            'columns': {
                'date': 'Date',
                'narration': 'Desc',
                'amount': 'Amt'
            }
        }
        assert loader.validate(valid_config) is True
        
        # Invalid config - missing required field
        invalid_config = {
            'institution': 'Test',
            'driver': 'csv'
            # Missing file_pattern and columns
        }
        assert loader.validate(invalid_config) is False
