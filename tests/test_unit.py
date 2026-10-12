# tests/test_unit.py
import sys
from datetime import date
from pathlib import Path

import pytest

# Import the banking module
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from banking import BankAccount, Customer, InsufficientFundsError


# Define the reset_user_count fixture
@pytest.fixture(autouse=True)
def reset_user_count():
    Customer.user_count = 0
    yield
    Customer.user_count = 0


# Define the adult_birth_date function
def adult_birth_date() -> date:
    today = date.today()
    return date(today.year - 30, 1, 1)


# Define the minor_birth_date function
def minor_birth_date() -> date:
    today = date.today()
    return date(today.year - 10, 1, 1)


# Define the test_account_defaults_and_getters function
def test_account_defaults_and_getters():
    account = BankAccount("1234567890")
    assert account.account_number == "1234567890"
    assert account.currency == "USD"
    assert account.account_type == "checking"
    assert account.balance == 0.0


# Define the test_negative_opening_balance_is_rejected function
def test_negative_opening_balance_is_rejected():
    with pytest.raises(ValueError, match="Balance cannot be negative"):
        BankAccount("1234567890", balance=-1)


# Define the test_balance_setter_rejects_negative_value function
def test_balance_setter_rejects_negative_value():
    account = BankAccount("1234567890", balance=25)
    with pytest.raises(ValueError, match="Balance cannot be negative"):
        account.balance = -5
    assert account.balance == 25


# Define the test_is_valid_account_number function
def test_is_valid_account_number():
    assert BankAccount.is_valid_account_number("1234567890")
    assert not BankAccount.is_valid_account_number("123456789")
    assert not BankAccount.is_valid_account_number("123456789a")


# Define the test_deposit_and_withdraw function
def test_deposit_and_withdraw():
    account = BankAccount("1234567890", balance=100)
    assert account.deposit(25) == 125
    assert account.withdraw(40) == 85


# Define the test_negative_deposit_and_withdrawal_are_rejected function
def test_negative_deposit_and_withdrawal_are_rejected():
    account = BankAccount("1234567890", balance=100)
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        account.deposit(-1)
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        account.withdraw(-1)
    assert account.balance == 100


# Define the test_withdraw_more_than_balance_raises_insufficient_funds function
def test_withdraw_more_than_balance_raises_insufficient_funds():
    account = BankAccount("1234567890", balance=40)
    with pytest.raises(InsufficientFundsError) as exc_info:
        account.withdraw(50)
    assert exc_info.value.amount == 50
    assert account.balance == 40


# Define the test_savings_withdrawal_cannot_pass_usd_floor function
def test_savings_withdrawal_cannot_pass_usd_floor():
    account = BankAccount.create_savings("1234567890", balance=150)
    assert account.withdraw(40) == 110
    with pytest.raises(InsufficientFundsError):
        account.withdraw(20)
    assert account.balance == 110


# Define the test_savings_floor_uses_currency_equivalent function
def test_savings_floor_uses_currency_equivalent():
    minimum = BankAccount._SAVINGS_MINIMUM_USD / BankAccount._USD_VALUE["EUR"]
    account = BankAccount.create_savings("1234567890", "EUR", balance=minimum)
    with pytest.raises(InsufficientFundsError):
        account.withdraw(0.01)
    assert account.balance == pytest.approx(minimum)


# Define the test_create_savings_rejects_opening_balance_below_minimum function
def test_create_savings_rejects_opening_balance_below_minimum():
    with pytest.raises(ValueError, match="Savings balance cannot be below the minimum"):
        BankAccount.create_savings("1234567890", balance=99)


# Define the test_open_with_deposit function
def test_open_with_deposit():
    account = BankAccount.open_with_deposit("1234567890", 80)
    assert account.balance == 80


# Define the test_convert_currency_returns_converted_amount_without_changing_balance function
def test_convert_currency_returns_converted_amount_without_changing_balance():
    account = BankAccount("1234567890", balance=100)
    assert account.convert_currency("EUR", 0.92) == pytest.approx(92)
    assert account.balance == 100
    assert account.currency == "USD"


# Define the test_convert_currency_rejects_non_positive_rate function
def test_convert_currency_rejects_non_positive_rate():
    account = BankAccount("1234567890", balance=100)
    with pytest.raises(ValueError, match="Exchange rate must be positive"):
        account.convert_currency("EUR", 0)
    assert account.balance == 100


# Define the test_customer_must_be_18_and_ids_are_consecutive function
def test_customer_must_be_18_and_ids_are_consecutive():
    today = date.today()
    try:
        exactly_18 = today.replace(year=today.year - 18)
    except ValueError:
        exactly_18 = today.replace(year=today.year - 18, day=28)
    first = Customer("Ada", adult_birth_date())
    second = Customer("Bea", exactly_18)
    assert (first.user_id, second.user_id) == (1, 2)
    assert first.accounts == ()
    with pytest.raises(ValueError, match="at least 18"):
        Customer("Cara", minor_birth_date())
    assert Customer.user_count == 2


# Define the test_add_account_and_total_balance function
def test_add_account_and_total_balance():
    customer = Customer("Ada", adult_birth_date())
    customer.add_account(BankAccount("1234567890", balance=100))
    customer.add_account(BankAccount("1234567891", balance=40))
    assert customer.get_total_balance() == 140
    with pytest.raises(ValueError, match="10 digits"):
        customer.add_account(BankAccount("123", balance=10))
    assert len(customer.accounts) == 2


# Define the test_with_account function
def test_with_account():
    account = BankAccount("1234567890", balance=20)
    customer = Customer.with_account("Ada", adult_birth_date(), account)
    assert customer.accounts[0] is account


# Define the test_transfer_moves_funds_when_rules_allow function
def test_transfer_moves_funds_when_rules_allow():
    customer = Customer("Ada", adult_birth_date())
    checking = BankAccount("1234567890", balance=50)
    savings = BankAccount.create_savings("1234567891", balance=150)
    customer.add_account(checking)
    customer.add_account(savings)
    customer.transfer(30, checking, savings)
    assert (checking.balance, savings.balance) == (20, 180)


# Define the test_transfer_rejects_savings_floor_and_unknown_source function
def test_transfer_rejects_savings_floor_and_unknown_source():
    customer = Customer("Ada", adult_birth_date())
    checking = BankAccount("1234567890", balance=20)
    savings = BankAccount.create_savings("1234567891", balance=180)
    customer.add_account(checking)
    customer.add_account(savings)
    customer.transfer(90, savings, checking)
    outsider = BankAccount("1234567892", balance=10)
    customer.transfer(5, outsider, checking)
    assert (checking.balance, savings.balance) == (20, 180)


# Define the test_transfer_rejects_insufficient_funds function
def test_transfer_rejects_insufficient_funds():
    customer = Customer("Ada", adult_birth_date())
    checking = BankAccount("1234567890", balance=20)
    savings = BankAccount.create_savings("1234567891", balance=180)
    customer.add_account(checking)
    customer.add_account(savings)
    customer.transfer(200, checking, savings)
    assert (checking.balance, savings.balance) == (20, 180)
