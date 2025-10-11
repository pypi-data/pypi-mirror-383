import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import requests
from ..core import CalculatorCore, CurrencyConverter, InterestCalculator
# Backward compatibility aliases
Rechner = CalculatorCore
Waerungsrechner = CurrencyConverter
tageszins = InterestCalculator.calculate_interest

class ModernCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator Suite")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Initialize calculator
        self.rechner = Rechner()
        
        # Configure style
        self.setup_styles()
        
        # Create main interface
        self.create_main_interface()
        
        # API server status
        self.api_server_running = False
        self.api_process = None
        self.use_free_api = True  # Default to free API
        self.api_port = 8000  # Default port
        
    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background='#2c3e50', 
                       foreground='#ecf0f1', 
                       font=('Arial', 24, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background='#2c3e50', 
                       foreground='#bdc3c7', 
                       font=('Arial', 12))
        
        style.configure('Modern.TButton',
                       background='#3498db',
                       foreground='white',
                       font=('Arial', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Modern.TButton',
                 background=[('active', '#2980b9')])
        
        style.configure('Success.TButton',
                       background='#27ae60',
                       foreground='white',
                       font=('Arial', 11, 'bold'))
        
        style.map('Success.TButton',
                 background=[('active', '#229954')])
        
        style.configure('Warning.TButton',
                       background='#e74c3c',
                       foreground='white',
                       font=('Arial', 11, 'bold'))
        
        style.map('Warning.TButton',
                 background=[('active', '#c0392b')])

    def create_main_interface(self):
        """Create the main interface with tabs"""
        # Title
        title_label = ttk.Label(self.root, text="Calculator Suite", style='Title.TLabel')
        title_label.pack(pady=20)
        
        subtitle_label = ttk.Label(self.root, text="Modern Calculator with Multiple Functions", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))

        # Create menu bar
        self.create_menu_bar()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)

        # Track which tabs have been created
        self.tabs_created = {
            'basic': False,
            'interest': False,
            'api': False
        }

        # Create placeholder frames for main tabs (excluding currency converter)
        self.tab_frames = {}
        self.create_tab_placeholders()

        # Currency converter window reference
        self.currency_window = None

        # Bind tab selection event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        # Create the first tab (Basic Calculator) immediately
        self.create_basic_calculator_tab()
        
    def create_basic_calculator_tab(self):
        """Create basic calculator tab content"""
        calc_frame = self.tab_frames['basic']
        self.tabs_created['basic'] = True
        
        # Calculator display
        self.calc_display = tk.Text(calc_frame, height=3, width=50, font=('Arial', 14), 
                                   bg='#34495e', fg='#ecf0f1', insertbackground='#ecf0f1')
        self.calc_display.pack(pady=20)
        
        # Input frame
        input_frame = ttk.Frame(calc_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="Number 1:").grid(row=0, column=0, padx=5, pady=5)
        self.num1_entry = ttk.Entry(input_frame, font=('Arial', 12))
        self.num1_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Number 2:").grid(row=1, column=0, padx=5, pady=5)
        self.num2_entry = ttk.Entry(input_frame, font=('Arial', 12))
        self.num2_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Operation buttons
        button_frame = ttk.Frame(calc_frame)
        button_frame.pack(pady=20)
        
        operations = [
            ("Addition (+)", lambda: self.calculate('add')),
            ("Subtraction (-)", lambda: self.calculate('subtract')),
            ("Multiplication (×)", lambda: self.calculate('multiply')),
            ("Division (÷)", lambda: self.calculate('divide'))
        ]
        
        for i, (text, command) in enumerate(operations):
            btn = ttk.Button(button_frame, text=text, command=command, style='Modern.TButton')
            btn.grid(row=i//2, column=i%2, padx=10, pady=5, sticky='ew')
        
        # Clear button
        clear_btn = ttk.Button(calc_frame, text="Clear", command=self.clear_calculator, style='Warning.TButton')
        clear_btn.pack(pady=10)

    def create_currency_converter_window_content(self, parent_window):
        """Create currency converter content in a separate window"""
        # Main frame for the window content
        main_frame = ttk.Frame(parent_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Currency Converter (Static Rates)",
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=20)
        
        ttk.Label(input_frame, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        self.currency_amount = ttk.Entry(input_frame, font=('Arial', 12))
        self.currency_amount.grid(row=0, column=1, padx=5, pady=5)
        
        # Conversion buttons
        conversions = [
            ("EUR → USD", lambda: self.convert_currency('eur_to_usd')),
            ("USD → EUR", lambda: self.convert_currency('usd_to_eur')),
            ("EUR → GBP", lambda: self.convert_currency('eur_to_gbp')),
            ("GBP → EUR", lambda: self.convert_currency('gbp_to_eur')),
            ("EUR → YEN", lambda: self.convert_currency('eur_to_yen')),
            ("YEN → EUR", lambda: self.convert_currency('yen_to_eur'))
        ]
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        for i, (text, command) in enumerate(conversions):
            btn = ttk.Button(button_frame, text=text, command=command, style='Modern.TButton')
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
        
        # Result display
        self.currency_result = tk.Text(main_frame, height=5, width=60, font=('Arial', 12),
                                      bg='#34495e', fg='#ecf0f1', insertbackground='#ecf0f1')
        self.currency_result.pack(pady=20)

    def create_interest_calculator_content(self):
        """Create interest calculator tab content"""
        interest_frame = self.tab_frames['interest']
        
        ttk.Label(interest_frame, text="Interest Calculator", 
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Input frame
        input_frame = ttk.Frame(interest_frame)
        input_frame.pack(pady=20)
        
        # Capital
        ttk.Label(input_frame, text="Capital (€):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.capital_entry = ttk.Entry(input_frame, font=('Arial', 12))
        self.capital_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Interest rate
        ttk.Label(input_frame, text="Interest Rate (%):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.rate_entry = ttk.Entry(input_frame, font=('Arial', 12))
        self.rate_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Start date
        ttk.Label(input_frame, text="Start Date (DD.MM.YYYY):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.start_date_entry = ttk.Entry(input_frame, font=('Arial', 12))
        self.start_date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # End date
        ttk.Label(input_frame, text="End Date (DD.MM.YYYY):").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.end_date_entry = ttk.Entry(input_frame, font=('Arial', 12))
        self.end_date_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Method
        ttk.Label(input_frame, text="Method:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.method_var = tk.StringVar(value="act/365")
        method_combo = ttk.Combobox(input_frame, textvariable=self.method_var, 
                                   values=["30/360", "act/360", "act/365", "act/act"],
                                   font=('Arial', 12))
        method_combo.grid(row=4, column=1, padx=5, pady=5)
        
        # Calculate button
        calc_btn = ttk.Button(interest_frame, text="Calculate Interest", 
                             command=self.calculate_interest, style='Success.TButton')
        calc_btn.pack(pady=20)
        
        # Result display
        self.interest_result = tk.Text(interest_frame, height=8, width=60, font=('Arial', 12),
                                      bg='#34495e', fg='#ecf0f1', insertbackground='#ecf0f1')
        self.interest_result.pack(pady=20)

    def create_api_currency_content(self):
        """Create API currency converter tab content"""
        api_frame = self.tab_frames['api']
        
        ttk.Label(api_frame, text="Live Currency Converter", 
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        # API Selection
        api_selection_frame = ttk.Frame(api_frame)
        api_selection_frame.pack(pady=10)

        ttk.Label(api_selection_frame, text="API Mode:", font=('Arial', 12, 'bold')).pack(side='left', padx=5)

        self.api_mode_var = tk.StringVar(value="free")
        free_radio = ttk.Radiobutton(api_selection_frame, text="Free API (No key required)",
                                    variable=self.api_mode_var, value="free",
                                    command=self.on_api_mode_change)
        free_radio.pack(side='left', padx=5)

        paid_radio = ttk.Radiobutton(api_selection_frame, text="Paid API (Requires .env file)",
                                    variable=self.api_mode_var, value="paid",
                                    command=self.on_api_mode_change)
        paid_radio.pack(side='left', padx=5)

        # Server control
        control_frame = ttk.Frame(api_frame)
        control_frame.pack(pady=10)

        self.server_status_label = ttk.Label(control_frame, text="API Server: Stopped",
                                           font=('Arial', 12, 'bold'))
        self.server_status_label.pack(pady=5)

        self.start_server_btn = ttk.Button(control_frame, text="Start API Server",
                                          command=self.start_api_server, style='Success.TButton')
        self.start_server_btn.pack(side='left', padx=5)

        self.stop_server_btn = ttk.Button(control_frame, text="Stop API Server",
                                         command=self.stop_api_server, style='Warning.TButton')
        self.stop_server_btn.pack(side='left', padx=5)

        # Force stop button (always enabled)
        self.force_stop_btn = ttk.Button(control_frame, text="Force Stop",
                                        command=self.force_stop_server, style='Danger.TButton')
        self.force_stop_btn.pack(side='left', padx=5)
        
        # Conversion interface
        conversion_frame = ttk.Frame(api_frame)
        conversion_frame.pack(pady=20)
        
        ttk.Label(conversion_frame, text="From Currency:").grid(row=0, column=0, padx=5, pady=5)
        self.from_currency = ttk.Entry(conversion_frame, font=('Arial', 12))
        self.from_currency.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(conversion_frame, text="To Currency:").grid(row=1, column=0, padx=5, pady=5)
        self.to_currency = ttk.Entry(conversion_frame, font=('Arial', 12))
        self.to_currency.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(conversion_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5)
        self.api_amount = ttk.Entry(conversion_frame, font=('Arial', 12))
        self.api_amount.grid(row=2, column=1, padx=5, pady=5)
        
        # Conversion and test buttons
        button_frame2 = ttk.Frame(api_frame)
        button_frame2.pack(pady=20)

        convert_btn = ttk.Button(button_frame2, text="Convert Currency",
                                command=self.api_convert_currency, style='Modern.TButton')
        convert_btn.pack(side='left', padx=5)

        test_btn = ttk.Button(button_frame2, text="Test Output",
                             command=self.test_api_output, style='Success.TButton')
        test_btn.pack(side='left', padx=5)

        clear_btn = ttk.Button(button_frame2, text="Clear Results",
                              command=self.clear_api_results, style='Warning.TButton')
        clear_btn.pack(side='left', padx=5)
        
        # Result display section
        result_label = ttk.Label(api_frame, text="Conversion Results:", font=('Arial', 12, 'bold'))
        result_label.pack(pady=(10, 5))

        # Create frame for text widget and scrollbar
        text_frame = ttk.Frame(api_frame)
        text_frame.pack(pady=10, padx=20, fill='both', expand=True)

        # Create text widget
        self.api_result = tk.Text(text_frame, height=10, width=70, font=('Arial', 11),
                                 bg='#34495e', fg='#ecf0f1', insertbackground='#ecf0f1',
                                 wrap=tk.WORD, state=tk.NORMAL, relief='solid', bd=1)
        self.api_result.pack(side='left', fill='both', expand=True)

        # Add scrollbar
        result_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.api_result.yview)
        result_scrollbar.pack(side='right', fill='y')
        self.api_result.config(yscrollcommand=result_scrollbar.set)

        # Add initial text to verify widget is working
        self.api_result.insert(tk.END, "💡 Live Currency Converter Ready\n")
        self.api_result.insert(tk.END, "1. Select API mode above\n")
        self.api_result.insert(tk.END, "2. Start the API server\n")
        self.api_result.insert(tk.END, "3. Enter currencies and amount\n")
        self.api_result.insert(tk.END, "4. Click 'Convert Currency'\n")
        self.api_result.insert(tk.END, f"{'-'*40}\n")

    def create_menu_bar(self):
        """Create menu bar with Tools dropdown for Currency Converter"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Currency Converter (Static)", command=self.open_currency_converter)
        tools_menu.add_separator()
        tools_menu.add_command(label="About", command=self.show_about)

    def open_currency_converter(self):
        """Open Currency Converter in a separate window"""
        if self.currency_window is not None and self.currency_window.winfo_exists():
            # Window already exists, bring it to front
            self.currency_window.lift()
            self.currency_window.focus_force()
            return

        # Create new currency converter window
        self.currency_window = tk.Toplevel(self.root)
        self.currency_window.title("Currency Converter (Static Rates)")
        self.currency_window.geometry("500x400")
        self.currency_window.resizable(True, True)

        # Apply dark theme to the window
        self.currency_window.configure(bg='#2c3e50')

        # Create currency converter content in the new window
        self.create_currency_converter_window_content(self.currency_window)

        # Handle window closing
        self.currency_window.protocol("WM_DELETE_WINDOW", self.close_currency_converter)

    def close_currency_converter(self):
        """Close the currency converter window"""
        if self.currency_window:
            self.currency_window.destroy()
            self.currency_window = None

    def show_about(self):
        """Show about dialog"""
        about_text = """Calculator Suite v2.0

Modern calculator with multiple functions:
• Basic Calculator with logging
• Interest Calculator
• Live Currency API
• Currency Converter (Static Rates)

Developed with Python & tkinter"""

        from tkinter import messagebox
        messagebox.showinfo("About Calculator Suite", about_text)

    def create_tab_placeholders(self):
        """Create placeholder frames for main tabs (excluding currency converter)"""
        # Basic Calculator tab
        self.tab_frames['basic'] = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_frames['basic'], text="Basic Calculator")

        # Interest Calculator tab
        self.tab_frames['interest'] = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_frames['interest'], text="Interest Calculator")

        # Live Currency API tab
        self.tab_frames['api'] = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_frames['api'], text="Live Currency API")

        # Add loading labels to empty tabs
        for tab_name, frame in self.tab_frames.items():
            if tab_name != 'basic':  # Don't add to basic tab since it loads immediately
                loading_label = ttk.Label(frame, text=f"Loading {tab_name.title()} Calculator...",
                                        font=('Arial', 14), foreground='gray')
                loading_label.pack(expand=True)

    def on_tab_changed(self, event=None):  # noqa: ARG002
        """Handle tab selection changes - create tab content on first access"""
        selected_tab = self.notebook.index(self.notebook.select())

        # Map tab indices to tab names (currency converter removed)
        tab_mapping = {0: 'basic', 1: 'interest', 2: 'api'}
        tab_name = tab_mapping.get(selected_tab)

        if tab_name and not self.tabs_created[tab_name]:
            # Clear the loading label
            for widget in self.tab_frames[tab_name].winfo_children():
                widget.destroy()

            # Create the actual tab content
            if tab_name == 'interest':
                self.create_interest_calculator_content()
            elif tab_name == 'api':
                self.create_api_currency_content()

            # Mark as created
            self.tabs_created[tab_name] = True

    def calculate(self, operation):
        """Perform basic calculator operations"""
        try:
            num1 = float(self.num1_entry.get())
            num2 = float(self.num2_entry.get())

            if operation == 'add':
                result = self.rechner.add(num1, num2)
                op_symbol = '+'
            elif operation == 'subtract':
                result = self.rechner.subtract(num1, num2)
                op_symbol = '-'
            elif operation == 'multiply':
                result = self.rechner.multiply(num1, num2)
                op_symbol = '×'
            elif operation == 'divide':
                result = self.rechner.divide(num1, num2)
                op_symbol = '÷'

            if result is not None:
                calculation_text = f"{num1} {op_symbol} {num2} = {result}\n"
                self.calc_display.insert(tk.END, calculation_text)
                self.calc_display.see(tk.END)
            else:
                messagebox.showerror("Error", "Calculation failed. Check your inputs.")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")

    def clear_calculator(self):
        """Clear calculator display and inputs"""
        self.calc_display.delete(1.0, tk.END)
        self.num1_entry.delete(0, tk.END)
        self.num2_entry.delete(0, tk.END)

    def convert_currency(self, conversion_type):
        """Convert currency using static rates"""
        try:
            amount = float(self.currency_amount.get())

            if conversion_type == 'eur_to_usd':
                result = Waerungsrechner.eur_to_usd(amount)
                text = f"{amount} EUR = {result} USD\n"
            elif conversion_type == 'usd_to_eur':
                result = Waerungsrechner.usd_to_eur(amount)
                text = f"{amount} USD = {result} EUR\n"
            elif conversion_type == 'eur_to_gbp':
                result = Waerungsrechner.eur_to_gbp(amount)
                text = f"{amount} EUR = {result} GBP\n"
            elif conversion_type == 'gbp_to_eur':
                result = Waerungsrechner.gbp_to_eur(amount)
                text = f"{amount} GBP = {result} EUR\n"
            elif conversion_type == 'eur_to_yen':
                result = Waerungsrechner.eur_to_jpy(amount)
                text = f"{amount} EUR = {result} JPY\n"
            elif conversion_type == 'yen_to_eur':
                result = Waerungsrechner.jpy_to_eur(amount)
                text = f"{amount} JPY = {result} EUR\n"

            if result is not None:
                self.currency_result.insert(tk.END, text)
                self.currency_result.see(tk.END)
            else:
                messagebox.showerror("Error", "Conversion failed.")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")

    def calculate_interest(self):
        """Calculate interest using the zinsen module"""
        try:
            capital = float(self.capital_entry.get())
            rate = float(self.rate_entry.get())
            start_date = self.start_date_entry.get()
            end_date = self.end_date_entry.get()
            method = self.method_var.get()

            interest = tageszins(capital, rate, start_date, end_date, method)

            result_text = f"""
📊 Interest Calculation Result:
Capital: {capital:,.2f} €
Interest Rate: {rate}% per year
Period: {start_date} to {end_date}
Method: {method}
Interest: {interest:,.2f} €
Total: {capital + interest:,.2f} €
{'-'*40}
"""

            self.interest_result.insert(tk.END, result_text)
            self.interest_result.see(tk.END)

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")

    def on_api_mode_change(self):
        """Handle API mode change"""
        if self.api_server_running:
            messagebox.showinfo("Info", "Please stop the current server before changing API mode.")
            return

        mode = self.api_mode_var.get()
        if mode == "free":
            self.use_free_api = True
        else:
            self.use_free_api = False

    def find_available_port(self, start_port=8000):
        """Find an available port starting from start_port"""
        import socket
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        return None

    def start_api_server(self):
        """Start the FastAPI server in a separate thread"""
        if not self.api_server_running:
            def run_server():
                try:
                    # Find available port
                    port = self.find_available_port(8000)
                    if not port:
                        self.root.after(0, lambda: messagebox.showerror("Error", "No available ports found (8000-8009)"))
                        return

                    self.api_port = port

                    # Choose which API to start based on mode
                    if self.use_free_api:
                        api_module = "api_free:app"
                    else:
                        api_module = "api:app"

                    self.api_process = subprocess.Popen(
                        ["uvicorn", api_module, "--host", "127.0.0.1", "--port", str(port)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    # Wait a moment and check if server started
                    import time
                    time.sleep(2)

                    # Test if server is responding
                    try:
                        import requests
                        response = requests.get(f"http://127.0.0.1:{port}/", timeout=5)
                        if response.status_code == 200:
                            self.api_server_running = True
                            mode_text = "Free API" if self.use_free_api else "Paid API"
                            self.root.after(0, lambda: self.update_server_status(f"Running ({mode_text}) on port {port}"))
                        else:
                            raise Exception(f"Server not responding (status: {response.status_code})")
                    except Exception as e:
                        self.api_process.terminate()
                        self.root.after(0, lambda err=str(e): messagebox.showerror("Error", f"Server failed to start properly: {err}"))

                except Exception as error:
                    self.root.after(0, lambda err=error: messagebox.showerror("Error", f"Failed to start server: {str(err)}"))

            threading.Thread(target=run_server, daemon=True).start()

    def stop_api_server(self):
        """Stop the FastAPI server"""
        try:
            # Show progress
            self.api_result.insert(tk.END, "🛑 Stopping API server...\n")
            self.api_result.see(tk.END)
            self.root.update()

            stopped = False

            # Method 1: Try to stop the process we started
            if self.api_process is not None:
                try:
                    self.api_process.terminate()
                    self.api_process.wait(timeout=5)  # Wait up to 5 seconds
                    self.api_process = None
                    stopped = True
                    self.api_result.insert(tk.END, "✅ Stopped tracked process\n")
                except Exception as e:
                    self.api_result.insert(tk.END, f"⚠️  Could not stop tracked process: {e}\n")

            # Method 2: Kill any process on the current port (more robust)
            if not stopped:
                try:
                    import subprocess
                    # Find process on current port
                    result = subprocess.run(
                        ["netstat", "-ano"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    for line in result.stdout.split('\n'):
                        if f':{self.api_port}' in line and ('LISTENING' in line or 'ABHÖREN' in line):
                            # Extract PID (last column)
                            parts = line.split()
                            if parts:
                                pid = parts[-1]
                                if pid.isdigit():
                                    try:
                                        subprocess.run(["taskkill", "/PID", pid, "/F"],
                                                     capture_output=True, timeout=5)
                                        stopped = True
                                        self.api_result.insert(tk.END, f"✅ Killed process {pid} on port {self.api_port}\n")
                                        break
                                    except Exception:
                                        pass
                except Exception as e:
                    self.api_result.insert(tk.END, f"⚠️  Port check failed: {e}\n")

            # Update GUI state
            self.api_server_running = False
            self.api_process = None

            if stopped:
                self.update_server_status("Stopped")
                self.api_result.insert(tk.END, "✅ API Server stopped successfully!\n")
                self.api_result.insert(tk.END, f"{'-'*40}\n")
                messagebox.showinfo("Success", "API Server stopped successfully!")
            else:
                self.update_server_status("Unknown")
                self.api_result.insert(tk.END, "⚠️  Could not confirm server was stopped\n")
                self.api_result.insert(tk.END, "💡 Try 'Force Stop' if server is still running\n")
                self.api_result.insert(tk.END, f"{'-'*40}\n")
                messagebox.showwarning("Warning", "Could not confirm server was stopped. Try 'Force Stop' if needed.")

            self.api_result.see(tk.END)

        except Exception as e:
            self.api_result.insert(tk.END, f"❌ Stop failed: {str(e)}\n")
            self.api_result.see(tk.END)
            messagebox.showerror("Error", f"Failed to stop server: {str(e)}")

    def force_stop_server(self):
        """Force stop any API server on common ports"""
        try:
            import subprocess
            ports_to_check = [8000, 8001, 8002, 8003]
            stopped_any = False

            for port in ports_to_check:
                try:
                    # Find processes on this port
                    result = subprocess.run(
                        ["netstat", "-ano"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    for line in result.stdout.split('\n'):
                        if f':{port}' in line and ('LISTENING' in line or 'ABHÖREN' in line):
                            parts = line.split()
                            if parts:
                                pid = parts[-1]
                                if pid.isdigit():
                                    try:
                                        subprocess.run(["taskkill", "/PID", pid, "/F"],
                                                     capture_output=True, timeout=5)
                                        stopped_any = True
                                        print(f"Killed process {pid} on port {port}")
                                    except Exception:
                                        pass
                except Exception:
                    pass

            # Reset GUI state
            self.api_server_running = False
            self.api_process = None

            if stopped_any:
                self.update_server_status("Force Stopped")
                messagebox.showinfo("Success", "Force stopped API servers on ports 8000-8003")
            else:
                self.update_server_status("No servers found")
                messagebox.showinfo("Info", "No API servers found running on ports 8000-8003")

        except Exception as e:
            messagebox.showerror("Error", f"Force stop failed: {str(e)}")

    def update_server_status(self, status):
        """Update server status label"""
        self.server_status_label.config(text=f"API Server: {status}")
        if "Running" in status:
            self.start_server_btn.config(state='disabled')
            self.stop_server_btn.config(state='normal')
        else:
            self.start_server_btn.config(state='normal')
            # Keep stop button enabled - user might need to force stop
            self.stop_server_btn.config(state='normal')

    def api_convert_currency(self):
        """Convert currency using the live API"""
        # First check if server is actually reachable
        if not self.check_api_server_health():
            return

        try:
            from_curr = self.from_currency.get().strip().upper()
            to_curr = self.to_currency.get().strip().upper()
            amount = self.api_amount.get().strip()

            if not all([from_curr, to_curr, amount]):
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            # Validate inputs
            try:
                float(amount.replace(",", "."))
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount.")
                return

            if len(from_curr) != 3 or len(to_curr) != 3:
                messagebox.showerror("Error", "Please use 3-letter currency codes (e.g., EUR, USD).")
                return

            # Show progress
            self.api_result.insert(tk.END, f"🔄 Converting {amount} {from_curr} to {to_curr}...\n")
            self.api_result.see(tk.END)
            self.root.update()

            # Make API request
            url = f"http://127.0.0.1:{self.api_port}/convert"
            params = {
                "from_currency": from_curr,
                "to_currency": to_curr,
                "amount": amount
            }

            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                cached_status = "Cached" if data.get("cached", False) else "Live"

                result_text = f"""✅ {cached_status} Currency Conversion:
{data['amount']} {data['from']} = {data['result']:.2f} {data['to']}
Exchange Rate: {data['info']['rate']:.4f}
{'-'*40}
"""
                self.api_result.insert(tk.END, result_text)
                self.api_result.see(tk.END)
            else:
                error_msg = f"❌ API Error {response.status_code}: {response.text}\n{'-'*40}\n"
                self.api_result.insert(tk.END, error_msg)
                self.api_result.see(tk.END)

        except requests.exceptions.ConnectionError:
            self.api_result.insert(tk.END, "❌ Connection Error: API server not reachable\n")
            self.api_result.insert(tk.END, "💡 Try restarting the API server\n{'-'*40}\n")
            self.api_result.see(tk.END)
            self.api_server_running = False
            self.update_server_status("Stopped")
        except requests.exceptions.Timeout:
            self.api_result.insert(tk.END, "❌ Timeout Error: API server too slow\n{'-'*40}\n")
            self.api_result.see(tk.END)
        except requests.exceptions.RequestException as e:
            self.api_result.insert(tk.END, f"❌ Network Error: {str(e)}\n{'-'*40}\n")
            self.api_result.see(tk.END)
        except Exception as e:
            self.api_result.insert(tk.END, f"❌ Unexpected Error: {str(e)}\n{'-'*40}\n")
            self.api_result.see(tk.END)

    def check_api_server_health(self):
        """Check if API server is actually running and reachable"""
        try:
            response = requests.get(f"http://127.0.0.1:{self.api_port}/", timeout=5)
            if response.status_code == 200:
                return True
            else:
                self.api_result.insert(tk.END, f"❌ Server health check failed: {response.status_code}\n")
                self.api_result.see(tk.END)
                return False
        except requests.exceptions.ConnectionError:
            self.api_result.insert(tk.END, "❌ API server not running. Please start it first.\n")
            self.api_result.see(tk.END)
            self.api_server_running = False
            self.update_server_status("Stopped")
            return False
        except Exception as e:
            self.api_result.insert(tk.END, f"❌ Server check failed: {str(e)}\n")
            self.api_result.see(tk.END)
            return False

    def test_api_output(self):
        """Test the API output text widget"""
        try:
            self.api_result.insert(tk.END, "\n🧪 Testing output widget...\n")
            self.api_result.insert(tk.END, "✅ Text widget is working!\n")

            # Test formatted output like real API response
            test_result = f"""✅ Test Currency Conversion:
100.0 EUR = 116.00 USD
Exchange Rate: 1.1600
{'-'*40}
"""
            self.api_result.insert(tk.END, test_result)
            self.api_result.see(tk.END)

            messagebox.showinfo("Success", "Output widget is working correctly!")

        except Exception as e:
            messagebox.showerror("Error", f"Output widget test failed: {str(e)}")

    def clear_api_results(self):
        """Clear the API results text widget"""
        try:
            self.api_result.delete(1.0, tk.END)
            self.api_result.insert(tk.END, "💡 Results cleared. Ready for new conversions.\n")
            self.api_result.insert(tk.END, f"{'-'*40}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear results: {str(e)}")


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = ModernCalculatorGUI(root)

    # Handle window closing
    def on_closing():
        if hasattr(app, 'api_server_running') and app.api_server_running:
            app.stop_api_server()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
