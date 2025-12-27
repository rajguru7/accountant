#!/usr/bin/env python
"""
Generate inflation-adjusted price data for SFIS
Creates I-USD (Inflation-adjusted USD) price directives based on CPI data
"""

from datetime import date
from decimal import Decimal

from plugins.inflation import InflationPlugin


def main():
    """Generate inflation price data"""
    plugin = InflationPlugin()

    # Sample CPI data for US (simplified for demonstration)
    # In production, this would be fetched from BLS or other sources
    us_cpi_data = {
        "2023-01": 299.170,
        "2023-02": 300.840,
        "2023-03": 301.836,
        "2023-04": 303.363,
        "2023-05": 304.127,
        "2023-06": 305.109,
        "2023-07": 305.691,
        "2023-08": 307.026,
        "2023-09": 307.789,
        "2023-10": 307.671,
        "2023-11": 308.003,
        "2023-12": 306.746,
        "2024-01": 308.417,
        "2024-02": 310.326,
        "2024-03": 312.230,
    }

    # Load and convert CPI data
    cpi_data = plugin.load_cpi_data(us_cpi_data)

    # Generate prices with January 2023 as base (price = 1.0)
    base_date = date(2023, 1, 1)

    # Generate Beancount file
    output_file = "ledger/includes/inflation_usd.bean"
    plugin.generate_beancount_file(
        commodity="I-USD",
        base_currency="USD",
        cpi_data=cpi_data,
        base_date=base_date,
        output_file=output_file,
    )

    print(f"Generated inflation price data: {output_file}")
    print(f"Base date: {base_date}")
    print(f"Price entries: {len(cpi_data)}")

    # Calculate and display inflation rate
    start_cpi = cpi_data[date(2023, 1, 1)]
    end_cpi = cpi_data[date(2024, 3, 1)]
    inflation_rate = plugin.calculate_inflation_rate(start_cpi, end_cpi)

    print(f"\nInflation from {date(2023, 1, 1)} to {date(2024, 3, 1)}: {inflation_rate * 100:.2f}%")

    # Show how $100 from Jan 2023 compares to March 2024
    nominal_value = Decimal("100.00")
    real_value = plugin.adjust_value_for_inflation(nominal_value, inflation_rate)
    print(f"$100 in Jan 2023 = ${real_value} in real purchasing power (March 2024)")


if __name__ == "__main__":
    main()
