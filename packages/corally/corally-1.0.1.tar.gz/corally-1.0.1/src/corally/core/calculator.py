"""
Calculator Suite Core Library

A unified library combining all calculator functionality:
- Basic arithmetic operations with logging
- Currency conversion (static rates)
- Interest calculations with multiple methods

This module replaces the separate Maxim.py and zinsen.py files.
"""

import csv
import os
from datetime import datetime
from typing import Optional, Union
from pathlib import Path


class CalculatorCore:
    """
    Main calculator class providing basic arithmetic operations with automatic logging.
    
    Features:
    - Four basic operations: add, subtract, multiply, divide
    - Automatic CSV logging of all operations
    - Robust error handling and input validation
    """
    
    def __init__(self, csv_file: Optional[str] = None):
        """
        Initialize calculator with CSV logging.

        Args:
            csv_file (str): Path to CSV file for logging operations.
                          If None, uses 'data/rechner_log.csv' in current directory.
        """
        if csv_file is None:
            # Create data directory if it doesn't exist
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            self.csv_file = str(data_dir / "rechner_log.csv")
        else:
            self.csv_file = csv_file
        self._initialize_csv()
    
    def _initialize_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist or is empty."""
        try:
            with open(self.csv_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                if file.tell() == 0:
                    writer.writerow(["Zahl 1", "Operator", "Zahl 2", "Ergebnis", "Zeitstempel"])
        except Exception as e:
            print(f"Warning: Could not initialize CSV file: {e}")
    
    def _log_operation(self, a: float, operator: str, b: float, result: float) -> None:
        """
        Log calculation to CSV file.
        
        Args:
            a (float): First number
            operator (str): Operation symbol
            b (float): Second number
            result (float): Calculation result
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.csv_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([a, operator, b, result, timestamp])
        except Exception as e:
            print(f"Warning: Could not log operation: {e}")
    
    def _validate_numbers(self, a: Union[str, int, float], b: Union[str, int, float]) -> tuple[float, float]:
        """
        Validate and convert input numbers to float.
        
        Args:
            a: First number (any numeric type or string)
            b: Second number (any numeric type or string)
            
        Returns:
            tuple[float, float]: Validated numbers as floats
            
        Raises:
            ValueError: If inputs cannot be converted to float
        """
        try:
            return float(a), float(b)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid number input: {e}")
    
    def add(self, a: Union[str, int, float], b: Union[str, int, float]) -> Optional[float]:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            float: Sum of a and b, or None if error
        """
        try:
            num_a, num_b = self._validate_numbers(a, b)
            result = num_a + num_b
            self._log_operation(num_a, "+", num_b, result)
            return result
        except ValueError as e:
            print(f"Addition error: {e}")
            return None
    
    def subtract(self, a: Union[str, int, float], b: Union[str, int, float]) -> Optional[float]:
        """
        Subtract two numbers.
        
        Args:
            a: Minuend (first number)
            b: Subtrahend (second number)
            
        Returns:
            float: Difference of a and b, or None if error
        """
        try:
            num_a, num_b = self._validate_numbers(a, b)
            result = num_a - num_b
            self._log_operation(num_a, "-", num_b, result)
            return result
        except ValueError as e:
            print(f"Subtraction error: {e}")
            return None
    
    def multiply(self, a: Union[str, int, float], b: Union[str, int, float]) -> Optional[float]:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            float: Product of a and b, or None if error
        """
        try:
            num_a, num_b = self._validate_numbers(a, b)
            result = num_a * num_b
            self._log_operation(num_a, "*", num_b, result)
            return result
        except ValueError as e:
            print(f"Multiplication error: {e}")
            return None
    
    def divide(self, a: Union[str, int, float], b: Union[str, int, float]) -> Optional[float]:
        """
        Divide two numbers.
        
        Args:
            a: Dividend (first number)
            b: Divisor (second number)
            
        Returns:
            float: Quotient of a and b, or None if error
        """
        try:
            num_a, num_b = self._validate_numbers(a, b)
            if num_b == 0:
                print("Division error: Division by zero is not allowed!")
                return None
            result = num_a / num_b
            self._log_operation(num_a, "/", num_b, result)
            return result
        except ValueError as e:
            print(f"Division error: {e}")
            return None


