# 🧮 Calculator Suite

A comprehensive calculator application suite featuring both modern GUI and console interfaces. This project combines multiple calculation tools into one unified system with both traditional console applications and a sleek modern GUI.

## 🌟 Features

### 🧮 Basic Calculator
- **Four basic operations**: Addition, subtraction, multiplication, division
- **Automatic logging**: All calculations saved to `rechner_log.csv`
- **Error handling**: Robust input validation and error reporting
- **GUI & Console**: Available in both modern GUI and traditional console interface

### 💱 Currency Converter
- **Static rates**: Predefined exchange rates for common currency pairs
- **Live rates**: Real-time exchange rates via API integration
- **Supported currencies**: EUR, USD, GBP, JPY and more
- **Caching system**: Improved performance with 1-hour cache
- **Dual access**: Available via dropdown menu in GUI or console application

### 📈 Interest Calculator
- **Multiple methods**: 30/360, act/360, act/365, act/act calculation methods
- **Date range support**: Calculate interest between any two dates
- **Professional accuracy**: Financial-grade calculations
- **Flexible input**: DD.MM.YYYY date format support

### 🌐 Live Currency API
- **Two API modes**: Free (no registration) and Paid (API key required)
- **Real-time rates**: Current market exchange rates
- **Multiple providers**: Support for various API services
- **Server management**: Built-in API server with start/stop controls
- **Health monitoring**: Server status checking and diagnostics

### 🎨 Modern GUI Interface
- **Dark theme**: Professional dark mode interface
- **Tabbed layout**: Organized functionality in separate tabs
- **Lazy loading**: Efficient resource usage with on-demand tab loading
- **Menu system**: Dropdown access to additional tools
- **Real-time feedback**: Live status updates and progress indicators

## 🚀 Quick Start

### Option 1: GUI Interface (Recommended)
```bash
python gui_launcher.py
```

### Option 2: Console Interface (Traditional)
```bash
python Hauptprogramm.py
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Dependencies Installation
```bash
pip install -r requirements.txt
```

**Required packages:**
- `fastapi>=0.68.0` - Web framework for API server
- `uvicorn>=0.15.0` - ASGI server for FastAPI
- `httpx>=0.24.0` - Async HTTP client
- `requests>=2.25.0` - HTTP library for API calls
- `python-dotenv>=0.19.0` - Environment variable management

### Optional: API Key Setup
For live currency conversion with paid APIs:

1. **Get an API key** from one of these providers:
   - [ExchangeRate-API](https://exchangerate-api.com/) (Free tier available)
   - [Fixer.io](https://fixer.io/) (Free tier available)
   - [CurrencyAPI](https://currencyapi.com/) (Free tier available)

2. **Create `.env` file** in project directory:
   ```env
   API_KEY=your_actual_api_key_here
   ```

## 🏗️ Project Structure

```
Calculator/
├── 🎨 GUI Applications
│   ├── calculator_gui.py      # Main GUI application
│   ├── gui_launcher.py        # GUI launcher with dependency checks
│   └── manage_api_server.py   # API server management utility
│
├── 🖥️ Console Applications
│   ├── Hauptprogramm.py       # Main console menu
│   ├── Rechner.py            # Console calculator
│   ├── Waerungsrechner.py    # Console currency converter
│   └── zinsen.py             # Console interest calculator
│
├── 📚 Core Library
│   ├── calculator_core.py    # Unified library (combines all functionality)
│   ├── Maxim.py              # Legacy library (deprecated)
│   └── zinsen.py             # Legacy library (deprecated)
│
├── 🌐 API Services
│   ├── api.py                # Paid API server (requires API key)
│   ├── api_free.py           # Free API server (no key required)
│   └── cache.csv             # API response cache
│
├── 🧪 Testing & Debugging
│   ├── test_api.py           # API functionality tests
│   ├── test_gui.py           # GUI component tests
│   ├── debug_api_error.py    # API debugging utilities
│   └── manage_api_server.py  # Server management tools
│
├── 📄 Configuration & Documentation
│   ├── requirements.txt      # Python dependencies
│   ├── README.md            # This documentation
│   └── QUICK_START_GUIDE.md # Quick setup guide
│
└── 📊 Data Files
    ├── rechner_log.csv       # Calculator operation logs
    └── cache.csv             # API response cache
```

## 🎯 Usage Guide

### GUI Interface

#### Main Tabs
1. **Basic Calculator**: Standard arithmetic operations with history
2. **Interest Calculator**: Financial interest calculations
3. **Live Currency API**: Real-time currency conversion

#### Tools Menu
- **Currency Converter (Static)**: Offline currency conversion with predefined rates
- **About**: Application information

#### API Server Management
- **Free API**: No setup required, works immediately
- **Paid API**: Requires API key in `.env` file
- **Server Controls**: Start, stop, and monitor API servers
- **Health Checks**: Automatic server status monitoring

### 📚 Core Library Usage

The project uses a **unified core library** (`calculator_core.py`) that combines all functionality:

```python
# New unified imports (recommended)
from calculator_core import CalculatorCore, CurrencyConverter, InterestCalculator

