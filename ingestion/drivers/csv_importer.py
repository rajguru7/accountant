"""
GenericCSVImporter - A generalized CSV importer driver for SFIS
Handles any delimited text file with configurable column mapping
"""
import csv
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Any, Optional
import re


class GenericCSVImporter:
    """
    Generic CSV importer that can handle various CSV formats
    based on YAML configuration
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the CSV importer with configuration
        
        Args:
            config: Configuration dictionary with required fields:
                - institution: Name of the financial institution
                - driver: Type of driver (must be "csv")
                - file_pattern: Glob pattern for matching files
                - skip_header_lines: Number of header lines to skip
                - columns: Column mapping configuration
        """
        self._validate_config(config)
        
        self.institution = config['institution']
        self.driver = config['driver']
        self.file_pattern = config['file_pattern']
        self.skip_header_lines = config.get('skip_header_lines', 0)
        self.columns = config['columns']
        self.account = config.get('account', '')
        
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate that required configuration fields are present"""
        required_fields = ['institution', 'driver', 'file_pattern', 'columns']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required configuration field: {field}")
        
        if config['driver'] != 'csv':
            raise ValueError(f"Invalid driver type: {config['driver']}, expected 'csv'")
        
        # Validate columns configuration
        columns = config['columns']
        required_columns = ['date', 'narration', 'amount']
        for col in required_columns:
            if col not in columns:
                raise ValueError(f"Missing required column mapping: {col}")
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a CSV file and extract transactions
        
        Args:
            file_path: Path to the CSV file to parse
            
        Returns:
            List of transaction dictionaries with parsed data
        """
        transactions = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read all lines
            all_lines = f.readlines()
            
            # skip_header_lines indicates how many lines to skip before the CSV header
            # For skip_header_lines=1, skip line 0, line 1 is the CSV header
            # For skip_header_lines=2, skip lines 0-1, line 2 is the CSV header
            if self.skip_header_lines >= len(all_lines):
                return []
            
            # Get header and data lines
            header = all_lines[self.skip_header_lines]
            data_lines = all_lines[self.skip_header_lines + 1:]
            
            # Create a DictReader from header and data
            reader = csv.DictReader([header] + data_lines)
            
            for row in reader:
                transaction = self._parse_row(row)
                transactions.append(transaction)
        
        return transactions
    
    def _parse_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse a single CSV row into a transaction dictionary
        
        Args:
            row: Dictionary representing a CSV row
            
        Returns:
            Parsed transaction dictionary
        """
        transaction = {}
        
        # Parse date
        date_column = self.columns['date']
        date_str = row[date_column]
        transaction['date'] = self._parse_date(date_str)
        
        # Parse narration (description)
        narration_column = self.columns['narration']
        transaction['narration'] = row[narration_column]
        
        # Parse amount
        amount_column = self.columns['amount']
        amount_str = row[amount_column]
        transaction['amount'] = self._parse_amount(amount_str)
        
        # Parse metadata if configured
        if 'meta' in self.columns:
            transaction['meta'] = {}
            for meta_field in self.columns['meta']:
                if meta_field in row:
                    transaction['meta'][meta_field] = row[meta_field]
        
        return transaction
    
    def _parse_date(self, date_str: str) -> date:
        """
        Parse date string into date object
        Supports common date formats
        """
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%m-%d-%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _parse_amount(self, amount_str: str) -> Decimal:
        """
        Parse amount string into Decimal
        Handles various formats including negative amounts
        """
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$€£¥₹,\s]', '', amount_str)
        
        # Handle parentheses for negative amounts (accounting format)
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        return Decimal(cleaned)
    
    def to_beancount(self, transactions: List[Dict[str, Any]]) -> List[str]:
        """
        Convert parsed transactions to Beancount format
        
        Args:
            transactions: List of parsed transaction dictionaries
            
        Returns:
            List of Beancount transaction strings
        """
        entries = []
        
        for txn in transactions:
            # Build Beancount transaction entry
            entry_lines = []
            
            # Transaction header
            txn_date = txn['date'].strftime('%Y-%m-%d')
            narration = txn['narration']
            entry_lines.append(f'{txn_date} * "{self.institution}" "{narration}"')
            
            # Main account posting
            amount = txn['amount']
            if self.account:
                entry_lines.append(f'  {self.account}  {amount} USD')
            
            # Add metadata as comments if present
            if 'meta' in txn:
                for key, value in txn['meta'].items():
                    entry_lines.append(f'  ; {key}: {value}')
            
            entries.append('\n'.join(entry_lines))
        
        return entries
