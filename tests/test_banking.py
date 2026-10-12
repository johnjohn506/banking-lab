# tests/test_banking.py
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Import the banking module
from banking import BankAccount, Customer, InsufficientFundsError

# Initialize the customers list
customers: list[Customer] = []


# Define the find_customer function
def find_customer(user_id: int) -> Customer:
    for customer in customers:
        if customer.user_id == user_id:
            return customer
    raise ValueError(f"No customer with user id {user_id}")


# Define the find_account function
def find_account(customer: Customer, account_number: str) -> BankAccount:
    for account in customer.accounts:
        if account.account_number == account_number:
            return account
    raise ValueError(f"No account {account_number} for customer {customer.user_id}")


# Define the menu function
def menu() -> None:
    options = """
1. Add customer
2. Add bank account
3. Deposit
4. Withdraw
5. Convert currency
6. Transfer
7. Exit
"""
    while True:
        print(options)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                name = input("Name: ").strip()
                birth_date = date.fromisoformat(input("Birth date (YYYY-MM-DD): "))
                customers.append(Customer(name, birth_date))
                print(f"Added customer {customers[-1].user_id}")
            elif choice == "2":
                customer = find_customer(int(input("User id: ")))
                account_number = input("Account number: ").strip()
                currency = input("Currency [USD]: ").strip() or "USD"
                account_type = input("Account type [checking]: ").strip() or "checking"
                balance = float(input("Opening balance: "))
                if account_type == "savings":
                    account = BankAccount.create_savings(
                        account_number, currency, account_type, balance
                    )
                else:
                    account = BankAccount(
                        account_number, currency, account_type, balance
                    )
                customer.add_account(account)
                print(f"Added account {account.account_number}")
            elif choice == "3":
                customer = find_customer(int(input("User id: ")))
                account = find_account(customer, input("Account number: ").strip())
                print(account.deposit(float(input("Amount: "))))
            elif choice == "4":
                customer = find_customer(int(input("User id: ")))
                account = find_account(customer, input("Account number: ").strip())
                print(account.withdraw(float(input("Amount: "))))
            elif choice == "5":
                customer = find_customer(int(input("User id: ")))
                account = find_account(customer, input("Account number: ").strip())
                account.convert_currency(
                    input("Target currency: ").strip(),
                    float(input("Exchange rate: ")),
                )
            elif choice == "6":
                customer = find_customer(int(input("User id: ")))
                source = find_account(customer, input("Source account: ").strip())
                target = find_account(customer, input("Target account: ").strip())
                customer.transfer(float(input("Amount: ")), source, target)
            elif choice == "7":
                break
            else:
                print("Unknown option")
        except (ValueError, InsufficientFundsError) as error:
            print(error)


# Define the test_menu function
if __name__ == "__main__":
    menu()
