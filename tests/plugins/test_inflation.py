"""
Tests for inflation adjustment plugin
Following Test-Driven Development approach
"""

from datetime import date
from decimal import Decimal

from plugins.inflation import InflationPlugin


class TestInflationPlugin:
    """Test suite for InflationPlugin"""

    def test_initialization(self):
        """Test that InflationPlugin can be initialized"""
        plugin = InflationPlugin()
        assert plugin is not None

    def test_generate_synthetic_currency_prices(self):
        """Test generation of inflation-adjusted currency prices"""
        plugin = InflationPlugin()

        # Define CPI data for testing
        cpi_data = {
            date(2024, 1, 1): Decimal("300.0"),
            date(2024, 2, 1): Decimal("303.0"),
            date(2024, 3, 1): Decimal("306.0"),
        }

        # Generate synthetic prices for I-USD (Inflation-adjusted USD)
        prices = plugin.generate_prices("I-USD", "USD", cpi_data, base_date=date(2024, 1, 1))

        # Should have one price entry per CPI data point
        assert len(prices) >= 3

        # Base date should have price of 1.0
        base_price = next((p for p in prices if p["date"] == date(2024, 1, 1)), None)
        assert base_price is not None
        assert base_price["value"] == Decimal("1.0")

        # Later dates should reflect inflation adjustment
        march_price = next((p for p in prices if p["date"] == date(2024, 3, 1)), None)
        assert march_price is not None
        # March CPI is 2% higher than January (306/300 = 1.02)
        assert march_price["value"] == Decimal("1.02")

    def test_load_cpi_data_from_dict(self):
        """Test loading CPI data from dictionary"""
        plugin = InflationPlugin()

        cpi_dict = {"2024-01": 300.0, "2024-02": 303.0, "2024-03": 306.0}

        cpi_data = plugin.load_cpi_data(cpi_dict)

        assert len(cpi_data) == 3
        assert date(2024, 1, 1) in cpi_data
        assert cpi_data[date(2024, 1, 1)] == Decimal("300.0")

    def test_format_beancount_price_entry(self):
        """Test formatting of Beancount price directive"""
        plugin = InflationPlugin()

        price_entry = {
            "date": date(2024, 1, 15),
            "commodity": "I-USD",
            "base_currency": "USD",
            "value": Decimal("1.05"),
        }

        formatted = plugin.format_price_entry(price_entry)

        # Should be in format: YYYY-MM-DD price I-USD 1.05 USD
        assert "2024-01-15" in formatted
        assert "price" in formatted
        assert "I-USD" in formatted
        assert "1.05" in formatted
        assert "USD" in formatted

    def test_calculate_inflation_rate(self):
        """Test calculation of inflation rate between two periods"""
        plugin = InflationPlugin()

        cpi_start = Decimal("300.0")
        cpi_end = Decimal("306.0")

        # (306 - 300) / 300 = 0.02 = 2%
        inflation_rate = plugin.calculate_inflation_rate(cpi_start, cpi_end)

        assert inflation_rate == Decimal("0.02")

    def test_adjust_value_for_inflation(self):
        """Test adjusting a nominal value to real value"""
        plugin = InflationPlugin()

        # $100 nominal with 2% inflation should be worth $98 in real terms
        nominal_value = Decimal("100.0")
        inflation_rate = Decimal("0.02")

        real_value = plugin.adjust_value_for_inflation(nominal_value, inflation_rate)

        # Real value = nominal / (1 + inflation)
        expected = Decimal("100.0") / Decimal("1.02")
        assert abs(real_value - expected) < Decimal("0.01")

    def test_generate_prices_with_empty_cpi_data(self):
        """Test handling of empty CPI data"""
        plugin = InflationPlugin()

        prices = plugin.generate_prices("I-USD", "USD", {}, base_date=date(2024, 1, 1))

        assert len(prices) == 0

    def test_generate_prices_different_base_date(self):
        """Test that changing base date changes price calculations"""
        plugin = InflationPlugin()

        cpi_data = {
            date(2024, 1, 1): Decimal("300.0"),
            date(2024, 2, 1): Decimal("303.0"),
            date(2024, 3, 1): Decimal("306.0"),
        }

        # Use February as base date
        prices = plugin.generate_prices("I-USD", "USD", cpi_data, base_date=date(2024, 2, 1))

        # February should have price of 1.0
        feb_price = next((p for p in prices if p["date"] == date(2024, 2, 1)), None)
        assert feb_price is not None
        assert feb_price["value"] == Decimal("1.0")

        # January should be adjusted relative to February (300/303 ≈ 0.99)
        jan_price = next((p for p in prices if p["date"] == date(2024, 1, 1)), None)
        assert jan_price is not None
        assert jan_price["value"] < Decimal("1.0")
