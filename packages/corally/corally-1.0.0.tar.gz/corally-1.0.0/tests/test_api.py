#!/usr/bin/env python3
"""
API Diagnostic Tool for Calculator Suite
Tests both free and paid API configurations
"""

import os
import requests
import subprocess
import time
import sys

def test_free_api_direct():
    """Test the free API directly without local server"""
    print("🌐 Testing Free API (direct call)...")
    
    try:
        # Test the free exchange rate API directly
        url = "https://api.exchangerate-api.com/v4/latest/EUR"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates", {})
            
            if "USD" in rates:
                eur_to_usd_rate = rates["USD"]
                print(f"✅ Free API working! EUR to USD rate: {eur_to_usd_rate}")
                
                # Test conversion
                amount = 100
                result = amount * eur_to_usd_rate
                print(f"   Example: {amount} EUR = {result:.2f} USD")
                return True
            else:
                print("❌ USD rate not found in response")
                return False
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Free API test failed: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has API key"""
    print("\n🔑 Checking .env file...")
    
    if os.path.exists(".env"):
        print("✅ .env file found")
        
        try:
            with open(".env", "r") as f:
                content = f.read()
                
            if "API_KEY=" in content and not content.strip().endswith("API_KEY="):
                print("✅ API_KEY found in .env file")
                return True
            else:
                print("❌ API_KEY not properly set in .env file")
                print("   Please add: API_KEY=your_actual_api_key")
                return False
                
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            return False
    else:
        print("❌ .env file not found")
        print("   Create .env file with: API_KEY=your_actual_api_key")
        return False

def test_local_server(api_type="free"):
    """Test local API server"""
    print(f"\n🖥️  Testing Local {api_type.title()} API Server...")
    
    # Start the server
    try:
        if api_type == "free":
            api_module = "api_free:app"
        else:
            api_module = "api:app"
            
        print(f"   Starting server: uvicorn {api_module}...")
        
        process = subprocess.Popen(
            ["uvicorn", api_module, "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        print("   Waiting for server to start...")
        time.sleep(3)
        
        # Test the server
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running!")
                
                # Test conversion
                print("   Testing currency conversion...")
                conv_response = requests.get(
                    "http://127.0.0.1:8000/convert",
                    params={"from_currency": "EUR", "to_currency": "USD", "amount": "100"},
                    timeout=10
                )
                
                if conv_response.status_code == 200:
                    data = conv_response.json()
                    print("✅ Conversion successful!")
                    print(f"   {data['amount']} {data['from']} = {data['result']} {data['to']}")
                    print(f"   Rate: {data['info']['rate']}")
                    success = True
                else:
                    print(f"❌ Conversion failed: {conv_response.status_code}")
                    print(f"   Response: {conv_response.text}")
                    success = False
            else:
                print(f"❌ Server responded with status: {response.status_code}")
                success = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to server: {e}")
            success = False
        
        # Stop the server
        print("   Stopping server...")
        process.terminate()
        process.wait()
        
        return success
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("📦 Checking dependencies...")

    # Core packages
    core_packages = ["fastapi", "uvicorn", "httpx", "requests"]
    missing = []

    for package in core_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)

    # Check for dotenv (either python-dotenv or dontenv)
    try:
        import dotenv  # noqa: F401
        print("✅ python-dotenv")
    except ImportError:
        try:
            import dotenv  # noqa: F401
            print("✅ dotenv (alternative to python-dotenv)")
        except ImportError:
            print("❌ dotenv package (python-dotenv or dotenv)")
            missing.append("python-dotenv")

    if missing:
        print("\n💡 To install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False

    print("\n🎉 All dependencies are installed!")
    return True

def main():
    """Run all API tests"""
    print("🧪 API Diagnostic Tool for Calculator Suite")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return False
    
    # Test free API directly
    free_api_works = test_free_api_direct()
    
    # Check .env file
    env_file_ok = check_env_file()
    
    # Test local servers
    print("\n" + "=" * 50)
    print("Testing Local Servers...")
    
    free_server_works = test_local_server("free")
    
    if env_file_ok:
        paid_server_works = test_local_server("paid")
    else:
        print("\n⏭️  Skipping paid API test (no .env file)")
        paid_server_works = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Free API (direct): {'✅' if free_api_works else '❌'}")
    print(f"   Free API (local):  {'✅' if free_server_works else '❌'}")
    print(f"   Paid API (local):  {'✅' if paid_server_works else '❌' if env_file_ok else '⏭️ '}")
    
    if free_server_works:
        print("\n🎉 Recommendation: Use Free API mode in the GUI!")
        print("   1. Launch the GUI: python gui_launcher.py")
        print("   2. Go to 'Live Currency API' tab")
        print("   3. Select 'Free API (No key required)'")
        print("   4. Click 'Start API Server'")
        print("   5. Test currency conversion!")
    elif free_api_works:
        print("\n💡 Free API works directly, but local server has issues.")
        print("   Check if uvicorn is installed: pip install uvicorn")
    else:
        print("\n❌ API issues detected. Check your internet connection.")
    
    return free_server_works or paid_server_works

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
