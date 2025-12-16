"""
TKinter Trader Profile Form 
Complete implementation with form fields, buttons, textarea, and event handling.
"""

import tkinter as tk
from tkinter import ttk

# Initialize main window
root = tk.Tk()
root.title("Trader Profile Registration")
root.geometry("600x500")

# Dictionary to store trader profile information
trader_profile = {}

# ============================================================================
# Function Definitions
# ============================================================================

def submit_profile():
    """
    Collects data from form fields, stores in trader_profile dictionary,
    and displays it in the textarea.
    """
    # Collect data from entry widgets
    trader_profile['Trader Name'] = name_entry.get()
    trader_profile['Trading Firm'] = firm_entry.get()
    trader_profile['Trader ID'] = trader_id_entry.get()
    trader_profile['Primary Strategy'] = strategy_entry.get()
    trader_profile['Asset Classes'] = asset_classes_entry.get()
    trader_profile['Risk Tolerance'] = risk_var.get()
    trader_profile['Years of Experience'] = experience_entry.get()
    trader_profile['Email'] = email_entry.get()
    
    # Clear the text widget
    profile_text.delete('1.0', tk.END)
    
    # Display the profile data
    profile_text.insert('1.0', "=" * 50 + "\n")
    profile_text.insert(tk.END, "REGISTERED TRADER PROFILE\n")
    profile_text.insert(tk.END, "=" * 50 + "\n\n")
    
    # Loop through dictionary and display each key-value pair
    for key, value in trader_profile.items():
        profile_text.insert(tk.END, f"{key}: {value}\n")
    
    profile_text.insert(tk.END, "\n" + "=" * 50 + "\n")
    profile_text.insert(tk.END, "Profile successfully registered!\n")


def clear_profile():
    """
    Clears all form fields and the textarea.
    """
    # Clear all entry widgets
    name_entry.delete(0, tk.END)
    firm_entry.delete(0, tk.END)
    trader_id_entry.delete(0, tk.END)
    strategy_entry.delete(0, tk.END)
    asset_classes_entry.delete(0, tk.END)
    risk_var.set("")  # Clear radio button selection
    experience_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    
    # Clear the text widget
    profile_text.delete('1.0', tk.END)
    
    # Clear the dictionary
    trader_profile.clear()


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

# Form frame (top section)
form_frame = ttk.LabelFrame(main_frame, text="Trader Profile Information", padding="15")
form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
form_frame.columnconfigure(1, weight=1)

# Button frame (middle section)
button_frame = ttk.Frame(main_frame, padding="10")
button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

# Display frame (bottom section)
display_frame = ttk.LabelFrame(main_frame, text="Registered Trader Profile", padding="15")
display_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
display_frame.columnconfigure(0, weight=1)
display_frame.rowconfigure(0, weight=1)
main_frame.rowconfigure(2, weight=1)

# ============================================================================
# Form Fields
# ============================================================================

# Row 0: Trader Name
ttk.Label(form_frame, text="Trader Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
name_entry = ttk.Entry(form_frame, width=40)
name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

# Row 1: Trading Firm
ttk.Label(form_frame, text="Trading Firm:").grid(row=1, column=0, sticky=tk.W, pady=5)
firm_entry = ttk.Entry(form_frame, width=40)
firm_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

# Row 2: Trader ID
ttk.Label(form_frame, text="Trader ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
trader_id_entry = ttk.Entry(form_frame, width=40)
trader_id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

# Row 3: Primary Strategy
ttk.Label(form_frame, text="Primary Strategy:").grid(row=3, column=0, sticky=tk.W, pady=5)
strategy_entry = ttk.Entry(form_frame, width=40)
strategy_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
ttk.Label(form_frame, text="(e.g., Momentum, Mean Reversion, Arbitrage)", 
          font=('TkDefaultFont', 8)).grid(row=3, column=2, sticky=tk.W, padx=5)

# Row 4: Asset Classes
ttk.Label(form_frame, text="Asset Classes:").grid(row=4, column=0, sticky=tk.W, pady=5)
asset_classes_entry = ttk.Entry(form_frame, width=40)
asset_classes_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
ttk.Label(form_frame, text="(e.g., Equities, Options, Futures)", 
          font=('TkDefaultFont', 8)).grid(row=4, column=2, sticky=tk.W, padx=5)

# Row 5: Risk Tolerance (Radio buttons)
ttk.Label(form_frame, text="Risk Tolerance:").grid(row=5, column=0, sticky=tk.W, pady=5)
risk_frame = ttk.Frame(form_frame)
risk_frame.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
risk_var = tk.StringVar()
ttk.Radiobutton(risk_frame, text="Conservative", variable=risk_var, value="Conservative").pack(side=tk.LEFT, padx=5)
ttk.Radiobutton(risk_frame, text="Moderate", variable=risk_var, value="Moderate").pack(side=tk.LEFT, padx=5)
ttk.Radiobutton(risk_frame, text="Aggressive", variable=risk_var, value="Aggressive").pack(side=tk.LEFT, padx=5)

# Row 6: Years of Experience
ttk.Label(form_frame, text="Years of Experience:").grid(row=6, column=0, sticky=tk.W, pady=5)
experience_entry = ttk.Entry(form_frame, width=40)
experience_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

# Row 7: Email
ttk.Label(form_frame, text="Email:").grid(row=7, column=0, sticky=tk.W, pady=5)
email_entry = ttk.Entry(form_frame, width=40)
email_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

# ============================================================================
# Buttons
# ============================================================================

register_btn = ttk.Button(button_frame, text="Register Profile", command=submit_profile)
register_btn.pack(side=tk.LEFT, padx=5)

clear_btn = ttk.Button(button_frame, text="Clear Form", command=clear_profile)
clear_btn.pack(side=tk.LEFT, padx=5)

# ============================================================================
# Textarea with Scrollbar
# ============================================================================

profile_text = tk.Text(display_frame, height=15, width=50, wrap=tk.WORD)
scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=profile_text.yview)
profile_text.configure(yscrollcommand=scrollbar.set)
profile_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

# ============================================================================
# Run the application
# ============================================================================
root.mainloop()

