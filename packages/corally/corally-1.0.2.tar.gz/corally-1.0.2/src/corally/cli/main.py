"""
Main CLI entry point for Corally calculator suite.
"""

import sys
from typing import Optional

from ..core import CalculatorCore, CurrencyConverter, InterestCalculator
from ..gui.launcher import launch_gui
from ..api.server import start_server
from ..api.free_server import start_free_server


def main_cli() -> None:
    """Main CLI interface for Corally calculator suite."""
    print("🧮 Corally Calculator Suite")
    print("=" * 40)
    
    while True:
        print("\nSelect an option:")
        print("1: Basic Calculator")
        print("2: Currency Converter")
        print("3: Interest Calculator")
        print("4: Launch GUI")
        print("5: Start API Server (Free)")
        print("6: Start API Server (Paid)")
        print("7: Exit")
        
        try:
            choice = int(input("\nEnter your choice (1-7): "))
        except ValueError:
            print("❌ Invalid input. Please enter a number between 1-7.")
            continue
        
        if choice == 7:
            print("👋 Goodbye!")
            break
        elif choice == 1:
            calculator_cli()
        elif choice == 2:
            currency_cli()
        elif choice == 3:
            interest_cli()
        elif choice == 4:
            print("🚀 Launching GUI...")
            launch_gui()
        elif choice == 5:
            print("🌐 Starting Free API Server...")
            start_free_server()
        elif choice == 6:
            print("🌐 Starting Paid API Server...")
            start_server()
        else:
            print("❌ Invalid choice. Please select 1-7.")


def calculator_cli() -> None:
    """Basic calculator CLI interface."""
    calc = CalculatorCore()
    print("\n🧮 Basic Calculator")
    print("-" * 20)
    
    while True:
        print("\nOperations:")
        print("1: Addition")
        print("2: Subtraction")
        print("3: Multiplication")
        print("4: Division")
        print("5: Back to main menu")
        
        try:
            choice = int(input("\nSelect operation (1-5): "))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            continue
        
        if choice == 5:
            break
        elif choice not in [1, 2, 3, 4]:
            print("❌ Invalid choice. Please select 1-5.")
            continue
        
        try:
            a = float(input("Enter first number: "))
            b = float(input("Enter second number: "))
        except ValueError:
            print("❌ Invalid number input.")
            continue
        
        result = None
        if choice == 1:
            result = calc.add(a, b)
            print(f"✅ {a} + {b} = {result}")
        elif choice == 2:
            result = calc.subtract(a, b)
            print(f"✅ {a} - {b} = {result}")
        elif choice == 3:
            result = calc.multiply(a, b)
            print(f"✅ {a} × {b} = {result}")
        elif choice == 4:
            result = calc.divide(a, b)
            if result is not None:
                print(f"✅ {a} ÷ {b} = {result}")


def currency_cli() -> None:
    """Currency converter CLI interface."""
    converter = CurrencyConverter()
    print("\n💱 Currency Converter")
    print("-" * 22)
    
    while True:
        print("\nAvailable conversions:")
        print("1: EUR to USD")
        print("2: USD to EUR")
        print("3: EUR to GBP")
        print("4: GBP to EUR")
        print("5: EUR to JPY")
        print("6: JPY to EUR")
        print("7: Back to main menu")
        
        try:
            choice = int(input("\nSelect conversion (1-7): "))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            continue
        
        if choice == 7:
            break
        elif choice not in range(1, 7):
            print("❌ Invalid choice. Please select 1-7.")
            continue
        
        try:
            amount = float(input("Enter amount: "))
        except ValueError:
            print("❌ Invalid amount.")
            continue
        
        result = None
        if choice == 1:
            result = converter.eur_to_usd(amount)
            print(f"✅ {amount} EUR = {result} USD")
        elif choice == 2:
            result = converter.usd_to_eur(amount)
            print(f"✅ {amount} USD = {result} EUR")
        elif choice == 3:
            result = converter.eur_to_gbp(amount)
            print(f"✅ {amount} EUR = {result} GBP")
        elif choice == 4:
            result = converter.gbp_to_eur(amount)
            print(f"✅ {amount} GBP = {result} EUR")
        elif choice == 5:
            result = converter.eur_to_jpy(amount)
            print(f"✅ {amount} EUR = {result} JPY")
        elif choice == 6:
            result = converter.jpy_to_eur(amount)
            print(f"✅ {amount} JPY = {result} EUR")


def interest_cli() -> None:
    """Interest calculator CLI interface."""
    print("\n📈 Interest Calculator")
    print("-" * 22)
    
    while True:
        print("\nCalculation methods:")
        print("1: 30/360 method")
        print("2: act/360 method")
        print("3: act/365 method")
        print("4: act/act method")
        print("5: Back to main menu")
        
        try:
            choice = int(input("\nSelect method (1-5): "))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            continue
        
        if choice == 5:
            break
        elif choice not in range(1, 5):
            print("❌ Invalid choice. Please select 1-5.")
            continue
        
        try:
            principal = float(input("Enter principal amount: "))
            rate = float(input("Enter interest rate (%): "))
            start_date = input("Enter start date (DD.MM.YYYY): ")
            end_date = input("Enter end date (DD.MM.YYYY): ")
        except ValueError:
            print("❌ Invalid input.")
            continue
        
        methods = ["30/360", "act/360", "act/365", "act/act"]
        method = methods[choice - 1]
        
        try:
            result = InterestCalculator.calculate_interest(
                principal, rate, start_date, end_date, method
            )
            print(f"✅ Interest ({method}): {result}")
        except Exception as e:
            print(f"❌ Error calculating interest: {e}")


if __name__ == "__main__":
    main_cli()
