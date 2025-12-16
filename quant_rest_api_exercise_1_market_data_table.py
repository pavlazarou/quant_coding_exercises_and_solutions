"""
REST API Exercise 1 - SOLUTION: Market Data Table Display
"""

import requests
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv
import os

# API Configuration
load_dotenv()
ALPACA_API_KEY = os.getenv("API_KEY")
ALPACA_API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://data.alpaca.markets/v2"

# List of symbols to track
SYMBOLS = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"]


def fetch_market_data(symbol):
    """Fetch the latest market data for a given symbol from Alpaca API."""
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_API_SECRET
    }
    
    url = f"{BASE_URL}/stocks/{symbol}/bars/latest"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching {symbol}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching {symbol}: {e}")
        return None


def update_table():
    """Fetch data for all symbols and update the table display."""
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
    
    # Fetch and display data for each symbol
    for symbol in SYMBOLS:
        data = fetch_market_data(symbol)
        
        if data and 'bar' in data:
            bar = data['bar']
            tree.insert('', 'end', values=(
                symbol,
                f"${bar['o']:.2f}",
                f"${bar['h']:.2f}",
                f"${bar['l']:.2f}",
                f"${bar['c']:.2f}",
                f"{bar['v']:,}"
            ))
        else:
            tree.insert('', 'end', values=(symbol, "Error", "Error", "Error", "Error", "Error"))


# Create main window
root = tk.Tk()
root.title("Market Data Table - Solution")
root.geometry("800x400")

# Create title label
title_label = tk.Label(root, text="Real-Time Market Data", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Create frame for the table
table_frame = tk.Frame(root)
table_frame.pack(pady=10, padx=20, fill='both', expand=True)

# Create Treeview widget
columns = ("Symbol", "Open", "High", "Low", "Close", "Volume")
tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

# Define headings
for col in columns:
    tree.heading(col, text=col)

# Define column widths
tree.column("Symbol", width=100, anchor='center')
tree.column("Open", width=100, anchor='center')
tree.column("High", width=100, anchor='center')
tree.column("Low", width=100, anchor='center')
tree.column("Close", width=100, anchor='center')
tree.column("Volume", width=150, anchor='center')

# Add scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# Pack widgets
tree.pack(side='left', fill='both', expand=True)
scrollbar.pack(side='right', fill='y')

# Create refresh button
refresh_button = tk.Button(root, text="Refresh Data", command=update_table, 
                          font=("Arial", 12), bg="#4CAF50", fg="white")
refresh_button.pack(pady=10)

# Load initial data
update_table()

# Start the GUI event loop
root.mainloop()

