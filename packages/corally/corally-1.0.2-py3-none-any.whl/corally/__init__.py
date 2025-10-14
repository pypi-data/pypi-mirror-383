"""
Corally - A comprehensive calculator suite with GUI and API support.

This package provides:
- Basic arithmetic operations with logging
- Currency conversion (static and live rates)
- Interest calculations with multiple methods
- Modern GUI interface
- REST API for currency conversion
- Command-line interface

Example usage:
    >>> from corally import CalculatorCore, CurrencyConverter
    >>> calc = CalculatorCore()
    >>> result = calc.add(5, 3)
    >>> print(result)  # 8.0
    
    >>> converter = CurrencyConverter()
    >>> usd = converter.eur_to_usd(100)
    >>> print(usd)  # 117.0
"""

from .core.calculator import CalculatorCore, CurrencyConverter, InterestCalculator

__version__ = "2.0.0"
__author__ = "Corally Team"
__email__ = "contact@corally.dev"
__description__ = "A comprehensive calculator suite with GUI and API support"

# Make main classes available at package level
__all__ = [
    "CalculatorCore",
    "CurrencyConverter", 
    "InterestCalculator",
    "__version__",
]
