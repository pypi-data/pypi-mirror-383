"""
Currency converter CLI module for Corally.
"""

from ..core import CurrencyConverter


def currency_cli() -> None:
    """Standalone currency converter CLI interface."""
    converter = CurrencyConverter()
    print("💱 Corally Currency Converter")
    print("=" * 30)
    
    while True:
        print("\nAvailable conversions:")
        print("1: EUR to USD")
        print("2: USD to EUR")
        print("3: EUR to GBP")
        print("4: GBP to EUR")
        print("5: EUR to JPY")
        print("6: JPY to EUR")
        print("7: Exit")
        
        try:
            choice = int(input("\nSelect conversion (1-7): "))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            continue
        
        if choice == 7:
            print("👋 Currency converter closed.")
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


if __name__ == "__main__":
    currency_cli()
