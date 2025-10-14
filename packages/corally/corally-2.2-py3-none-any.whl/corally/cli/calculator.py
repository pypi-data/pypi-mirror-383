"""
Calculator CLI module for Corally.
"""

from ..core import CalculatorCore


def calculator_cli() -> None:
    """Standalone calculator CLI interface."""
    calc = CalculatorCore()
    print("🧮 Corally Calculator")
    print("=" * 20)
    
    while True:
        print("\nOperations:")
        print("1: Addition")
        print("2: Subtraction")
        print("3: Multiplication")
        print("4: Division")
        print("5: Exit")
        
        try:
            choice = int(input("\nSelect operation (1-5): "))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            continue
        
        if choice == 5:
            print("👋 Calculator closed.")
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


if __name__ == "__main__":
    calculator_cli()
