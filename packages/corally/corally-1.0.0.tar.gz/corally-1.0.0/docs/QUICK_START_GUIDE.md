# 🚀 Quick Start Guide - Live Currency API

## Option 1: Free API (Recommended) ⭐

**No API key required - works immediately!**

### Steps:
1. **Launch the GUI:**
   ```bash
   python gui_launcher.py
   ```

2. **Go to the "Live Currency API" tab**

3. **Select "Free API (No key required)" radio button**

4. **Click "Start API Server"**
   - Wait for status to show "Running (Free API)"

5. **Test the conversion:**
   - From Currency: `EUR`
   - To Currency: `USD`
   - Amount: `100`
   - Click "Convert Currency"

### If the Free API doesn't start:
Try starting it manually first:
```bash
uvicorn api_free:app --host 127.0.0.1 --port 8000
```

Then in another terminal, test it:
```bash
curl "http://127.0.0.1:8000/convert?from_currency=EUR&to_currency=USD&amount=100"
```

## Option 2: Paid API (Requires API Key)

### Steps:
1. **Get a free API key from:**
   - https://exchangerate.host/ (Free, no registration)
   - https://fixer.io/ (Free tier available)
   - https://exchangeratesapi.io/ (Free tier available)

2. **Create a `.env` file in your Calculator folder:**
   ```
   API_KEY=your_actual_api_key_here
   ```

3. **In the GUI:**
   - Select "Paid API (Requires .env file)"
   - Click "Start API Server"

## Troubleshooting 🔧

### Problem: "Failed to start server"
**Solution:** Check if port 8000 is already in use
```bash
netstat -an | findstr :8000
```

If something is using port 8000, either:
- Stop that service, or
- Modify the port in the GUI code

### Problem: "Network error" or "API request failed"
**Solutions:**
1. **Check internet connection**
2. **Try the Free API mode first**
3. **Check Windows Firewall** - make sure Python is allowed

### Problem: "Missing dependencies"
**Solution:** Install required packages
```bash
pip install fastapi uvicorn httpx requests dotenv
```

## Testing the API Manually 🧪

### Test Free API directly:
```bash
python -c "
import requests
response = requests.get('https://api.exchangerate-api.com/v4/latest/EUR')
print(response.json()['rates']['USD'])
"
```

### Test Local Server:
1. Start server: `uvicorn api_free:app --port 8000`
2. Open browser: `http://127.0.0.1:8000`
3. Test conversion: `http://127.0.0.1:8000/convert?from_currency=EUR&to_currency=USD&amount=100`

## Success Indicators ✅

When working correctly, you should see:
- ✅ Server status: "Running (Free API)" or "Running (Paid API)"
- ✅ Conversion results showing in the text area
- ✅ Exchange rates and amounts displayed
- ✅ "Cached" or "Live" status for each conversion

## Example Working Output:
```
🌐 Live Currency Conversion:
100.0 EUR = 108.50 USD
Exchange Rate: 1.0850
----------------------------------------
```

## Still Having Issues? 🆘

1. **Check the terminal/console** where you started the GUI for error messages
2. **Try the basic calculator and currency converter tabs first** - they should work perfectly
3. **The static currency converter** (tab 2) works without any API and gives you currency conversion
4. **Contact me** if you need help - I can help debug specific error messages

## Pro Tips 💡

1. **Start with Free API** - it's more reliable and doesn't need setup
2. **The GUI saves your calculations** - check the CSV files for history
3. **You can use both APIs** - switch between them as needed
4. **Cache system** - repeated conversions are faster (cached for 1 hour)

Your Calculator Suite is fully functional - the Live API is just an extra feature! 🎯
