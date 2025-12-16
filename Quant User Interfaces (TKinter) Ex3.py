"""
TKinter Market Watchlist Monitor
Complete implementation with symbol management, simulated price updates, and Treeview display.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random

# Initialize main window
root = tk.Tk()
root.title("Market Watchlist Monitor")
root.geometry("800x550")

# List to store watchlist symbols
watchlist = []

# Dictionary to store symbol data
market_data = {}

# Variable to track if updates are running
update_running = False
update_job = None

# ============================================================================
# Function Definitions
# ============================================================================

def add_symbol():
    """
    Adds a new symbol to the watchlist with initial random price.
    """
    symbol = symbol_entry.get().upper().strip()
    
    # Validate input
    if not symbol:
        messagebox.showwarning("Input Error", "Please enter a symbol!")
        return
    
    # Check if symbol already exists
    if symbol in watchlist:
        messagebox.showwarning("Duplicate Symbol", f"{symbol} is already in the watchlist!")
        return
    
    # Generate random initial price between 50 and 500
    initial_price = round(random.uniform(50, 500), 2)
    
    # Add to watchlist and market_data
    watchlist.append(symbol)
    market_data[symbol] = {
        'price': initial_price,
        'prev_price': initial_price,
        'change': 0.00,
        'change_pct': 0.00
    }
    
    # Update display
    refresh_display()
    
    # Clear entry
    symbol_entry.delete(0, tk.END)
    symbol_entry.focus()


def remove_symbol():
    """
    Removes the selected symbol from the watchlist.
    """
    # Get selected item
    selected = watchlist_tree.selection()
    
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a symbol to remove!")
        return
    
    # Get the symbol from the selected row
    item = watchlist_tree.item(selected[0])
    symbol = item['values'][0]
    
    # Remove from watchlist and market_data
    watchlist.remove(symbol)
    del market_data[symbol]
    
    # Update display
    refresh_display()


def update_prices():
    """
    Simulates price updates by randomly changing prices (±0.5% to ±2%).
    Schedules itself to run again after 2 seconds.
    """
    global update_job
    
    if not update_running:
        return
    
    # Update each symbol's price
    for symbol in watchlist:
        data = market_data[symbol]
        
        # Store previous price
        data['prev_price'] = data['price']
        
        # Generate random price change between -2% and +2%
        change_pct = random.uniform(-2.0, 2.0)
        change_amount = data['price'] * (change_pct / 100)
        
        # Update price
        new_price = data['price'] + change_amount
        data['price'] = round(max(new_price, 0.01), 2)  # Ensure price stays positive
        
        # Calculate change from previous price
        data['change'] = round(data['price'] - data['prev_price'], 2)
        data['change_pct'] = round((data['change'] / data['prev_price'] * 100), 2) if data['prev_price'] > 0 else 0
    
    # Refresh display
    refresh_display()
    
    # Schedule next update in 2000ms (2 seconds)
    update_job = root.after(2000, update_prices)


def start_updates():
    """
    Starts the price update simulation.
    """
    global update_running
    
    if not watchlist:
        messagebox.showinfo("No Symbols", "Add symbols to the watchlist first!")
        return
    
    if update_running:
        messagebox.showinfo("Already Running", "Price updates are already running!")
        return
    
    update_running = True
    start_btn.config(state='disabled')
    stop_btn.config(state='normal')
    update_prices()


def stop_updates():
    """
    Stops the price update simulation.
    """
    global update_running, update_job
    
    update_running = False
    start_btn.config(state='normal')
    stop_btn.config(state='disabled')
    
    # Cancel scheduled update
    if update_job:
        root.after_cancel(update_job)
        update_job = None


def refresh_display():
    """
    Refreshes the Treeview display with current market data.
    Applies color coding: green for gains, red for losses.
    """
    # Clear existing items
    for item in watchlist_tree.get_children():
        watchlist_tree.delete(item)
    
    # Insert each symbol with current data
    for symbol in watchlist:
        data = market_data[symbol]
        
        # Format values
        price_str = f"${data['price']:.2f}"
        change_str = f"${data['change']:+.2f}"  # + sign for positive
        change_pct_str = f"{data['change_pct']:+.2f}%"
        
        # Determine tag for color coding
        tag = 'gain' if data['change'] > 0 else 'loss' if data['change'] < 0 else 'neutral'
        
        # Insert into treeview
        watchlist_tree.insert('', tk.END, values=(symbol, price_str, change_str, change_pct_str), 
                            tags=(tag,))


def clear_watchlist():
    """
    Clears the entire watchlist.
    """
    if not watchlist:
        messagebox.showinfo("Empty Watchlist", "Watchlist is already empty!")
        return
    
    result = messagebox.askyesno("Clear Watchlist", 
                                 "Are you sure you want to clear the entire watchlist?")
    if result:
        # Stop updates if running
        if update_running:
            stop_updates()
        
        # Clear data structures
        watchlist.clear()
        market_data.clear()
        
        # Clear display
        for item in watchlist_tree.get_children():
            watchlist_tree.delete(item)


def sort_by_column(col):
    """
    Sorts the treeview by the clicked column.
    """
    # Get current items
    items = [(watchlist_tree.set(item, col), item) for item in watchlist_tree.get_children('')]
    
    # Sort items
    items.sort(reverse=False)
    
    # Rearrange items in sorted positions
    for index, (val, item) in enumerate(items):
        watchlist_tree.move(item, '', index)


# ============================================================================
# Frame Setup
# ============================================================================

# Main container frame
main_frame = ttk.Frame(root, padding="20")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Configure grid weights for responsive layout
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)

# Control frame (top section)
control_frame = ttk.LabelFrame(main_frame, text="Watchlist Controls", padding="15")
control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))

# Button frame (middle section)
button_frame = ttk.Frame(main_frame, padding="10")
button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

# Display frame (bottom section)
display_frame = ttk.LabelFrame(main_frame, text="Market Data - Live Updates", padding="15")
display_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
display_frame.columnconfigure(0, weight=1)
display_frame.rowconfigure(0, weight=1)
main_frame.rowconfigure(2, weight=1)

# ============================================================================
# Input Field
# ============================================================================

ttk.Label(control_frame, text="Symbol:").pack(side=tk.LEFT, padx=5)
symbol_entry = ttk.Entry(control_frame, width=15)
symbol_entry.pack(side=tk.LEFT, padx=5)
ttk.Label(control_frame, text="(e.g., AAPL, TSLA, MSFT, GOOGL, NVDA)", 
          font=('TkDefaultFont', 9, 'italic')).pack(side=tk.LEFT, padx=5)

# Bind Enter key to add symbol
symbol_entry.bind('<Return>', lambda e: add_symbol())

# ============================================================================
# Buttons
# ============================================================================

add_btn = ttk.Button(button_frame, text="Add Symbol", command=add_symbol)
add_btn.pack(side=tk.LEFT, padx=5)

remove_btn = ttk.Button(button_frame, text="Remove Selected", command=remove_symbol)
remove_btn.pack(side=tk.LEFT, padx=5)

start_btn = ttk.Button(button_frame, text="Start Updates", command=start_updates)
start_btn.pack(side=tk.LEFT, padx=5)

stop_btn = ttk.Button(button_frame, text="Stop Updates", command=stop_updates, state='disabled')
stop_btn.pack(side=tk.LEFT, padx=5)

clear_btn = ttk.Button(button_frame, text="Clear Watchlist", command=clear_watchlist)
clear_btn.pack(side=tk.LEFT, padx=5)

# ============================================================================
# Treeview Display
# ============================================================================

# Define columns
columns = ("Symbol", "Price", "Change", "Change %")
watchlist_tree = ttk.Treeview(display_frame, columns=columns, show="headings", height=20)

# Define column headings and widths
watchlist_tree.heading("Symbol", text="Symbol")
watchlist_tree.heading("Price", text="Price")
watchlist_tree.heading("Change", text="Change ($)")
watchlist_tree.heading("Change %", text="Change %")

watchlist_tree.column("Symbol", width=150, anchor='center')
watchlist_tree.column("Price", width=150, anchor='center')
watchlist_tree.column("Change", width=150, anchor='center')
watchlist_tree.column("Change %", width=150, anchor='center')

# Configure tags for color coding
watchlist_tree.tag_configure('gain', foreground='green')
watchlist_tree.tag_configure('loss', foreground='red')
watchlist_tree.tag_configure('neutral', foreground='black')

# Add scrollbar
scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=watchlist_tree.yview)
watchlist_tree.configure(yscrollcommand=scrollbar.set)

# Grid layout
watchlist_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

# Bind double-click to remove symbol
watchlist_tree.bind('<Double-1>', lambda e: remove_symbol())

# Bind Delete key to remove symbol
root.bind('<Delete>', lambda e: remove_symbol())

# ============================================================================
# Cleanup on window close
# ============================================================================

def on_closing():
    """
    Handles cleanup when window is closed.
    """
    global update_running, update_job
    
    # Stop updates
    update_running = False
    if update_job:
        root.after_cancel(update_job)
    
    # Close window
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# ============================================================================
# Run the application
# ============================================================================
root.mainloop()

