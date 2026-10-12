# src/banking.py
import logging
from datetime import date
from typing import ClassVar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# Custom exception for insufficient funds
class InsufficientFundsError(Exception):
    def __init__(self, message: str, amount: float) -> None:
        self.amount = amount
        super().__init__(message)


# BankAccount class
class BankAccount:
    _USD_VALUE: ClassVar[dict[str, float]] = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27}
    _SAVINGS_MINIMUM_USD = 100.0

    # BankAccount constructor
    def __init__(
        self,
        account_number: str,
        currency: str = "USD",
        account_type: str = "checking",
        balance: float = 0.0,
    ) -> None:
        self.__account_number = account_number
        self.__currency = currency
        self._account_type = account_type
        self.balance = balance

    # Account number property
    @property
    def account_number(self) -> str:
        return self.__account_number

    @property
    def currency(self) -> str:
        return self.__currency

    @property
    def account_type(self) -> str:
        return self._account_type

    # Balance property
    @property
    def balance(self) -> float:
        return self.__balance

    # Balance setter
    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            logger.error(
                "Rejected negative balance %.2f for %s",
                value,
                self.__account_number,
            )
            raise ValueError("Balance cannot be negative")
        self.__balance = value

    # Validate amount method
    @staticmethod
    def validate_amount(amount: float) -> None:
        if amount < 0:
            raise ValueError("Amount cannot be negative")

    # Validate account number method
    @staticmethod
    def is_valid_account_number(account_number: str) -> bool:
        return account_number.isdigit() and len(account_number) == 10

    # Validate non-negative amount method
    def _validate_non_negative(self, amount: float) -> None:
        if amount < 0:
            logger.error(
                "Rejected negative amount %.2f for %s",
                amount,
                self.account_number,
            )
            self.validate_amount(amount)

    # Minimum balance method
    def _minimum_balance(self) -> float:
        if self._account_type != "savings":
            return 0.0
        usd_value = self._USD_VALUE[self.currency]
        return self._SAVINGS_MINIMUM_USD / usd_value

    # Open with deposit method
    @classmethod
    def open_with_deposit(cls, account_number: str, amount: float) -> "BankAccount":
        account = cls(account_number)
        account.deposit(amount)
        return account

    # Create savings method
    @classmethod
    def create_savings(
        cls,
        account_number: str,
        currency: str = "USD",
        account_type: str = "savings",
        balance: float = 0.0,
    ) -> "BankAccount":
        minimum = cls._SAVINGS_MINIMUM_USD / cls._USD_VALUE[currency]
        if balance < minimum:
            logger.error(
                "Rejected savings opening balance %.2f for %s. Minimum: %.2f",
                balance,
                account_number,
                minimum,
            )
            raise ValueError("Savings balance cannot be below the minimum")
        return cls(account_number, currency, account_type, balance)

    # Deposit method
    def deposit(self, amount: float) -> float:
        self._validate_non_negative(amount)
        self.balance += amount
        logger.info(
            "Deposited %.2f into %s. Balance: %.2f",
            amount,
            self.account_number,
            self.balance,
        )
        return self.balance

    # Withdraw method
    def withdraw(self, amount: float) -> float:
        self._validate_non_negative(amount)
        if self.balance - amount < self._minimum_balance():
            logger.error(
                "Withdrawal of %.2f rejected for %s. Balance: %.2f",
                amount,
                self.account_number,
                self.balance,
            )
            raise InsufficientFundsError("Insufficient funds", amount)
        self.balance -= amount
        logger.info(
            "Withdrew %.2f from %s. Balance: %.2f",
            amount,
            self.account_number,
            self.balance,
        )
        return self.balance

    # Convert currency method
    def convert_currency(self, target_currency: str, exchange_rate: float) -> None:
        if exchange_rate <= 0:
            logger.error(
                "Rejected exchange rate %.2f for %s",
                exchange_rate,
                self.account_number,
            )
            raise ValueError("Exchange rate must be positive")
        converted = self.balance * exchange_rate
        logger.info(
            "Converted %.2f %s to %.2f %s",
            self.balance,
            self.currency,
            converted,
            target_currency,
        )
        return converted


# Customer class
class Customer:
    user_count = 0

    # Customer constructor
    def __init__(self, name: str, birth_date: date) -> None:
        if not Customer._is_adult(birth_date):
            logger.error("Rejected customer %s: under 18", name)
            raise ValueError("Customer must be at least 18 years old")
        self.__name = name
        self._user_id = Customer._next_user_id()
        self.__accounts: list[BankAccount] = []

    # Is adult method
    @staticmethod
    def _is_adult(birth_date: date) -> bool:
        today = date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )
        return age >= 18

    # Next user count method
    @staticmethod
    def _next_user_id() -> int:
        Customer.user_count += 1
        return Customer.user_count

    # User ID property
    @property
    def user_id(self) -> int:
        return self._user_id

    # Name property
    @property
    def name(self) -> str:
        return self.__name

    # Accounts property
    @property
    def accounts(self) -> tuple[BankAccount, ...]:
        return tuple(self.__accounts)

    # Validate name method
    @staticmethod
    def is_valid_name(name: str) -> bool:
        return bool(name.strip())

    # Create customer with account method
    @classmethod
    def with_account(
        cls, name: str, birth_date: date, account: BankAccount
    ) -> "Customer":
        customer = cls(name, birth_date)
        customer.add_account(account)
        return customer

    # Add account method
    def add_account(self, account: BankAccount) -> None:
        if not self.is_valid_name(self.name):
            raise ValueError("Customer name cannot be blank")
        if not BankAccount.is_valid_account_number(account.account_number):
            logger.error(
                "Rejected account %s for customer %s",
                account.account_number,
                self.user_id,
            )
            raise ValueError("Account number must be exactly 10 digits")
        self.__accounts.append(account)
        logger.info(
            "Added account %s to customer %s",
            account.account_number,
            self.user_id,
        )

    # Get total balance method
    def get_total_balance(self) -> float:
        total = 0.0
        for account in self.__accounts:
            total += account.balance
        return total

    # Transfer method
    def transfer(
        self,
        amount: float,
        source_account: BankAccount,
        target_account: BankAccount,
    ) -> None:
        source_ok = source_account.balance - amount >= source_account._minimum_balance()
        target_ok = target_account.balance + amount >= target_account._minimum_balance()
        if (
            source_account not in self.__accounts
            or amount < 0
            or not source_ok
            or not target_ok
        ):
            logger.error(
                "Rejected transfer of %.2f from %s to %s for customer %s",
                amount,
                source_account.account_number,
                target_account.account_number,
                self.user_id,
            )
            return
        source_account.withdraw(amount)
        target_account.deposit(amount)
