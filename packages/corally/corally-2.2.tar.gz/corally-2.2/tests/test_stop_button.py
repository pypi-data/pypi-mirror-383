#!/usr/bin/env python3
"""
Test script to verify stop button functionality
"""

import subprocess
import time
import requests

def start_test_server():
    """Start a test API server"""
    print("🚀 Starting test API server...")
    try:
        process = subprocess.Popen(
            ["uvicorn", "api_free:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)
        
        # Test if server is running
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Test server started successfully on port 8000")
            return process
        else:
            print("❌ Test server failed to start")
            process.terminate()
            return None
    except Exception as e:
        print(f"❌ Failed to start test server: {e}")
        return None

def check_server_running():
    """Check if server is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        return False

def test_stop_methods():
    """Test different stop methods"""
    print("\n🧪 Testing stop methods...")
    
    # Method 1: netstat + taskkill
    print("\n1️⃣  Testing netstat + taskkill method:")
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        found_process = False
        for line in result.stdout.split('\n'):
            if ':8000' in line and ('LISTENING' in line or 'ABHÖREN' in line):
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    if pid.isdigit():
                        print(f"   📋 Found process {pid} on port 8000")
                        found_process = True
                        
                        # Try to kill it
                        try:
                            subprocess.run(["taskkill", "/PID", pid, "/F"],
                                         capture_output=True, timeout=5)
                            print(f"   ✅ Successfully killed process {pid}")
                            return True
                        except Exception as e:
                            print(f"   ❌ Failed to kill process {pid}: {e}")
                            return False
        
        if not found_process:
            print("   ℹ️  No process found on port 8000")
            return False
            
    except Exception as e:
        print(f"   ❌ netstat method failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Stop Button Test Tool")
    print("=" * 30)
    
    # Check initial state
    print("\n📊 Initial state:")
    check_server_running()
    
    # Start test server
    process = start_test_server()
    if not process:
        print("❌ Cannot test without a running server")
        return
    
    print("\n📊 After starting server:")
    check_server_running()
    
    # Test stop methods
    success = test_stop_methods()
    
    print("\n📊 After stop attempt:")
    still_running = check_server_running()
    
    # Cleanup
    if process and process.poll() is None:
        print("\n🧹 Cleaning up...")
        try:
            process.terminate()
            process.wait(timeout=5)
            print("✅ Cleanup successful")
        except Exception as e:
            print(f"⚠️  Cleanup may have failed: {e}")

    print("\n" + "=" * 30)
    print("📊 Test Results:")
    print(f"   Stop method worked: {'✅' if success else '❌'}")
    print(f"   Server still running: {'❌' if still_running else '✅'}")
    
    if success and not still_running:
        print("\n🎉 Stop functionality is working correctly!")
        print("💡 Your GUI stop button should work now")
    else:
        print("\n⚠️  Stop functionality needs attention")
        print("💡 Try the 'Force Stop' button in the GUI")

if __name__ == "__main__":
    main()
