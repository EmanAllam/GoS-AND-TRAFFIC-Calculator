import tkinter as tk
from tkinter import ttk
import math

def erlang_b(N, A):
    if N == 0:
        return 1.0  # If no servers, all calls are blocked
    numerator = (A ** N) / math.factorial(N)
    denominator = sum([(A ** i) / math.factorial(i) for i in range(N+1)])
    return numerator / denominator

def binomial(N, M, A):
    GoS = sum(math.comb(M - 1, i) * (A**i) * ((1 - A)**(M - 1 - i)) for i in range(N, M))
    return GoS

def erlang_c(N, A):
    if N == 0:
        return 0.0 # If no servers, no delay
    numerator = ((A ** N) * N) / (math.factorial(N) * (N - A))
    denominator = sum([(A ** i) / math.factorial(i) for i in range(N)])
    denominator += ((A ** N) * N) / (math.factorial(N) * (N - A))
    return numerator / denominator
    
def calculate_A(gos, N, type, tolerance=1e-10, max_iterations=10000):
    A_low = 0  # Lower bound for A
    A_high = N  # Upper bound, assuming maximum A can't be more than number of channels initially
    A_guess = (A_high + A_low) / 2  # Initial guess for A

    for _ in range(max_iterations):
        if type == 'Erlang B':
            calculated_gos = erlang_b(N, A_guess)
        elif type == 'Erlang C':
            calculated_gos = erlang_c(N, A_guess)
        
        # Check if the calculated GoS is close enough to the desired GoS
        if abs(calculated_gos - gos) < tolerance:
            return A_guess
        
        # Adjust the guess for A based on whether we need more or less traffic intensity
        if calculated_gos > gos:
            A_high = A_guess
        else:
            A_low = A_guess
        
        A_guess = (A_high + A_low) / 2

    # Return the last guess if the loop finishes without reaching the tolerance
    return A_guess

def calc_gos():
    try:
        
        N = int(N_entry.get())
        K = int(K_entry.get())
        lambdaa = float(lambda_entry.get())
        H = float(H_entry.get())

        A = lambdaa * H * K
        
        # Convert A to CCS if chosen by the user
        if unit_var.get() == 'CCS':
            A *= 3600 

        if method_var_gos.get() == 'Erlang B':
            GoS = erlang_b(N, A)
        elif method_var_gos.get() == 'Binomial':
            p = lambdaa * H
            GoS = binomial(N, K, p)
        else: # Erlang C
            GoS = erlang_c(N, A)

        # Update the output fields
        traffic_intensity_var.set(f'{A:.2f} {unit_var.get()}')
        GoS_var.set(f'{GoS:.2%}')

    except ValueError:
        traffic_intensity_var.set("Invalid input")
        GoS_var.set("Invalid input")
    ##################
    
def compare_gos_methods():
    lambdaa = 5  # calls/hour
    H = 3 / 60  # hours
    K_values = range(5, 51, 5)  # from 5 to 50 with step of 5
    N_values = range(1, 11)  # from 1 to 10
    
    # Create a new window to display the comparison results
    comparison_window = tk.Toplevel(app)
    comparison_window.title("GoS Comparison Results")

    # Create Treeview with columns for N, K, and GoS results for each method
    columns = ["N", "K", "Erlang B", "Binomial", "Erlang C"]
    comparison_tree = ttk.Treeview(comparison_window, columns=columns, show="headings")
    for col in columns:
        comparison_tree.heading(col, text=col)
        comparison_tree.column(col, anchor="center")
    comparison_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    # Populate the Treeview with GoS results for each combination of N and K
    for K in K_values:
        A = lambdaa * H * K
        for N in N_values:
            GoS_erlang_b = erlang_b(N, A)
            p = lambdaa * H
            GoS_binomial = binomial(N, K, p)
            GoS_erlang_c = erlang_c(N, A)
            comparison_tree.insert("", tk.END, values=(N, K, f"{GoS_erlang_b:.2%}", f"{GoS_binomial:.2%}", f"{GoS_erlang_c:.2%}"))

        
