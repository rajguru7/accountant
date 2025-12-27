"""
Inflation Plugin for Beancount - SFIS
Generates synthetic inflation-adjusted currency prices
"""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Any


class InflationPlugin:
    """
    Plugin to generate inflation-adjusted synthetic currency prices
    
    Creates price directives for inflation-adjusted currencies (e.g., I-USD)
    that can be used to view portfolio values in "real" terms.
    """
    
    def __init__(self):
        """Initialize the inflation plugin"""
        pass
    
    def generate_prices(
        self, 
        commodity: str, 
        base_currency: str, 
        cpi_data: Dict[date, Decimal],
        base_date: date
    ) -> List[Dict[str, Any]]:
        """
        Generate inflation-adjusted price entries
        
        Args:
            commodity: Name of inflation-adjusted commodity (e.g., 'I-USD')
            base_currency: Base currency (e.g., 'USD')
            cpi_data: Dictionary mapping dates to CPI values
            base_date: Reference date for price normalization (price = 1.0)
            
        Returns:
            List of price entry dictionaries
        """
        if not cpi_data:
            return []
        
        # Get base CPI value
        if base_date not in cpi_data:
            # Find closest date
            sorted_dates = sorted(cpi_data.keys())
            base_date = min(sorted_dates, key=lambda d: abs((d - base_date).days))
        
        base_cpi = cpi_data[base_date]
        
        prices = []
        for price_date, cpi_value in sorted(cpi_data.items()):
            # Calculate price relative to base date
            # Price = current_cpi / base_cpi
            price_value = (cpi_value / base_cpi).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            prices.append({
                'date': price_date,
                'commodity': commodity,
                'base_currency': base_currency,
                'value': price_value
            })
        
        return prices
    
    def load_cpi_data(self, cpi_dict: Dict[str, float]) -> Dict[date, Decimal]:
        """
        Load CPI data from dictionary format
        
        Args:
            cpi_dict: Dictionary with date strings as keys (YYYY-MM) and CPI values
            
        Returns:
            Dictionary mapping date objects to Decimal CPI values
        """
        cpi_data = {}
        
        for date_str, cpi_value in cpi_dict.items():
            # Parse date string (YYYY-MM format)
            year, month = date_str.split('-')
            # Use first day of month
            price_date = date(int(year), int(month), 1)
            cpi_data[price_date] = Decimal(str(cpi_value))
        
        return cpi_data
    
    def format_price_entry(self, price_entry: Dict[str, Any]) -> str:
        """
        Format a price entry as a Beancount price directive
        
        Args:
            price_entry: Dictionary with date, commodity, base_currency, and value
            
        Returns:
            Formatted Beancount price directive string
        """
        entry_date = price_entry['date'].strftime('%Y-%m-%d')
        commodity = price_entry['commodity']
        base_currency = price_entry['base_currency']
        value = price_entry['value']
        
        return f"{entry_date} price {commodity} {value} {base_currency}"
    
    def calculate_inflation_rate(self, cpi_start: Decimal, cpi_end: Decimal) -> Decimal:
        """
        Calculate inflation rate between two CPI values
        
        Args:
            cpi_start: Starting CPI value
            cpi_end: Ending CPI value
            
        Returns:
            Inflation rate as a decimal (e.g., 0.02 for 2%)
        """
        if cpi_start == 0:
            return Decimal('0')
        
        return ((cpi_end - cpi_start) / cpi_start).quantize(
            Decimal('0.0001'), rounding=ROUND_HALF_UP
        )
    
    def adjust_value_for_inflation(self, nominal_value: Decimal, inflation_rate: Decimal) -> Decimal:
        """
        Adjust a nominal value to real value using inflation rate
        
        Args:
            nominal_value: Value in nominal terms
            inflation_rate: Inflation rate as decimal
            
        Returns:
            Real value adjusted for inflation
        """
        return (nominal_value / (Decimal('1') + inflation_rate)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    
    def generate_beancount_file(
        self,
        commodity: str,
        base_currency: str,
        cpi_data: Dict[date, Decimal],
        base_date: date,
        output_file: str
    ) -> None:
        """
        Generate a complete Beancount file with price directives
        
        Args:
            commodity: Inflation-adjusted commodity name
            base_currency: Base currency
            cpi_data: CPI data dictionary
            base_date: Reference date for normalization
            output_file: Path to output file
        """
        prices = self.generate_prices(commodity, base_currency, cpi_data, base_date)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"; Inflation-adjusted prices for {commodity}\n")
            f.write(f"; Base date: {base_date.strftime('%Y-%m-%d')}\n")
            f.write(f"; Generated {len(prices)} price entries\n\n")
            
            # Define the commodity
            f.write(f"{base_date.strftime('%Y-%m-%d')} commodity {commodity}\n")
            f.write(f'  name: "Inflation-adjusted {base_currency}"\n\n')
            
            # Write price entries
            for price_entry in prices:
                f.write(self.format_price_entry(price_entry))
                f.write('\n')
