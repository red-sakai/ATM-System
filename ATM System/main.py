'''
*****************************************************************
*                                                               *
*       THIS SYSTEM WAS MADE BY JHERED MIGUEL C. REPUBLICA      *
*       DATE STARTED: FEBRUARY 4, 2025   2:21 PM                *
*       DATE FINISHED: FEBRUARY 4, 2025  6:56 PM                *
*                                                               *
*****************************************************************
'''

import csv
import datetime
from tkinter import *
from tkinter import messagebox

window = Tk()
window.geometry("420x420")
window.title("Jhered ATM Banking")
window.config(background="#ffefa1")

icon = PhotoImage(file="logo only.png")
window.iconphoto(True, icon)

fullLogo = PhotoImage(file="insideLogo.png")

frame = Frame(window, background="#ffefa1")
frame.pack()

Label(frame, text="Welcome to Jhered's ATM Banking", font=("Arial", 17, "bold"), background="#ffefa1", image=fullLogo,
      compound="bottom").pack(pady=20)
Label(frame, text="Enter PIN", font=("Arial", 14, "bold"), background="#ffefa1").pack()

entry = Entry(frame, font=("Arial", 17), show="*", width=6)
entry.pack()

request_counter = 0  # Initialize request counter


def submit():
    global request_counter
    pin = entry.get()

    with open("database.csv", mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        accounts = [row for row in reader]
        for row in accounts:
            if row and row[0] == pin:
                account_name = row[2]
                balance = float(row[1])
                window.destroy()
                show_menu(account_name, balance, pin, accounts)
                return

    error_label.config(text="Invalid PIN. Try again.", fg="red")


def update_database(accounts):
    with open("database.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(accounts)


def generate_receipt(transaction_type, amount):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        receipt_text = f"""
********** Jhered ATM Banking **********
Transaction Type: {transaction_type}
Amount: ₱{amount:.2f}
Date & Time: {timestamp}
************************************
"""

        with open("receipt.txt", "w", encoding="utf-8") as receipt_file:  # Overwrites for a fresh receipt
            receipt_file.write(receipt_text)

        # Show receipt in a new window
        show_receipt_window(receipt_text)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate receipt: {e}")


def show_receipt_window(receipt_text):
    receipt_win = Toplevel()
    receipt_win.geometry("350x250")
    receipt_win.title("Transaction Receipt")
    receipt_win.config(background="white")

    Label(receipt_win, text="Transaction Receipt", font=("Arial", 14, "bold"), background="white").pack(pady=10)

    receipt_label = Text(receipt_win, font=("Arial", 12), background="white", wrap=WORD)
    receipt_label.insert(END, receipt_text)
    receipt_label.config(state=DISABLED)  # Make it read-only
    receipt_label.pack(pady=5, padx=10)

    Button(receipt_win, text="Close", command=receipt_win.destroy).pack(pady=10)


def show_menu(account_name, balance, pin, accounts):
    global request_counter

    def logout():
        global request_counter
        if messagebox.askyesno("Logout", f"Are you sure you want to log out?\nTotal Requests: {request_counter}"):
            menu_window.destroy()
            window.deiconify()
            request_counter = 0  # Reset counter after logout

    menu_window = Tk()
    menu_window.geometry("420x420")
    menu_window.title("ATM Menu")
    menu_window.config(background="#ffefa1")

    Label(menu_window, text=f"Welcome {account_name}", font=("Arial", 17, "bold"), background="#ffefa1").pack(pady=20)

    balance_label = Label(menu_window, text=f"Balance: ₱{balance:.2f}", font=("Arial", 14), background="#ffefa1")
    balance_label.pack()

    Button(menu_window, text="Withdraw", font=("Arial", 14), padx=20, pady=10,
           command=lambda: withdraw_window(menu_window, account_name, pin, accounts, balance_label)).pack(pady=5)
    Button(menu_window, text="Deposit", font=("Arial", 14), padx=20, pady=10,
           command=lambda: deposit_window(menu_window, account_name, pin, accounts, balance_label)).pack(pady=5)
    Button(menu_window, text="Change PIN", font=("Arial", 14), padx=20, pady=10,
           command=lambda: change_pin_window(menu_window, pin, accounts)).pack(pady=5)
    Button(menu_window, text="Logout", font=("Arial", 14), padx=20, pady=10, command=logout).pack(pady=5)


def withdraw_window(menu_window, account_name, pin, accounts, balance_label):
    global request_counter
    request_counter += 1
    withdraw_win = Toplevel(menu_window)
    withdraw_win.geometry("200x200")
    withdraw_win.title("Withdraw")
    withdraw_win.config(background="#ffefa1")

    Label(withdraw_win, text="Enter amount:", background="#ffefa1").pack()
    entry_amount = Entry(withdraw_win)
    entry_amount.pack()
    Button(withdraw_win, text="Confirm",
           command=lambda: withdraw(entry_amount, withdraw_win, pin, accounts, balance_label)).pack(pady=5)
    Button(withdraw_win, text="Cancel", command=withdraw_win.destroy).pack(pady=5)


def withdraw(entry_amount, withdraw_win, pin, accounts, balance_label):
    amount_str = entry_amount.get().strip().replace(",", "")  # Remove unnecessary spaces and commas

    if not amount_str:
        messagebox.showerror("Error", "Please enter a valid amount.")
        return

    try:
        amount = float(amount_str)  # Convert input to float
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be greater than zero.")
            return

        for row in accounts:
            if row[0] == pin:
                balance = float(row[1])
                if amount > balance:
                    messagebox.showerror("Error", "Insufficient funds!")
                    return

                row[1] = str(balance - amount)  # Update balance in accounts list
                update_database(accounts)  # Write back to CSV

                balance_label.config(text=f"Balance: ₱{float(row[1]):.2f}")  # Update UI
                generate_receipt("Withdrawal", amount)  # Generate a receipt
                withdraw_win.destroy()  # Close window
                return

    except ValueError:
        messagebox.showerror("Error", "Please enter a numeric amount.")


def deposit_window(menu_window, account_name, pin, accounts, balance_label):
    global request_counter
    request_counter += 1
    deposit_win = Toplevel(menu_window)
    deposit_win.geometry("200x200")
    deposit_win.title("Deposit")
    deposit_win.config(background="#ffefa1")

    Label(deposit_win, text="Enter amount:", background="#ffefa1").pack()
    entry_amount = Entry(deposit_win)
    entry_amount.pack()
    Button(deposit_win, text="Confirm",
           command=lambda: deposit(entry_amount, deposit_win, pin, accounts, balance_label)).pack(pady=5)
    Button(deposit_win, text="Cancel", command=deposit_win.destroy).pack(pady=5)


def deposit(entry_amount, deposit_win, pin, accounts, balance_label):
    amount_str = entry_amount.get().strip().replace(",", "")  # Remove unnecessary spaces and commas

    if not amount_str:
        messagebox.showerror("Error", "Please enter a valid amount.")
        return

    try:
        amount = float(amount_str)  # Convert input to float
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be greater than zero.")
            return

        for row in accounts:
            if row[0] == pin:
                row[1] = str(float(row[1]) + amount)  # Update balance in accounts list
                update_database(accounts)  # Write back to CSV

                balance_label.config(text=f"Balance: ₱{float(row[1]):.2f}")  # Update UI
                generate_receipt("Deposit", amount)  # Generate a receipt
                deposit_win.destroy()  # Close window
                return

    except ValueError:
        messagebox.showerror("Error", "Please enter a numeric amount.")


def change_pin_window(menu_window, pin, accounts):
    global request_counter
    request_counter += 1
    change_pin_win = Toplevel(menu_window)
    change_pin_win.geometry("200x200")
    change_pin_win.title("Change PIN")
    change_pin_win.config(background="#ffefa1")

    Label(change_pin_win, text="Enter new PIN:", background="#ffefa1").pack()
    entry_new_pin = Entry(change_pin_win)
    entry_new_pin.pack()
    Button(change_pin_win, text="Confirm",
           command=lambda: change_pin(entry_new_pin, change_pin_win, pin, accounts)).pack(pady=5)
    Button(change_pin_win, text="Cancel", command=change_pin_win.destroy).pack(pady=5)


def change_pin(entry_new_pin, change_pin_win, old_pin, accounts):
    new_pin = entry_new_pin.get()
    for row in accounts:
        if row[0] == old_pin:
            row[0] = new_pin  # Update the PIN
            update_database(accounts)
            messagebox.showinfo("Success", "PIN changed successfully!")
            change_pin_win.destroy()
            return
    messagebox.showerror("Error", "Failed to change PIN.")


error_label = Label(frame, text="", font=("Arial", 12), background="#ffefa1")
error_label.pack()

submit_button = Button(window, text="Confirm", command=submit)
submit_button.pack()

window.mainloop()