def calc_A():
    try:
        N = int(N_entry_A.get())
        GoS = float(GoS_entry.get()) / 100
        A = calculate_A(GoS, N, type = method_var_A.get())
        traffic_intensity_var.set(f'{A:.4f} Erlang')
    except ValueError:
        traffic_intensity_var.set("Invalid input")

def calculate_and_display_results():
    # Define GoS values
    gos_values = [0.005, 0.01, 0.02, 0.03, 0.05]
    N_values = range(1, 11)
    
    # Create a new window to display the results
    results_window = tk.Toplevel(app)
    results_window.title("Batch Calculation Results")

    # Creating columns dynamically based on GoS values
    columns = ["N/B"] + [f"{gos*100:.2f}%" for gos in gos_values]
    columns_for_erlang_b = [col for col in columns]
    columns_for_erlang_c = [col for col in columns if col != "N/B"]
    
    # Title for Erlang B Table
    ttk.Label(results_window, text="Erlang B Results", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # Set up the Treeview for Erlang B
    results_tree_b = ttk.Treeview(results_window, columns=columns_for_erlang_b, show="headings")
    for col in columns_for_erlang_b:
        results_tree_b.heading(col, text=col)
    results_tree_b.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    
    # Title for Erlang C Table
    ttk.Label(results_window, text="Erlang C Results", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10, sticky="w")

    # Set up the Treeview for Erlang C
    results_tree_c = ttk.Treeview(results_window, columns=["N"] + columns_for_erlang_c, show="headings")
    results_tree_c.heading("N", text="N/B")
    for col in columns_for_erlang_c:
        results_tree_c.heading(col, text=col)
    results_tree_c.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)

    # Populate Treeviews with results
    for N in N_values:
        row_b = [N]
        row_c = [N]
        for gos in gos_values:
            A_erlang_b = calculate_A(gos, N, 'Erlang B')
            A_erlang_c = calculate_A(gos, N, 'Erlang C')
            row_b.append(f"{A_erlang_b:.4f}")
            row_c.append(f"{A_erlang_c:.4f}")
        results_tree_b.insert("", tk.END, values=row_b)
        results_tree_c.insert("", tk.END, values=row_c)

    # Adjust Treeview columns
    for col in columns_for_erlang_b:
        results_tree_b.column(col, anchor="center")
    for col in ["N"] + columns_for_erlang_c:
        results_tree_c.column(col, anchor="center")

#------------------------------------------------------------------------------------------------
# Enhanced GUI design
def enhanced_style():
    style = ttk.Style()
    style.configure("TLabel", font=("Arial", 12), background="light grey", foreground="black")
    style.configure("TEntry", font=("Arial", 12), foreground="blue")
    style.configure("TButton", font=("Arial", 12), background="grey", foreground="black")
    style.configure("TFrame", background="light grey")

    # You can also set specific styles for widgets or create custom ones
    style.configure("Header.TLabel", font=("Arial", 14, "bold"), foreground="black")

app = tk.Tk()
app.title("Combined Calculator")
enhanced_style()

# Variables
traffic_intensity_var = tk.StringVar()
method_var_A = tk.StringVar(value='Erlang B')
method_var_gos = tk.StringVar(value='Erlang B')
GoS_var = tk.StringVar()
unit_var = tk.StringVar(value='Erlang')

