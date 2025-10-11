#!/usr/bin/env python3
"""
Test script for Calculator GUI components
"""

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from calculator_core import Rechner, Waerungsrechner
        print("✅ Maxim library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Maxim: {e}")
        return False
    
    try:
        from calculator_core import tageszins
        print("✅ zinsen module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import zinsen: {e}")
        return False
    
    try:
        import tkinter as tk
        from tkinter import ttk
        print("✅ tkinter imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import tkinter: {e}")
        return False
    
    return True

def test_calculator():
    """Test basic calculator functionality"""
    print("\nTesting calculator...")
    
    try:
        from calculator_core import Rechner
        calc = Rechner()
        
        # Test basic operations
        result = calc.add(5, 3)
        assert result == 8, f"Addition failed: expected 8, got {result}"
        
        result = calc.subtract(10, 4)
        assert result == 6, f"Subtraction failed: expected 6, got {result}"
        
        result = calc.multiply(3, 4)
        assert result == 12, f"Multiplication failed: expected 12, got {result}"
        
        result = calc.divide(15, 3)
        assert result == 5, f"Division failed: expected 5, got {result}"
        
        print("✅ Calculator operations working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Calculator test failed: {e}")
        return False

def test_currency_converter():
    """Test currency converter functionality"""
    print("\nTesting currency converter...")
    
    try:
        from calculator_core import Waerungsrechner
        
        # Test EUR to USD
        result = Waerungsrechner.eur_in_usd(100)
        assert result is not None, "EUR to USD conversion failed"
        
        # Test USD to EUR
        result = Waerungsrechner.usd_in_eur(100)
        assert result is not None, "USD to EUR conversion failed"
        
        print("✅ Currency converter working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Currency converter test failed: {e}")
        return False

def test_interest_calculator():
    """Test interest calculator functionality"""
    print("\nTesting interest calculator...")
    
    try:
        from calculator_core import tageszins
        
        # Test interest calculation
        result = tageszins(1000, 5, "01.01.2024", "31.12.2024", "act/365")
        assert result is not None, "Interest calculation failed"
        assert isinstance(result, (int, float)), "Interest result should be numeric"
        
        print(f"✅ Interest calculator working correctly (result: {result})")
        return True
        
    except Exception as e:
        print(f"❌ Interest calculator test failed: {e}")
        return False

def test_gui_creation():
    """Test if GUI can be created without errors"""
    print("\nTesting GUI creation...")
    
    try:
        import tkinter as tk
        from calculator_gui import ModernCalculatorGUI
        
        # Create a test root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Try to create the GUI
        app = ModernCalculatorGUI(root)
        
        # Clean up
        root.destroy()
        
        print("✅ GUI creation successful")
        return True
        
    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Calculator GUI Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_calculator,
        test_currency_converter,
        test_interest_calculator,
        test_gui_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your GUI should work perfectly.")
        print("\n🚀 To launch the GUI, run:")
        print("   python gui_launcher.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()
