Technical Specification: Sovereign Financial Intelligence System (SFIS)
Status: Proposed
Author: AI Research Assistant
Target Persona: IT-Literate Individual Investor (US/India/Crypto)
Version: 1.2
1. Abstract
This document specifies the architecture for a "Sovereign Financial Intelligence System" (SFIS) designed to manage a complex, multi-jurisdictional personal finance portfolio. The system aims to solve the "fragmentation crisis" faced by individuals with assets in the United States (Chase, Robinhood, 401k) and India (ICICI, Zerodha, NPS), alongside cryptocurrency holdings. Unlike standard commercial Personal Financial Management (PFM) tools, SFIS prioritizes Algorithmic Sovereignty—ensuring the user retains full control over data ingestion, tax modeling, and inflation-adjusted analytics. The proposed solution utilizes a Plain Text Accounting (PTA) core based on Beancount, supported by a generalized, technology-agnostic ingestion layer.
2. Problem Statement & Requirements
2.1 The Core Problem
Sophisticated investors operating across borders face three distinct challenges that monolithic software fails to address:
 * Multi-Commodity Complexity: Standard apps treat "currency" as a metadata tag rather than a commodity. They fail to preserve historical cost basis for tax lots across currency fluctuations (e.g., purchasing INR assets with USD sources).
 * Regulatory Divergence: The system must handle two distinct fiscal years (US: Jan-Dec, India: Apr-Mar) and disparate tax treatments (US: FIFO/Specific ID, India: Grandfathered LTCG).
 * Data Silos: Indian financial data is locked behind PDF statements or restricted APIs (Sahamati), while US data requires expensive aggregators.
2.2 Design Goals
 * Modularity: Ingestion logic must be decoupled from the core ledger.
 * Extensibility: Analytics (inflation, savings rate) must be scriptable plugins, not hardcoded features.
 * Privacy: The system must be self-hosted with no data residing on third-party servers (except transient aggregator transit).
 * Automation: Manual entry must be reduced to near-zero via "Generalized Drivers."
3. Alternatives Analysis & Rejection Rationale
The following existing solutions were evaluated and rejected based on the specific constraints of this project.
3.1 Firefly III
 * Description: A popular self-hosted PHP/Laravel budgeting application.
 * Verdict: Rejected.
 * Rationale:
   * Investment Limitations: Firefly III treats assets primarily as monetary balances. It lacks native support for "Tax Lots" (tracking the specific date and price of each share purchased), which is non-negotiable for calculating Capital Gains Tax in both US and India.
   * Rigid Currency Handling: While multi-currency is supported, it often relies on converting transaction values at the moment of entry, destroying the historical cost basis required for accurate audit trails in volatile FX markets.
3.2 Actual Budget
 * Description: A local-first, Zero-Based Budgeting (ZBB) tool.
 * Verdict: Rejected.
 * Rationale:
   * Scope Mismatch: Excellent for budgeting (envelope method) but insufficient for investment performance analysis (XIRR, TWR) or complex crypto cost-basis tracking.
3.3 Sahamati (Account Aggregator Framework)
 * Description: India's RBI-regulated framework for financial data sharing.
 * Verdict: Rejected (as a direct integration).
 * Rationale:
   * Access Control: Currently, the AA framework restricts programmatic access (Financial Information User - FIU license) to regulated entities. Individual developers cannot obtain API keys to fetch their own data programmatically without routing through a third-party app, violating the privacy requirement.
4. System Architecture
The SFIS architecture follows a Hub-and-Spoke pattern, centered on a text-based ledger.
4.1 Core Components
 * The Ledger (Hub): Beancount (Python). Stores all financial truth in human-readable text files.
 * The Interface: Fava. A web UI for visualization, filtering, and debugging.
 * The Ingestion Layer (Spokes): A custom Python framework implementing "Generalized Drivers" (see Section 5).
 * The Analytics Layer: Python plugins injecting synthetic transactions (e.g., for inflation or accrued tax).
4.2 Directory Structure Specification
/financial-sovereignty
├── /ledger                   # The Database (Git Repository)
│   ├── main.bean             # Entry point
│   ├── /accounts             # Chart of Accounts definitions
│   └── /includes             # Monthly transaction files (e.g., 2024-05.bean)
├── /ingestion                # The Generalized Ingestion Framework
│   ├── /drivers              # Generic Tech Drivers (CSV, PDF, API)
│   ├── /config               # YAML definitions for each bank
│   └── runner.py             # Execution controller
├── /plugins                  # Custom Logic
│   ├── inflation.py          # CPI Adjustment Logic
│   └── india_tax.py          # STCG/LTCG Classifier
└── /documents                # PDF Archive (linked to transactions)
5. Detailed Design: The Generalized Ingestion Framework
To satisfy the "least manual" and "reusable" requirements, we define an architecture where code is written once per file format, not per bank.
5.1 Concept: Technology Drivers
Instead of icici_importer.py and chase_importer.py, we implement generic drivers that take a configuration object.
Driver A: GenericCSVImporter
 * Purpose: Handles any delimited text file (Chase, Robinhood, Zerodha Tradebook).
 * Configuration Schema (YAML):
   institution: "Zerodha"