def setup_gos_calculator_frame(parent_frame):

    # Setup GUI elements for the GoS Calculator inside the parent frame
    ttk.Label(parent_frame, text="GoS Calculator", style="Header.TLabel").grid(column=0, row=0, pady=10, columnspan=2)    # Inputs
    ttk.Label(parent_frame, text="Number of Trunks (N):").grid(column=0, row=1)
    global N_entry_gos
    N_entry_gos = ttk.Entry(parent_frame)
    N_entry_gos.grid(column=1, row=1)

    ttk.Label(parent_frame, text="Number of Users (K):").grid(column=0, row=2)
    global K_entry
    K_entry = ttk.Entry(parent_frame)
    K_entry.grid(column=1, row=2)

    ttk.Label(parent_frame, text="Average Call Rate (λ):").grid(column=0, row=3)
    global lambda_entry
    lambda_entry = ttk.Entry(parent_frame)
    lambda_entry.grid(column=1, row=3)

    ttk.Label(parent_frame, text="Call Holding Time (H):").grid(column=0, row=4)
    global H_entry
    H_entry = ttk.Entry(parent_frame)
    H_entry.grid(column=1, row=4)

    # Select GoS Method 
    ttk.Label(parent_frame, text="GoS Calculation Method:").grid(column=0, row=5)
    method_options = ['Erlang B', 'Binomial', 'Erlang C']
    method_menu = ttk.OptionMenu(parent_frame, method_var_gos, method_options[0], *method_options)
    method_menu.grid(column=1, row=5)
    
    # Select Unit
    ttk.Label(parent_frame, text="Traffic Intensity Unit:").grid(column=0, row=6)
    unit_options = ['Erlang', 'CCS']
    unit_menu = ttk.OptionMenu(parent_frame, unit_var, unit_options[0], *unit_options)
    unit_menu.grid(column=1, row=6)

    # Calculate Button
    calculate_btn_gos= ttk.Button(parent_frame, text="Calculate GoS", command=calc_gos)
    calculate_btn_gos.grid(column=0, row=7, columnspan=2)
    
    # Add button for comparing GoS methods here
    compare_gos_btn = ttk.Button(parent_frame, text="Compare GoS Methods", command=compare_gos_methods)
    compare_gos_btn.grid(column=0, row=9, columnspan=2, pady=10)
    
    # Outputs
    ttk.Label(parent_frame, text="Grade of Service (GoS):").grid(column=0, row=8)
    ttk.Label(parent_frame, textvariable=GoS_var).grid(column=1, row=8)


def setup_traffic_calculator_frame(parent_frame):
    # Setup GUI elements for the Traffic Calculator inside the parent frame
    ttk.Label(parent_frame, text="Traffic Intensity Calculator", style="Header.TLabel").grid(column=0, row=0, pady=10, columnspan=2)    # Inputs
    # Inputs
    ttk.Label(parent_frame, text="Number of Trunks (N):").grid(column=0, row=1)
    global N_entry_A
    N_entry_A = ttk.Entry(parent_frame)
    N_entry_A.grid(column=1, row=1)
    
    # Select GoS Method 
    ttk.Label(parent_frame, text="GoS Calculation Method:").grid(column=0, row=2)
    method_options = ['Erlang B', 'Erlang C']
    method_menu = ttk.OptionMenu(parent_frame, method_var_A, method_options[0], *method_options)
    method_menu.grid(column=1, row=2)
    
    # Add GoS Input
    ttk.Label(parent_frame, text="Grade of Service (GoS):").grid(column=0, row=3)
    global GoS_entry
    GoS_entry = ttk.Entry(parent_frame)
    GoS_entry.grid(column=1, row=3)
    
    # Calculate Button
    calculate_btn_gos= ttk.Button(parent_frame, text="Calculate Traffic Intenisty (A)", command=calc_A)
    calculate_btn_gos.grid(column=0, row=4, columnspan=2)
    
    # Outputs
    ttk.Label(parent_frame, text="Traffic Intensity (A):").grid(column=0, row=5)
    ttk.Label(parent_frame, textvariable=traffic_intensity_var).grid(column=1, row=5)

    
    # Add a button to your GUI to trigger this function
    calculate_results_btn = ttk.Button(parent_frame, text="Calculate and Display Tables", command=calculate_and_display_results)
    calculate_results_btn.grid(column=0, row=6, columnspan=2, pady=5)
    
# Create frames
traffic_frame = tk.Frame(app, borderwidth=2, relief="groove")
gos_frame = tk.Frame(app, borderwidth=2, relief="groove")

# Layout frames vertically
traffic_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
gos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Setup each calculator within its frame
setup_traffic_calculator_frame(traffic_frame)
setup_gos_calculator_frame(gos_frame)

app.mainloop()

