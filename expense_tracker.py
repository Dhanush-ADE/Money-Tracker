import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    description TEXT
)
""")
conn.commit()
# ---------------- FUNCTIONS ----------------
def add_transaction():
    transaction_type = type_var.get()
    amount = amount_entry.get()
    category = category_var.get()
    transaction_date = date_entry.get()
    description = description_entry.get()

    if not amount or not category or not transaction_date:
        messagebox.showerror(
            "Error",
            "Please fill in Amount, Category and Date."
        )
        return

    try:
        amount = float(amount)

        if amount <= 0:
            messagebox.showerror(
                "Error",
                "Amount must be greater than 0."
            )
            return

    except ValueError:
        messagebox.showerror(
            "Error",
            "Please enter a valid amount."
        )
        return

    cursor.execute("""
    INSERT INTO transactions
    (transaction_type, amount, category, transaction_date, description)
    VALUES (?, ?, ?, ?, ?)
    """, (
        transaction_type,
        amount,
        category,
        transaction_date,
        description
    ))

    conn.commit()

    messagebox.showinfo(
        "Success",
        "Transaction added successfully!"
    )

    clear_fields()
    load_transactions()


def load_transactions():
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
    SELECT id, transaction_type, amount, category,
           transaction_date, description
    FROM transactions
    ORDER BY id DESC
    """)

    records = cursor.fetchall()

    for record in records:
        tree.insert("", tk.END, values=record)

    update_summary()


def delete_transaction():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Warning",
            "Please select a transaction."
        )
        return

    item = tree.item(selected[0])
    transaction_id = item["values"][0]

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this transaction?"
    )

    if confirm:
        cursor.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )

        conn.commit()

        load_transactions()

        messagebox.showinfo(
            "Deleted",
            "Transaction deleted successfully."
        )


def search_transactions():
    search_text = search_entry.get().strip()

    for item in tree.get_children():
        tree.delete(item)

    if search_text == "":
        load_transactions()
        return

    cursor.execute("""
    SELECT id, transaction_type, amount, category,
           transaction_date, description
    FROM transactions
    WHERE category LIKE ?
       OR description LIKE ?
       OR transaction_type LIKE ?
    ORDER BY id DESC
    """, (
        "%" + search_text + "%",
        "%" + search_text + "%",
        "%" + search_text + "%"
    ))

    records = cursor.fetchall()

    for record in records:
        tree.insert("", tk.END, values=record)


