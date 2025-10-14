# 🧮 Corally Calculator Suite

[![PyPI version](https://badge.fury.io/py/corally.svg)](https://badge.fury.io/py/corally)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python calculator suite with modern GUI, CLI tools, and API servers. Features live currency conversion, interest calculations, and automatic operation logging.

## ✨ Features

- **🧮 Basic Calculator** - Four operations with automatic CSV logging
- **💱 Currency Converter** - Static rates + live API integration (150+ currencies)
- **📈 Interest Calculator** - Multiple methods (30/360, act/360, act/365, act/act)
- **🎨 Modern GUI** - Dark theme with tabbed interface
- **🌐 Live API** - Free & paid currency APIs with caching
- **📊 Auto Logging** - All operations saved to CSV files
- **🖥️ Multiple Interfaces** - GUI, CLI, and API access

## 🚀 Quick Start

### Installation from PyPI
```bash
pip install corally
```

### Command Line Usage
```bash
# Main calculator suite
corally

# Individual tools
corally-calc      # Basic calculator
corally-currency  # Currency converter
corally-gui       # Launch GUI interface
```

### Python Package Usage
```python
from corally import CalculatorCore, CurrencyConverter, InterestCalculator

# Basic calculator
calc = CalculatorCore()
result = calc.add(10, 5)  # Returns 15.0

# Currency conversion (static rates)
converter = CurrencyConverter()
usd_amount = converter.eur_to_usd(100)

# Interest calculation
interest_calc = InterestCalculator()
interest = interest_calc.calculate_interest(
    principal=1000,
    rate=5.0,
    days=30,
    method="30/360"
)
```

## 📁 Project Structure

```
Calculator Suite/
├── 📱 Core Applications
│   ├── calculator_core.py      # Unified core library
│   ├── calculator_gui.py       # Modern GUI application
│   ├── gui_launcher.py         # GUI launcher
│   ├── Hauptprogramm.py        # Console menu
│   ├── Rechner.py             # Console calculator
│   ├── Waerungsrechner.py     # Console currency converter
│   ├── api.py                 # Paid API server
│   ├── api_free.py            # Free API server
│   ├── manage_api_server.py   # API management
│   └── requirements.txt       # Dependencies
│
├── 📊 data/                   # Generated data files
│   ├── rechner_log.csv        # Calculator operation logs
│   ├── cache.csv              # API response cache
│   └── api.log                # Server logs
│
├── 📚 docs/                   # Documentation
│   ├── README.md              # Full documentation
│   └── QUICK_START_GUIDE.md   # Quick setup guide
│
├── 🧪 tests/                  # Test files
│   ├── test_api.py
│   ├── test_gui.py
│   └── test_*.py
│
├── 🔧 debug/                  # Debug & development tools
│   ├── debug_*.py
│   └── fix_*.py
│
└── 📁 misc_files/             # Miscellaneous files
    ├── launch_calculator.bat
    ├── RockYourBody.py
    └── *.pptx
```

## ✨ Features

- **🧮 Basic Calculator** - Four operations with automatic logging
- **💱 Currency Converter** - Static + live rates (150+ currencies)
- **📈 Interest Calculator** - Multiple calculation methods
- **🎨 Modern GUI** - Dark theme with tabbed interface
- **🌐 Live API** - Free & paid currency conversion
- **📊 Auto Logging** - All operations saved to CSV

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🔧 Configuration

For live currency conversion, create `.env` file:
```env
API_KEY=your_api_key_here
```

## 📖 Documentation

- **Full Documentation**: `docs/README.md`
- **Quick Start Guide**: `docs/QUICK_START_GUIDE.md`

## 🧪 Testing

Run tests from the tests/ directory:
```bash
python tests/test_gui.py
python tests/test_api.py
```

## 🛠️ Development

Debug tools are available in the debug/ directory for troubleshooting and development.

---

**Version**: 2.0 | **Python**: 3.8+ | **License**: Educational Use