class CurrencyConverter:
    """
    Currency converter with predefined exchange rates.
    
    Supported conversions:
    - EUR ↔ USD
    - EUR ↔ GBP  
    - EUR ↔ JPY
    """
    
    # Exchange rates (static)
    RATES = {
        'EUR_TO_USD': 1.17,
        'EUR_TO_GBP': 0.87,
        'EUR_TO_JPY': 173.84
    }
    
    @classmethod
    def _validate_amount(cls, amount: Union[str, int, float]) -> float:
        """
        Validate and convert amount to float.
        
        Args:
            amount: Amount to convert
            
        Returns:
            float: Validated amount
            
        Raises:
            ValueError: If amount cannot be converted to float
        """
        try:
            return float(amount)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid amount: {e}")
    
    @classmethod
    def eur_to_usd(cls, eur: Union[str, int, float]) -> Optional[float]:
        """Convert EUR to USD."""
        try:
            amount = cls._validate_amount(eur)
            result = amount * cls.RATES['EUR_TO_USD']
            return round(result, 2)
        except ValueError as e:
            print(f"EUR to USD conversion error: {e}")
            return None
    
    @classmethod
    def usd_to_eur(cls, usd: Union[str, int, float]) -> Optional[float]:
        """Convert USD to EUR."""
        try:
            amount = cls._validate_amount(usd)
            result = amount / cls.RATES['EUR_TO_USD']
            return round(result, 2)
        except ValueError as e:
            print(f"USD to EUR conversion error: {e}")
            return None
    
    @classmethod
    def eur_to_gbp(cls, eur: Union[str, int, float]) -> Optional[float]:
        """Convert EUR to GBP."""
        try:
            amount = cls._validate_amount(eur)
            result = amount * cls.RATES['EUR_TO_GBP']
            return round(result, 2)
        except ValueError as e:
            print(f"EUR to GBP conversion error: {e}")
            return None
    
    @classmethod
    def gbp_to_eur(cls, gbp: Union[str, int, float]) -> Optional[float]:
        """Convert GBP to EUR."""
        try:
            amount = cls._validate_amount(gbp)
            result = amount / cls.RATES['EUR_TO_GBP']
            return round(result, 2)
        except ValueError as e:
            print(f"GBP to EUR conversion error: {e}")
            return None
    
    @classmethod
    def eur_to_jpy(cls, eur: Union[str, int, float]) -> Optional[float]:
        """Convert EUR to JPY."""
        try:
            amount = cls._validate_amount(eur)
            result = amount * cls.RATES['EUR_TO_JPY']
            return round(result, 2)
        except ValueError as e:
            print(f"EUR to JPY conversion error: {e}")
            return None
    
    @classmethod
    def jpy_to_eur(cls, jpy: Union[str, int, float]) -> Optional[float]:
        """Convert JPY to EUR."""
        try:
            amount = cls._validate_amount(jpy)
            result = amount / cls.RATES['EUR_TO_JPY']
            return round(result, 2)
        except ValueError as e:
            print(f"JPY to EUR conversion error: {e}")
            return None


class InterestCalculator:
    """
    Interest calculator supporting multiple calculation methods.
    
    Supported methods:
    - 30/360: 30-day months, 360-day years
    - act/360: Actual days, 360-day years
    - act/365: Actual days, 365-day years  
    - act/act: Actual days, actual years
    """
    
    VALID_METHODS = ["30/360", "act/360", "act/365", "act/act"]
    
    @classmethod
    def calculate_interest(
        cls, 
        capital: Union[str, int, float], 
        interest_rate: Union[str, int, float], 
        start_date: str, 
        end_date: str, 
        method: str = "act/365"
    ) -> Optional[float]:
        """
        Calculate interest between two dates using specified method.
        
        Args:
            capital: Principal amount
            interest_rate: Annual interest rate (percentage)
            start_date: Start date in DD.MM.YYYY format
            end_date: End date in DD.MM.YYYY format
            method: Calculation method (30/360, act/360, act/365, act/act)
            
        Returns:
            float: Calculated interest amount, or None if error
        """
        try:
            # Validate inputs
            cap = float(capital)
            rate = float(interest_rate) / 100  # Convert percentage to decimal
            
            if method not in cls.VALID_METHODS:
                raise ValueError(f"Invalid method. Allowed: {', '.join(cls.VALID_METHODS)}")
            
            # Parse dates
            d1 = datetime.strptime(start_date, "%d.%m.%Y")
            d2 = datetime.strptime(end_date, "%d.%m.%Y")
            
            # Calculate days and year basis
            if method == "30/360":
                days = (d2.year - d1.year) * 360 + (d2.month - d1.month) * 30 + (d2.day - d1.day)
                year_basis = 360
            else:
                days = (d2 - d1).days
                if method == "act/360":
                    year_basis = 360
                elif method in ("act/365", "act/act"):
                    year_basis = 365
            
            # Calculate interest
            interest = cap * rate * (days / year_basis)
            return round(interest, 2)
            
        except (ValueError, TypeError) as e:
            print(f"Interest calculation error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in interest calculation: {e}")
            return None


# Backward compatibility aliases
Rechner = CalculatorCore
Waerungsrechner = CurrencyConverter
tageszins = InterestCalculator.calculate_interest

# Legacy method aliases for Waerungsrechner
# CurrencyConverter.eur_in_usd = CurrencyConverter.eur_to_usd
# CurrencyConverter.usd_in_eur = CurrencyConverter.usd_to_eur
# CurrencyConverter.eur_in_bp = CurrencyConverter.eur_to_gbp
# CurrencyConverter.bp_in_eur = CurrencyConverter.gbp_to_eur
# CurrencyConverter.eur_in_yen = CurrencyConverter.eur_to_jpy
# CurrencyConverter.yen_in_euro = CurrencyConverter.jpy_to_eur


def main():
    """Interactive console interface for interest calculation."""
    print("📊 Interest Calculator\n")
    
    try:
        capital = float(input("Capital (€): "))
        rate = float(input("Interest rate (% per year): "))
        start_date = input("Start date (DD.MM.YYYY): ")
        end_date = input("End date (DD.MM.YYYY): ")
        method = input(f"Method ({', '.join(InterestCalculator.VALID_METHODS)}): ")
        
        interest = InterestCalculator.calculate_interest(capital, rate, start_date, end_date, method)
        
        if interest is not None:
            print("\n💰 Result:")
            print(f"Capital: {capital:,.2f} €")
            print(f"Period: {start_date} to {end_date}")
            print(f"Method: {method}")
            print(f"Interest: {interest:,.2f} €")
            print(f"Total: {capital + interest:,.2f} €")
        else:
            print("❌ Calculation failed. Please check your inputs.")
            
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Invalid input or operation cancelled.")


if __name__ == "__main__":
    main()
