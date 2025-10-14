#!/usr/bin/env python3
"""
Simple GUI test to verify the API connection works
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests

def test_api_connection():
    """Test API and show result in GUI"""
    try:
        # Clear previous results
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "🔄 Testing API connection...\n")
        root.update()
        
        # Test API
        url = "http://127.0.0.1:8000/convert"
        params = {
            "from_currency": "EUR",
            "to_currency": "USD",
            "amount": "100"
        }
        
        result_text.insert(tk.END, f"📡 Making request to: {url}\n")
        result_text.insert(tk.END, f"📋 Parameters: {params}\n")
        root.update()
        
        response = requests.get(url, params=params, timeout=10)
        
        result_text.insert(tk.END, f"📊 Response status: {response.status_code}\n")
        root.update()
        
        if response.status_code == 200:
            data = response.json()
            
            # Show raw response
            result_text.insert(tk.END, f"✅ Raw response: {data}\n\n")
            
            # Format like the main GUI
            cached_status = "Cached" if data.get("cached", False) else "Live"
            formatted_result = f"""🌐 {cached_status} Currency Conversion:
{data['amount']} {data['from']} = {data['result']:.2f} {data['to']}
Exchange Rate: {data['info']['rate']:.4f}
{'-'*40}
"""
            result_text.insert(tk.END, formatted_result)
            result_text.see(tk.END)
            
            messagebox.showinfo("Success", "API connection working perfectly!")
        else:
            error_msg = f"❌ API Error: {response.status_code}\n{response.text}"
            result_text.insert(tk.END, error_msg)
            messagebox.showerror("Error", f"API returned status {response.status_code}")
            
    except Exception as e:
        error_msg = f"❌ Connection failed: {str(e)}"
        result_text.insert(tk.END, error_msg)
        messagebox.showerror("Error", f"Connection failed: {str(e)}")

def test_different_currencies():
    """Test different currency pairs"""
    currencies = [
        ("EUR", "USD", "100"),
        ("USD", "EUR", "100"), 
        ("EUR", "GBP", "50"),
        ("GBP", "JPY", "25")
    ]
    
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "🧪 Testing multiple currency pairs...\n\n")
    
    for from_curr, to_curr, amount in currencies:
        try:
            url = "http://127.0.0.1:8000/convert"
            params = {
                "from_currency": from_curr,
                "to_currency": to_curr,
                "amount": amount
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                cached_status = "Cached" if data.get("cached", False) else "Live"
                
                result = f"✅ {cached_status}: {data['amount']} {data['from']} = {data['result']:.2f} {data['to']} (Rate: {data['info']['rate']:.4f})\n"
                result_text.insert(tk.END, result)
            else:
                result_text.insert(tk.END, f"❌ {from_curr}->{to_curr}: Error {response.status_code}\n")
                
            root.update()
            
        except Exception as e:
            result_text.insert(tk.END, f"❌ {from_curr}->{to_curr}: {str(e)}\n")
    
    result_text.see(tk.END)

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status_label.config(text="✅ Server Status: Running", foreground="green")
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"✅ Server is running!\n")
            result_text.insert(tk.END, f"📄 Server response: {data}\n")
        else:
            status_label.config(text="❌ Server Status: Error", foreground="red")
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"❌ Server error: {response.status_code}\n")
    except Exception as e:
        status_label.config(text="❌ Server Status: Not Running", foreground="red")
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"❌ Server not reachable: {str(e)}\n")

# Create GUI
root = tk.Tk()
root.title("API Connection Test")
root.geometry("800x600")

# Status label
status_label = ttk.Label(root, text="🔄 Checking server...", font=('Arial', 12, 'bold'))
status_label.pack(pady=10)

# Buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

ttk.Button(button_frame, text="Check Server Status", command=check_server_status).pack(side='left', padx=5)
ttk.Button(button_frame, text="Test API Connection", command=test_api_connection).pack(side='left', padx=5)
ttk.Button(button_frame, text="Test Multiple Currencies", command=test_different_currencies).pack(side='left', padx=5)

# Result display
result_text = tk.Text(root, height=25, width=90, font=('Consolas', 10))
result_text.pack(pady=20, padx=20, fill='both', expand=True)

# Scrollbar
scrollbar = ttk.Scrollbar(root, orient='vertical', command=result_text.yview)
scrollbar.pack(side='right', fill='y')
result_text.config(yscrollcommand=scrollbar.set)

# Initial status check
root.after(100, check_server_status)

if __name__ == "__main__":
    print("🧪 Starting API Connection Test GUI...")
    print("💡 Make sure the API server is running on port 8000")
    root.mainloop()