driver: "csv"
file_pattern: "tradebook-*.csv"
skip_header_lines: 1
columns:
  date: "trade_date"
  narration: "symbol"
  amount: "net_amount" # Automatically detects sign
  meta:
    - "order_id"
    - "trade_type"

 * Machine Learning Hook: This driver wraps the smart_importer library. It sends the extracted narration to a local ML model (trained on your past ledger) to predict the correct Expenses: or Assets: account automatically.
Driver B: GenericPDFImporter
 * Purpose: Extracts tabular data from PDFs (ICICI Bank, NPS).
 * Technology: Wraps tabula-py (Java based) or pdfplumber.
 * Configuration Schema (YAML):
   institution: "ICICI Bank"
driver: "pdf_table"
password_algo: "icici_dob" # References a local function for password generation
table_area:  # Percentage coordinates of the table
columns:
  date: 0 # Column index
  narration: 2
  withdrawal: 4
  deposit: 5

Driver C: APIAggregatorBridge
 * Purpose: Fetches data from aggregation services.
 * Implementation:
   * US: SimpleFIN Bridge. Configured with a "Setup Token". It fetches a standardized JSON and maps it to Beancount accounts.
   * Crypto: Rotki Bridge. Queries the local Rotki API. Instead of importing every micro-transaction (spam), it imports Balance Assertions. This keeps the ledger clean while Rotki handles the granular chain analysis.
6. Specification: Tax & Reconciliation Workflow
This section formalizes the handling of dual-jurisdiction tax obligations, a critical requirement for the user.
6.1 The "Asset-Liability" Tax Model
Taxes are not expenses until the final return is filed. Throughout the year, they are tracked as Assets (Withholding) or Liabilities (Accrual).
Phase 1: Accrual (During the Year)
 * US Salary: Split paycheck entries.
   * Assets:US:Bank (Net Pay)
   * Assets:US:IRS:Withholding (Tax Withheld)
   * Income:US:Salary (Gross Pay)
 * India Interest: Split transaction.
   * Assets:IN:Bank (Interest Received)
   * Assets:IN:ITD:TDS (Tax Deducted at Source)
   * Income:IN:Interest (Gross Interest)
Phase 2: The "Close" (Filing Return)
A single manual transaction is recorded to "close" the tax year.
 * Scenario: Filing US 1040 claiming Foreign Tax Credit (FTC).
   2024-04-15 * "IRS" "Tax Return 2023 Settlement"
  Expenses:Tax:US:TotalLiability    15000.00 USD
  Assets:US:IRS:Withholding        -12000.00 USD  ; Consume US withholding
  Assets:IN:ITD:TDS               -200000.00 INR @ 0.012 USD ; Consume India TDS as FTC
  Assets:US:Bank                     -600.00 USD  ; Pay the difference

   This explicitly links the Indian tax paid to the US liability, creating an audit trail for the FTC.
6.2 Fiscal Year Management
 * US Reports: Filter date >= 2023-01-01 and date <= 2023-12-31.
 * India Reports: Define a custom "Fiscal Year" tag or option in Fava to filter date >= 2023-04-01 and date <= 2024-03-31. The underlying ledger is continuous; the view changes.
7. Advanced Analytics Specification
7.1 Real vs. Nominal Growth (Inflation)
 * Component: plugins/inflation.py.
 * Logic:
   * Define a synthetic currency I-USD (Inflation-Adjusted USD).
   * Fetch CPI data (US BLS & India CPI).
   * Generate daily price entries: 2024-01-01 price I-USD 1.05 USD.
 * Output: In Fava, switching the display currency to I-USD automatically discounts all historical values, revealing the "Real" purchasing power of the portfolio.
7.2 Custom Metric: Savings Rate
 * Definition: (Income - Expenses) / Income.
 * Implementation: A Fava extension (JavaScript + Python) that queries the ledger.
 * Nuance: It must exclude "Pass-through" expenses (reimbursable work expenses) and include "Hidden" income (Employer 401k match). These are handled via tags (#reimbursable) in the ledger, which the query filters out.
8. Conclusion
This specification outlines a system that prioritizes data sovereignty and architectural decoupling. By rejecting monolithic apps in favor of a Beancount core with Generalized Ingestion Drivers, the user gains the ability to:
 * Automate data flow from hostile sources (PDFs) and friendly sources (APIs).
 * Accurately model complex cross-border tax scenarios (FTC, TDS).
 * Analyze wealth in "Real" terms, stripping away the noise of inflation.
This system requires an initial time investment to configure the YAML drivers, but offers the lowest possible maintenance burden and highest analytical depth for the long term.
