#!/usr/bin/env python3
"""
Test GUI-API connection to debug why results don't show in GUI
"""

import requests
import json

def test_api_directly():
    """Test the API directly to see the exact response"""
    print("🧪 Testing API directly...")
    
    # Test the same conversion from the logs
    url = "http://127.0.0.1:8000/convert"
    params = {
        "from_currency": "EUR",
        "to_currency": "RUB", 
        "amount": "100"
    }
    
    try:
        print(f"📡 Making request to: {url}")
        print(f"📋 Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response Data:")
            print(json.dumps(data, indent=2))
            
            # Test the exact same formatting as GUI
            cached_status = "Cached" if data.get("cached", False) else "Live"
            result_text = f"""
🌐 {cached_status} Currency Conversion:
{data['amount']} {data['from']} = {data['result']:.2f} {data['to']}
Exchange Rate: {data['info']['rate']:.4f}
{'-'*40}
"""
            print(f"📝 Formatted result (as GUI should show):")
            print(result_text)
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_different_ports():
    """Test if API is running on a different port"""
    print("\n🔍 Checking different ports...")
    
    for port in [8000, 8001, 8002, 8003]:
        try:
            url = f"http://127.0.0.1:{port}/"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✅ API found on port {port}")
                
                # Test conversion on this port
                conv_url = f"http://127.0.0.1:{port}/convert"
                conv_response = requests.get(conv_url, 
                    params={"from_currency": "EUR", "to_currency": "USD", "amount": "100"},
                    timeout=5)
                
                if conv_response.status_code == 200:
                    data = conv_response.json()
                    print(f"   💱 Conversion works: {data['amount']} {data['from']} = {data['result']} {data['to']}")
                else:
                    print(f"   ❌ Conversion failed on port {port}")
            else:
                print(f"❌ Port {port}: Status {response.status_code}")
        except:
            print(f"❌ Port {port}: No response")

def simulate_gui_request():
    """Simulate exactly what the GUI does"""
    print("\n🎭 Simulating GUI request...")
    
    # Simulate GUI inputs
    from_curr = "EUR"
    to_curr = "RUB" 
    amount = "100"
    api_port = 8000  # Default GUI port
    
    try:
        # Exact same code as GUI
        url = f"http://127.0.0.1:{api_port}/convert"
        params = {
            "from_currency": from_curr,
            "to_currency": to_curr,
            "amount": amount
        }
        
        print(f"📡 GUI would make request to: {url}")
        print(f"📋 With params: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GUI would receive:")
            print(json.dumps(data, indent=2))
            
            # Exact GUI formatting
            cached_status = "Cached" if data.get("cached", False) else "Live"
            result_text = f"""
🌐 {cached_status} Currency Conversion:
{data['amount']} {data['from']} = {data['result']:.2f} {data['to']}
Exchange Rate: {data['info']['rate']:.4f}
{'-'*40}
"""
            print(f"📝 GUI would display:")
            print(repr(result_text))  # Show exact string with escape chars
            print(f"📺 GUI would show:")
            print(result_text)
            
            return True
        else:
            print(f"❌ GUI would get error: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ GUI would get exception: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 GUI-API Connection Diagnostic")
    print("=" * 50)
    
    # Test 1: Direct API test
    api_works = test_api_directly()
    
    # Test 2: Check different ports
    test_different_ports()
    
    # Test 3: Simulate GUI
    gui_simulation_works = simulate_gui_request()
    
    print("\n" + "=" * 50)
    print("📊 Diagnostic Results:")
    print(f"   API Direct Test: {'✅' if api_works else '❌'}")
    print(f"   GUI Simulation:  {'✅' if gui_simulation_works else '❌'}")
    
    if api_works and gui_simulation_works:
        print("\n🎉 API is working perfectly!")
        print("💡 The issue might be:")
        print("   1. GUI is using wrong port")
        print("   2. GUI text widget is not updating")
        print("   3. GUI is catching an exception silently")
        print("   4. GUI server status is wrong")
        
        print("\n🔧 Try this in your GUI:")
        print("   1. Check the server status shows 'Running'")
        print("   2. Make sure you're in the 'Live Currency API' tab")
        print("   3. Try EUR -> USD instead of EUR -> RUB")
        print("   4. Check if any error dialogs appear")
    else:
        print("\n❌ API connection issues detected")
        print("💡 Check:")
        print("   1. Is the API server actually running?")
        print("   2. Is it on the right port?")
        print("   3. Are there firewall issues?")

if __name__ == "__main__":
    main()
