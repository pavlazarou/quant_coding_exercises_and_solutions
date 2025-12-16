"""
REST API Exercise 3: Account Information and Portfolio Display
"""

import requests
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv
import os

# API Configuration
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets/v2"


def fetch_account_info():
    """Fetch account information from Alpaca API."""
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }
    
    url = f"{BASE_URL}/account"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching account: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def fetch_positions():
    """Fetch current portfolio positions from Alpaca API."""
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }
    
    url = f"{BASE_URL}/positions"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching positions: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def update_account_display():
    """Fetch account data and update the display labels."""
    account_data = fetch_account_info()
    
    if account_data:
        cash = float(account_data['cash'])
        portfolio_value = float(account_data['portfolio_value'])
        buying_power = float(account_data['buying_power'])
        equity = float(account_data['equity'])
        
        cash_label.config(text=f"Cash: ${cash:,.2f}")
        portfolio_value_label.config(text=f"Portfolio Value: ${portfolio_value:,.2f}")
        buying_power_label.config(text=f"Buying Power: ${buying_power:,.2f}")
        equity_label.config(text=f"Equity: ${equity:,.2f}")
    else:
        cash_label.config(text="Cash: Error")
        portfolio_value_label.config(text="Portfolio Value: Error")
        buying_power_label.config(text="Buying Power: Error")
        equity_label.config(text="Equity: Error")


def update_positions_display():
    """Fetch positions data and update the table display."""
    # Clear existing items
    for item in positions_tree.get_children():
        positions_tree.delete(item)
    
    positions_data = fetch_positions()
    
    if positions_data:
        if len(positions_data) == 0:
            positions_tree.insert('', 'end', values=("No positions", "", "", "", "", ""))
        else:
            for position in positions_data:
                symbol = position['symbol']
                qty = position['qty']
                current_price = float(position['current_price'])
                market_value = float(position['market_value'])
                unrealized_pl = float(position['unrealized_pl'])
                unrealized_plpc = float(position['unrealized_plpc']) * 100  # Convert to percentage
                
                # Color code P&L
                pl_color = "green" if unrealized_pl >= 0 else "red"
                
                positions_tree.insert('', 'end', values=(
                    symbol,
                    qty,
                    f"${current_price:.2f}",
                    f"${market_value:.2f}",
                    f"${unrealized_pl:.2f}",
                    f"{unrealized_plpc:.2f}%"
                ), tags=(pl_color,))
        
        # Configure tag colors
        positions_tree.tag_configure('green', foreground='green')
        positions_tree.tag_configure('red', foreground='red')
    else:
        positions_tree.insert('', 'end', values=("Error fetching data", "", "", "", "", ""))


def refresh_all():
    """Refresh both account info and positions display."""
    update_account_display()
    update_positions_display()


# Create main window
root = tk.Tk()
root.title("Account & Portfolio - Solution")
root.geometry("900x600")

# Create title label
title_label = tk.Label(root, text="Account Information & Portfolio", 
                       font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Create account info frame
account_frame = tk.LabelFrame(root, text="Account Summary", font=("Arial", 12, "bold"))
account_frame.pack(pady=10, padx=20, fill='x')

# Account info labels
cash_label = tk.Label(account_frame, text="Cash: $0.00", font=("Arial", 11))
cash_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')

portfolio_value_label = tk.Label(account_frame, text="Portfolio Value: $0.00", font=("Arial", 11))
portfolio_value_label.grid(row=0, column=1, padx=20, pady=10, sticky='w')

buying_power_label = tk.Label(account_frame, text="Buying Power: $0.00", font=("Arial", 11))
buying_power_label.grid(row=1, column=0, padx=20, pady=10, sticky='w')

equity_label = tk.Label(account_frame, text="Equity: $0.00", font=("Arial", 11))
equity_label.grid(row=1, column=1, padx=20, pady=10, sticky='w')

# Create positions frame
positions_frame = tk.LabelFrame(root, text="Current Positions", font=("Arial", 12, "bold"))
positions_frame.pack(pady=10, padx=20, fill='both', expand=True)

# Create Treeview widget for positions
columns = ("Symbol", "Quantity", "Price", "Market Value", "P&L", "P&L %")
positions_tree = ttk.Treeview(positions_frame, columns=columns, show='headings', height=12)

# Define headings
for col in columns:
    positions_tree.heading(col, text=col)

# Define column widths
positions_tree.column("Symbol", width=100, anchor='center')
positions_tree.column("Quantity", width=100, anchor='center')
positions_tree.column("Price", width=120, anchor='center')
positions_tree.column("Market Value", width=150, anchor='center')
positions_tree.column("P&L", width=120, anchor='center')
positions_tree.column("P&L %", width=100, anchor='center')

# Add scrollbar
scrollbar = ttk.Scrollbar(positions_frame, orient='vertical', command=positions_tree.yview)
positions_tree.configure(yscrollcommand=scrollbar.set)

# Pack widgets
positions_tree.pack(side='left', fill='both', expand=True)
scrollbar.pack(side='right', fill='y')

# Create refresh button
refresh_button = tk.Button(root, text="Refresh Data", command=refresh_all,
                          font=("Arial", 12), bg="#2196F3", fg="white")
refresh_button.pack(pady=10)

# Load initial data
refresh_all()

# Start the GUI event loop
root.mainloop()

