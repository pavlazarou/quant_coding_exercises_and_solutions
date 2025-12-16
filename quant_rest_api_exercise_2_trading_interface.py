"""
REST API Exercise 2: Trading Interface
"""

import requests
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
import os

# API Configuration
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets/v2"


def place_order(symbol, qty, side):
    """Place a market order through Alpaca API."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }
    
    order_data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": "market",
        "time_in_force": "day"
    }
    
    url = f"{BASE_URL}/orders"
    
    try:
        response = requests.post(url, json=order_data, headers=headers)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def handle_buy():
    """Handle the buy button click event."""
    symbol = symbol_entry.get().strip().upper()
    qty_str = qty_entry.get().strip()
    
    # Validate inputs
    if not symbol:
        messagebox.showerror("Error", "Please enter a stock symbol")
        return
    
    try:
        qty = int(qty_str)
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be a positive number")
            return
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a valid integer")
        return
    
    # Place the order
    status_label.config(text=f"Placing BUY order for {qty} {symbol}...", fg="blue")
    root.update()
    
    result = place_order(symbol, qty, "buy")
    
    if result:
        messagebox.showinfo("Success", 
                           f"BUY order placed successfully!\n\n"
                           f"Symbol: {result['symbol']}\n"
                           f"Quantity: {result['qty']}\n"
                           f"Status: {result['status']}\n"
                           f"Order ID: {result['id']}")
        status_label.config(text="Order placed successfully", fg="green")
        symbol_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Failed to place order. Check your API keys and try again.")
        status_label.config(text="Order failed", fg="red")


def handle_sell():
    """Handle the sell button click event."""
    symbol = symbol_entry.get().strip().upper()
    qty_str = qty_entry.get().strip()
    
    # Validate inputs
    if not symbol:
        messagebox.showerror("Error", "Please enter a stock symbol")
        return
    
    try:
        qty = int(qty_str)
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be a positive number")
            return
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a valid integer")
        return
    
    # Place the order
    status_label.config(text=f"Placing SELL order for {qty} {symbol}...", fg="blue")
    root.update()
    
    result = place_order(symbol, qty, "sell")
    
    if result:
        messagebox.showinfo("Success", 
                           f"SELL order placed successfully!\n\n"
                           f"Symbol: {result['symbol']}\n"
                           f"Quantity: {result['qty']}\n"
                           f"Status: {result['status']}\n"
                           f"Order ID: {result['id']}")
        status_label.config(text="Order placed successfully", fg="green")
        symbol_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Failed to place order. Check your API keys and try again.")
        status_label.config(text="Order failed", fg="red")


# Create main window
root = tk.Tk()
root.title("Trading Interface - Solution")
root.geometry("400x350")

# Create title label
title_label = tk.Label(root, text="Place Market Orders", font=("Arial", 16, "bold"))
title_label.pack(pady=20)

# Create input frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

# Symbol input
symbol_label = tk.Label(input_frame, text="Symbol:", font=("Arial", 12))
symbol_label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

symbol_entry = tk.Entry(input_frame, width=20, font=("Arial", 12))
symbol_entry.grid(row=0, column=1, padx=10, pady=10)

# Quantity input
qty_label = tk.Label(input_frame, text="Quantity:", font=("Arial", 12))
qty_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')

qty_entry = tk.Entry(input_frame, width=20, font=("Arial", 12))
qty_entry.grid(row=1, column=1, padx=10, pady=10)

# Create button frame
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# Buy button
buy_button = tk.Button(button_frame, text="BUY", command=handle_buy,
                       font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
                       width=10, height=2)
buy_button.grid(row=0, column=0, padx=10)

# Sell button
sell_button = tk.Button(button_frame, text="SELL", command=handle_sell,
                        font=("Arial", 14, "bold"), bg="#f44336", fg="white",
                        width=10, height=2)
sell_button.grid(row=0, column=1, padx=10)

# Create status label
status_label = tk.Label(root, text="Ready to trade", font=("Arial", 10), fg="gray")
status_label.pack(pady=10)

# Start the GUI event loop
root.mainloop()

