# Sovereign Financial Intelligence System (SFIS)

A powerful, self-hosted personal finance management system designed for sophisticated investors operating across multiple jurisdictions (US, India, Crypto). Built on Beancount with generalized data ingestion drivers and advanced analytics plugins.

## Overview

SFIS prioritizes **Algorithmic Sovereignty** - giving you full control over your financial data, tax modeling, and analytics. Unlike commercial PFM tools, SFIS:

- ✅ Treats currencies as true commodities with historical cost basis tracking
- ✅ Handles multi-jurisdictional tax scenarios (US, India, Crypto)
- ✅ Provides inflation-adjusted "real" portfolio values
- ✅ Runs entirely on your infrastructure (self-hosted)
- ✅ Uses plain text accounting for maximum transparency and version control

## Features

### Core Capabilities
- **Plain Text Accounting**: Human-readable ledger files using Beancount
- **Generalized Data Ingestion**: Reusable drivers for CSV, PDF, and API sources
- **Multi-Currency Support**: Native support for USD, INR, BTC, ETH, and more
- **Tax Modeling**: Proper tracking of withholdings, TDS, and foreign tax credits
- **Inflation Analytics**: View portfolio in real purchasing power terms
- **Self-Hosted**: Complete data privacy and control

### Supported Data Sources
- **CSV Files**: Chase, Robinhood, Zerodha, and any other CSV-based statements
- **PDF Statements**: ICICI Bank, NPS (coming soon)
- **API Aggregators**: SimpleFIN, Rotki (coming soon)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/rajguru7/accountant.git
cd accountant
```

2. Install dependencies:
```bash
pip install -e .
```

3. Verify installation:
```bash
bean-check ledger/main.bean
```

## Quick Start

### 1. Import Your First Statement

Place your bank CSV file in the `data/` directory:
```bash
cp ~/Downloads/chase-statement.csv data/
```

Configure the import in `ingestion/config/chase_checking.yaml`:
```yaml
institution: "Chase Bank"
driver: "csv"
file_pattern: "chase-*.csv"
skip_header_lines: 0
account: "Assets:US:Chase:Checking"
columns:
  date: "Posting Date"
  narration: "Description"
  amount: "Amount"
```

Run the ingestion:
```bash
python ingestion/runner.py
```

### 2. View Your Ledger

```bash
bean-check ledger/main.bean
fava ledger/main.bean
```

Open http://localhost:5000 in your browser to view your financial data with Fava's web interface.

### 3. Generate Inflation-Adjusted Prices

```bash
python scripts/generate_inflation_data.py
```

This creates I-USD (Inflation-adjusted USD) prices that let you view your wealth in real purchasing power terms.

## Project Structure

```
/accountant
├── ledger/                    # The Database (Beancount files)
│   ├── main.bean              # Entry point
│   ├── accounts/              # Chart of accounts definitions
│   │   ├── us_accounts.bean
│   │   ├── india_accounts.bean
│   │   └── crypto_accounts.bean
│   └── includes/              # Imported transaction files
├── ingestion/                 # Data ingestion framework
│   ├── drivers/               # Generic drivers (CSV, PDF, API)
│   │   └── csv_importer.py
│   ├── config/                # YAML configurations per institution
│   │   ├── chase_checking.yaml
│   │   └── zerodha_tradebook.yaml
│   ├── config_loader.py       # Configuration parser
│   └── runner.py              # Main ingestion controller
├── plugins/                   # Analytics plugins
│   └── inflation.py           # Inflation adjustment logic
├── scripts/                   # Utility scripts
│   └── generate_inflation_data.py
├── tests/                     # Test suite
│   ├── ingestion/
│   └── plugins/
└── data/                      # Source data files (gitignored)
```

## Configuration

### Adding a New Data Source

1. Create a YAML config file in `ingestion/config/`:

```yaml
institution: "Your Bank"
driver: "csv"
file_pattern: "yourbank-*.csv"
skip_header_lines: 0
account: "Assets:US:YourBank:Checking"
columns:
  date: "Date"
  narration: "Description"
  amount: "Amount"
  meta:
    - "Transaction ID"  # Optional metadata fields
```

2. Place your data files in `data/` matching the pattern
3. Run `python ingestion/runner.py`

### Chart of Accounts

Accounts are defined in `ledger/accounts/*.bean` files. Add new accounts as needed:

```beancount
2024-01-01 open Assets:US:NewBank:Checking USD
2024-01-01 open Expenses:NewCategory USD
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=ingestion --cov=plugins --cov-report=html
```

## Development

This project follows Test-Driven Development (TDD):

1. Write tests first in `tests/`
2. Implement the feature to make tests pass
3. Refactor and optimize
4. Run full test suite

### Code Style

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Advanced Usage

### Tax Tracking Example

Track US salary with federal withholding:

```beancount
2024-01-15 * "Employer" "Salary - January 2024"
  Assets:US:Bank:Checking           2500.00 USD  ; Net pay
  Assets:US:IRS:Withholding          500.00 USD  ; Federal withholding
  Income:US:Salary                 -3000.00 USD  ; Gross salary
```

Close tax year with return filing:

```beancount
2024-04-15 * "IRS" "Tax Return 2023 Settlement"
  Expenses:Tax:US:TotalLiability   6000.00 USD
  Assets:US:IRS:Withholding       -5800.00 USD  ; Consume withholding
  Assets:US:Bank:Checking          -200.00 USD  ; Pay difference
```

### Multi-Currency Transactions

```beancount
2024-01-10 * "Currency Exchange" "USD to INR"
  Assets:IN:ICICI:Savings     100000.00 INR @ 0.012 USD
  Assets:US:Chase:Checking     -1200.00 USD
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/rajguru7/accountant/issues
- Documentation: See `spec.md` for detailed technical specifications

## Acknowledgments

Built on:
- [Beancount](https://github.com/beancount/beancount) - Plain text accounting
- [Fava](https://github.com/beancount/fava) - Web interface for Beancount
- [Smart Importer](https://github.com/beancount/smart_importer) - ML-based import assistance