# Backward compatibility (old imports still work)
from calculator_core import Rechner, Waerungsrechner, tageszins

# Example usage
calc = CalculatorCore()
result = calc.add(5, 3)  # Returns 8.0 with CSV logging

converter = CurrencyConverter()
usd = converter.eur_to_usd(100)  # Returns 117.0

interest = InterestCalculator.calculate_interest(1000, 5, "01.01.2024", "31.12.2024")
```

**Benefits of unified library:**
- ✅ Single import for all functionality
- ✅ Improved type hints and error handling
- ✅ Backward compatibility with existing code
- ✅ Better organization and maintainability

### Console Interface

#### Available Programs
```bash
python Hauptprogramm.py     # Main menu system
python Rechner.py          # Basic calculator
python Waerungsrechner.py  # Currency converter  
python zinsen.py           # Interest calculator
```

#### API Server Management
```bash
python manage_api_server.py  # Server management utility
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for API configuration:
```env
# Required for paid API services
API_KEY=your_api_key_here

# Optional: Custom API endpoints
API_BASE_URL=https://api.exchangerate-api.com/v4/latest/
```

### Calculation Methods
The interest calculator supports multiple industry-standard methods:
- **30/360**: 30-day months, 360-day years
- **act/360**: Actual days, 360-day years  
- **act/365**: Actual days, 365-day years
- **act/act**: Actual days, actual years

### Currency Pairs
**Static rates** (predefined in calculator_core.py):
- EUR ↔ USD (1.17 rate)
- EUR ↔ GBP (0.87 rate)
- EUR ↔ JPY (173.84 rate)

**Live rates** (via API):
- 150+ currency pairs supported
- Real-time market rates
- 1-hour caching for performance

## 🛠️ Troubleshooting

### Common Issues

#### Import Errors
```bash
# Install missing dependencies
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.8+
```

#### API Server Issues
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Test API manually
curl "http://127.0.0.1:8000/convert?from_currency=EUR&to_currency=USD&amount=100"

# Check server logs
python debug_api_error.py
```

#### File Not Found Errors
Ensure all core files are in the same directory:
- `calculator_core.py` (required - unified core library)
- `api.py` or `api_free.py` (for live currency features)

#### GUI Issues
```bash
# Test GUI components
python test_gui.py

# Launch with debug info
python gui_launcher.py
```

### Debug Tools

#### API Debugging
```bash
python debug_api_error.py     # Test API connectivity
python test_api.py           # Comprehensive API tests
```

#### Server Management
```bash
python manage_api_server.py  # Interactive server management
```

#### GUI Testing
```bash
python test_gui.py           # Test GUI components
```

## 📊 Data Management

### Automatic Logging
- **Calculator operations**: Saved to `rechner_log.csv`
- **API responses**: Cached in `cache.csv` (1-hour expiry)
- **Server logs**: Written to `api.log`

### Data Formats
- **Dates**: DD.MM.YYYY (e.g., 31.12.2024)
- **Numbers**: Decimal point or comma supported
- **Currency codes**: ISO 4217 standard (EUR, USD, GBP, etc.)

## 🔒 Security Notes

1. **API Keys**: Never commit `.env` files to version control
2. **Local Server**: API server runs on localhost only (127.0.0.1)
3. **Input Validation**: All user inputs are validated and sanitized
4. **Error Handling**: Comprehensive error handling prevents crashes

## 🚀 Advanced Features

### API Caching System
- **1-hour cache**: Reduces API calls and improves performance
- **Automatic cleanup**: Expired entries removed automatically
- **Cache bypass**: Force fresh data when needed

### Server Health Monitoring
- **Automatic detection**: Server status checking
- **Port management**: Dynamic port allocation (8000-8009)
- **Process tracking**: PID-based process management

### Lazy Loading
- **Efficient startup**: Only essential components loaded initially
- **On-demand loading**: Tab content created when first accessed
- **Memory optimization**: Reduced memory footprint

## 🤝 Contributing

This project maintains backward compatibility with existing console applications while adding modern GUI functionality. When contributing:

1. **Preserve console interfaces**: Don't break existing command-line tools
2. **Maintain API compatibility**: Keep existing function signatures
3. **Add comprehensive tests**: Test both GUI and console functionality
4. **Document changes**: Update README and inline documentation

## 📜 License

This project is provided as-is for educational and personal use. The GUI enhancement maintains full compatibility with the original calculator project structure and functionality.

---

**Version**: 2.0
**Last Updated**: 2024
**Python Compatibility**: 3.8+
