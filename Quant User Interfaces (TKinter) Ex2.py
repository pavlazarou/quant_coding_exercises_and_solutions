"""
TKinter Portfolio Position Tracker
Complete implementation with position entry, calculations, and portfolio display.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Initialize main window
root = tk.Tk()
root.title("Portfolio Position Tracker")
root.geometry("750x600")

# Dictionary to store portfolio positions
portfolio = {}

# ============================================================================
# Function Definitions
# ============================================================================

def add_position():
    """
    Adds a new position to the portfolio with calculated metrics.
    Validates input and calculates: total_cost, current_value, P&L, P&L%
    """
    try:
        # Get values from entry widgets
        symbol = symbol_entry.get().upper().strip()
        quantity = float(quantity_entry.get())
        entry_price = float(entry_price_entry.get())
        current_price = float(current_price_entry.get())
        
        # Validate inputs
        if not symbol:
            messagebox.showwarning("Input Error", "Please enter a symbol!")
            return
        
        if quantity <= 0 or entry_price <= 0 or current_price <= 0:
            messagebox.showwarning("Input Error", "All values must be positive!")
            return
        
        # Calculate metrics
        total_cost = quantity * entry_price
        current_value = quantity * current_price
        pnl = current_value - total_cost
        pnl_pct = (pnl / total_cost) * 100 if total_cost > 0 else 0
        
        # Store in portfolio dictionary
        portfolio[symbol] = {
            'quantity': quantity,
            'entry_price': entry_price,
            'current_price': current_price,
            'total_cost': total_cost,
            'current_value': current_value,
            'pnl': pnl,
            'pnl_pct': pnl_pct
        }
        
        # Update display
        update_display()
        
        # Clear entry fields
        symbol_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
        entry_price_entry.delete(0, tk.END)
        current_price_entry.delete(0, tk.END)
        
        # Focus back to symbol entry
        symbol_entry.focus()
        
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values!")


def update_display():
    """
    Updates the portfolio display with all positions and calculated metrics.
    """
    # Clear the text widget
    portfolio_text.delete('1.0', tk.END)
    
    if not portfolio:
        portfolio_text.insert('1.0', "No positions in portfolio. Add a position to get started!")
        return
    
    # Header
    portfolio_text.insert('1.0', "=" * 95 + "\n")
    portfolio_text.insert(tk.END, "PORTFOLIO POSITIONS\n")
    portfolio_text.insert(tk.END, "=" * 95 + "\n\n")
    
    # Column headers
    header = f"{'Symbol':<10} {'Qty':<10} {'Entry $':<12} {'Current $':<12} {'Cost':<15} {'Value':<15} {'P&L':<15} {'P&L %':<10}\n"
    portfolio_text.insert(tk.END, header)
    portfolio_text.insert(tk.END, "-" * 95 + "\n")
    
    # Display each position
    for symbol, data in portfolio.items():
        line = f"{symbol:<10} "
        line += f"{data['quantity']:<10.2f} "
        line += f"${data['entry_price']:<11.2f} "
        line += f"${data['current_price']:<11.2f} "
        line += f"${data['total_cost']:<14.2f} "
        line += f"${data['current_value']:<14.2f} "
        line += f"${data['pnl']:<14.2f} "
        line += f"{data['pnl_pct']:<9.2f}%\n"
        portfolio_text.insert(tk.END, line)
    
    portfolio_text.insert(tk.END, "\n")


def calculate_portfolio_metrics():
    """
    Calculates and displays total portfolio metrics.
    """
    if not portfolio:
        messagebox.showinfo("Portfolio Metrics", "No positions in portfolio!")
        return
    
    # Calculate totals
    total_invested = sum(pos['total_cost'] for pos in portfolio.values())
    total_current_value = sum(pos['current_value'] for pos in portfolio.values())
    total_pnl = total_current_value - total_invested
    portfolio_return = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    # Display metrics
    portfolio_text.insert(tk.END, "=" * 95 + "\n")
    portfolio_text.insert(tk.END, "PORTFOLIO SUMMARY\n")
    portfolio_text.insert(tk.END, "=" * 95 + "\n")
    portfolio_text.insert(tk.END, f"Total Invested:        ${total_invested:,.2f}\n")
    portfolio_text.insert(tk.END, f"Total Current Value:   ${total_current_value:,.2f}\n")
    portfolio_text.insert(tk.END, f"Total P&L:             ${total_pnl:,.2f}\n")
    portfolio_text.insert(tk.END, f"Portfolio Return:      {portfolio_return:.2f}%\n")
    portfolio_text.insert(tk.END, f"Number of Positions:   {len(portfolio)}\n")
    portfolio_text.insert(tk.END, "=" * 95 + "\n")


def clear_portfolio():
    """
    Clears all positions from the portfolio.
    """
    if portfolio:
        result = messagebox.askyesno("Clear Portfolio", 
                                     "Are you sure you want to clear all positions?")
        if result:
            portfolio.clear()
            portfolio_text.delete('1.0', tk.END)
            portfolio_text.insert('1.0', "Portfolio cleared.")
    else:
        messagebox.showinfo("Clear Portfolio", "Portfolio is already empty!")


def remove_position():
    """
    Removes a specific position by symbol.
    """
    symbol = symbol_entry.get().upper().strip()
    if symbol in portfolio:
        del portfolio[symbol]
        update_display()
        symbol_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Position {symbol} removed!")
    else:
        messagebox.showwarning("Not Found", f"Position {symbol} not found in portfolio!")


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

# Position entry frame (top section)
entry_frame = ttk.LabelFrame(main_frame, text="Add New Position", padding="15")
entry_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
entry_frame.columnconfigure(1, weight=1)
entry_frame.columnconfigure(3, weight=1)

# Action buttons frame (middle section)
button_frame = ttk.Frame(main_frame, padding="10")
button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

# Portfolio display frame (bottom section)
display_frame = ttk.LabelFrame(main_frame, text="Portfolio Positions", padding="15")
display_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
display_frame.columnconfigure(0, weight=1)
display_frame.rowconfigure(0, weight=1)
main_frame.rowconfigure(2, weight=1)

# ============================================================================
# Form Fields (2x2 grid layout)
# ============================================================================

# Row 0, Column 0-1: Symbol
ttk.Label(entry_frame, text="Symbol:").grid(row=0, column=0, sticky=tk.W, pady=5)
symbol_entry = ttk.Entry(entry_frame, width=15)
symbol_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

# Row 0, Column 2-3: Quantity
ttk.Label(entry_frame, text="Quantity:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
quantity_entry = ttk.Entry(entry_frame, width=15)
quantity_entry.grid(row=0, column=3, sticky=tk.W, pady=5, padx=5)

# Row 1, Column 0-1: Entry Price
ttk.Label(entry_frame, text="Entry Price:").grid(row=1, column=0, sticky=tk.W, pady=5)
entry_price_entry = ttk.Entry(entry_frame, width=15)
entry_price_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

# Row 1, Column 2-3: Current Price
ttk.Label(entry_frame, text="Current Price:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20, 0))
current_price_entry = ttk.Entry(entry_frame, width=15)
current_price_entry.grid(row=1, column=3, sticky=tk.W, pady=5, padx=5)

# ============================================================================
# Buttons
# ============================================================================

add_btn = ttk.Button(button_frame, text="Add Position", command=add_position)
add_btn.pack(side=tk.LEFT, padx=5)

remove_btn = ttk.Button(button_frame, text="Remove Position", command=remove_position)
remove_btn.pack(side=tk.LEFT, padx=5)

calc_btn = ttk.Button(button_frame, text="Calculate Metrics", command=calculate_portfolio_metrics)
calc_btn.pack(side=tk.LEFT, padx=5)

clear_btn = ttk.Button(button_frame, text="Clear Portfolio", command=clear_portfolio)
clear_btn.pack(side=tk.LEFT, padx=5)

# ============================================================================
# Textarea with Scrollbar
# ============================================================================

portfolio_text = tk.Text(display_frame, height=20, width=80, wrap=tk.NONE, font=('Courier', 10))
scrollbar_y = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=portfolio_text.yview)
scrollbar_x = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=portfolio_text.xview)
portfolio_text.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

portfolio_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

# Initial message
portfolio_text.insert('1.0', "Welcome to Portfolio Position Tracker!\n\nAdd positions using the form above.")

# ============================================================================
# Run the application
# ============================================================================
root.mainloop()