def update_summary():
    cursor.execute("""
    SELECT COALESCE(SUM(amount), 0)
    FROM transactions
    WHERE transaction_type = 'Income'
    """)

    income = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COALESCE(SUM(amount), 0)
    FROM transactions
    WHERE transaction_type = 'Expense'
    """)

    expense = cursor.fetchone()[0]

    balance = income - expense

    income_label.config(
        text=f"Income: ₹{income:.2f}"
    )

    expense_label.config(
        text=f"Expenses: ₹{expense:.2f}"
    )

    balance_label.config(
        text=f"Balance: ₹{balance:.2f}"
    )


def clear_fields():
    amount_entry.delete(0, tk.END)
    category_var.set("")
    description_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    date_entry.insert(0, str(date.today()))

    type_var.set("Expense")


def close_application():
    conn.close()
    root.destroy()


# ---------------- GUI ----------------

root = tk.Tk()

root.title("Personal Expense Tracker")
root.geometry("950x600")
root.resizable(False, False)


# Title

title_label = tk.Label(
    root,
    text="PERSONAL EXPENSE TRACKER",
    font=("Arial", 20, "bold")
)

title_label.pack(pady=15)


# ---------------- INPUT FRAME ----------------

input_frame = tk.LabelFrame(
    root,
    text="Add Transaction",
    padx=10,
    pady=10
)

input_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


# Transaction Type

tk.Label(
    input_frame,
    text="Type:"
).grid(row=0, column=0, padx=5, pady=5)

type_var = tk.StringVar(value="Expense")

type_combo = ttk.Combobox(
    input_frame,
    textvariable=type_var,
    values=["Income", "Expense"],
    state="readonly",
    width=15
)

type_combo.grid(row=0, column=1, padx=5, pady=5)


# Amount

tk.Label(
    input_frame,
    text="Amount:"
).grid(row=0, column=2, padx=5, pady=5)

amount_entry = tk.Entry(
    input_frame,
    width=18
)

amount_entry.grid(
    row=0,
    column=3,
    padx=5,
    pady=5
)


# Category

tk.Label(
    input_frame,
    text="Category:"
).grid(row=1, column=0, padx=5, pady=5)

category_var = tk.StringVar()

category_combo = ttk.Combobox(
    input_frame,
    textvariable=category_var,
    values=[
        "Food",
        "Travel",
        "Shopping",
        "Education",
        "Bills",
        "Entertainment",
        "Salary",
        "Other"
    ],
    width=15
)

category_combo.grid(
    row=1,
    column=1,
    padx=5,
    pady=5
)


# Date

tk.Label(
    input_frame,
    text="Date:"
).grid(row=1, column=2, padx=5, pady=5)

date_entry = tk.Entry(
    input_frame,
    width=18
)

date_entry.grid(
    row=1,
    column=3,
    padx=5,
    pady=5
)

date_entry.insert(
    0,
    str(date.today())
)


# Description

tk.Label(
    input_frame,
    text="Description:"
).grid(row=2, column=0, padx=5, pady=5)

description_entry = tk.Entry(
    input_frame,
    width=45
)

description_entry.grid(
    row=2,
    column=1,
    columnspan=3,
    padx=5,
    pady=5
)


# Add Button

add_button = tk.Button(
    input_frame,
    text="Add Transaction",
    command=add_transaction,
    width=18
)

add_button.grid(
    row=3,
    column=1,
    pady=10
)


# Clear Button

clear_button = tk.Button(
    input_frame,
    text="Clear",
    command=clear_fields,
    width=18
)

clear_button.grid(
    row=3,
    column=2,
    pady=10
)


# ---------------- SEARCH ----------------

search_frame = tk.Frame(root)

search_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

tk.Label(
    search_frame,
    text="Search:"
).pack(side="left")

search_entry = tk.Entry(
    search_frame,
    width=30
)

search_entry.pack(
    side="left",
    padx=10
)

search_button = tk.Button(
    search_frame,
    text="Search",
    command=search_transactions
)

search_button.pack(side="left")

show_all_button = tk.Button(
    search_frame,
    text="Show All",
    command=load_transactions
)

show_all_button.pack(
    side="left",
    padx=10
)


# ---------------- TABLE ----------------

table_frame = tk.Frame(root)

table_frame.pack(
    fill="both",
    expand=True,
    padx=20
)


columns = (
    "ID",
    "Type",
    "Amount",
    "Category",
    "Date",
    "Description"
)

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10
)


for column in columns:

    tree.heading(
        column,
        text=column
    )

    tree.column(
        column,
        width=130
    )


tree.column(
    "ID",
    width=50
)

tree.column(
    "Description",
    width=220
)


tree.pack(
    side="left",
    fill="both",
    expand=True
)


scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

scrollbar.pack(
    side="right",
    fill="y"
)

tree.configure(
    yscrollcommand=scrollbar.set
)


# ---------------- DELETE BUTTON ----------------

delete_button = tk.Button(
    root,
    text="Delete Selected Transaction",
    command=delete_transaction
)

delete_button.pack(
    pady=8
)


# ---------------- SUMMARY ----------------

summary_frame = tk.Frame(root)

summary_frame.pack(
    fill="x",
    padx=20,
    pady=10
)


income_label = tk.Label(
    summary_frame,
    text="Income: ₹0.00",
    font=("Arial", 12, "bold")
)

income_label.pack(
    side="left",
    padx=30
)


expense_label = tk.Label(
    summary_frame,
    text="Expenses: ₹0.00",
    font=("Arial", 12, "bold")
)

expense_label.pack(
    side="left",
    padx=30
)


balance_label = tk.Label(
    summary_frame,
    text="Balance: ₹0.00",
    font=("Arial", 12, "bold")
)

balance_label.pack(
    side="left",
    padx=30
)


# Load existing records

load_transactions()


# Start application

root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)

root.mainloop()

